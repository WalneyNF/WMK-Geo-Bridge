"""WMK Geo Bridge - API HTTP local, sem dependências externas.
Copyright (c) 2026 Walney Moreira Klein.
"""
import base64
import hmac
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

VERSION = "0.1.0"
HOST = "127.0.0.1"
PORT = int(os.getenv("WMK_BRIDGE_PORT", "8766"))
TRACCAR_URL = os.getenv("WMK_TRACCAR_URL", "http://127.0.0.1:8082").rstrip("/")
TRACCAR_TOKEN = os.getenv("WMK_TRACCAR_TOKEN", "")
TRACCAR_USER = os.getenv("WMK_TRACCAR_USER", "")
TRACCAR_PASSWORD = os.getenv("WMK_TRACCAR_PASSWORD", "")
API_KEY = os.getenv("WMK_BRIDGE_API_KEY", "")
ALLOWED_ORIGINS = {"http://127.0.0.1:4173", "http://localhost:4173"}
MAX_BODY = 16384
DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"

def now():
    return datetime.now(timezone.utc).isoformat()

def normalize(device, position=None, simulated=None, source="traccar"):
    p = None
    if position:
        lat, lon = float(position["latitude"]), float(position["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Coordenadas fora dos limites")
        p = {"latitude": lat, "longitude": lon,
             "speedKmh": round(float(position.get("speed", 0)) * 1.852, 2),
             "heading": position.get("course"), "timestamp": position.get("fixTime"),
             "valid": position.get("valid")}
    return {"id": str(device["id"]), "deviceId": device["id"],
            "name": device.get("name", "Dispositivo"), "source": source,
            "simulated": simulated, "position": p}

def traccar_get(path):
    if not (TRACCAR_URL.startswith("http://127.0.0.1:") or TRACCAR_URL.startswith("http://localhost:")):
        raise ValueError("Nesta versão, o Traccar deve ser local")
    if TRACCAR_TOKEN:
        auth = "Bearer " + TRACCAR_TOKEN
    elif TRACCAR_USER and TRACCAR_PASSWORD:
        auth = "Basic " + base64.b64encode((TRACCAR_USER + ":" + TRACCAR_PASSWORD).encode()).decode()
    else:
        raise PermissionError("Configure as credenciais do Traccar")
    with urlopen(Request(TRACCAR_URL + "/api/" + path,
                         headers={"Authorization": auth, "Accept": "application/json"}), timeout=6) as response:
        return json.load(response)

def vehicles():
    devices = traccar_get("devices")
    positions = {p["deviceId"]: p for p in traccar_get("positions")}
    return [normalize(d, positions.get(d["id"])) for d in devices]

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, obj):
        body = json.dumps(obj, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlsplit(self.path).path
        static = {
            "/docs": ("swagger.html", "text/html; charset=utf-8"),
            "/docs/": ("swagger.html", "text/html; charset=utf-8"),
            "/docs/manual": ("endpoints.html", "text/html; charset=utf-8"),
            "/openapi.json": ("openapi.json", "application/json; charset=utf-8"),
        }
        if route in static:
            filename, content_type = static[route]
            try:
                raw = (DOCS_DIR / filename).read_bytes()
            except OSError:
                return self.send_json(404, {"error": "documentation_not_found"})
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)
            return
        if route == "/health":
            return self.send_json(200, {"status": "ok", "service": "wmk-geo-bridge", "version": VERSION})
        if route == "/api/v1/capabilities":
            return self.send_json(200, {"schemaVersion": "1.0", "sources": ["traccar"],
                                        "traccarConfigured": bool(TRACCAR_TOKEN or (TRACCAR_USER and TRACCAR_PASSWORD)),
                                        "writeEnabled": bool(API_KEY)})
        if route == "/api/v1/vehicles":
            try:
                items = vehicles()
                return self.send_json(200, {"schemaVersion": "1.0", "source": "traccar",
                                            "items": items, "count": len(items), "timestamp": now()})
            except PermissionError:
                return self.send_json(503, {"error": "traccar_auth_not_configured"})
            except (HTTPError, URLError, ValueError, KeyError, TypeError):
                return self.send_json(502, {"error": "traccar_unavailable_or_invalid_response"})
        return self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/v1/positions":
            return self.send_json(404, {"error": "not_found"})
        if not API_KEY:
            return self.send_json(403, {"error": "write_disabled"})
        if not hmac.compare_digest(self.headers.get("X-WMK-API-Key", ""), API_KEY):
            return self.send_json(401, {"error": "unauthorized"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= MAX_BODY:
                return self.send_json(413, {"error": "invalid_size"})
            p = json.loads(self.rfile.read(length))
            if not isinstance(p, dict) or not isinstance(p.get("id"), str) or not 1 <= len(p["id"]) <= 128:
                return self.send_json(400, {"error": "invalid_device"})
            lat, lon = float(p["latitude"]), float(p["longitude"])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return self.send_json(400, {"error": "invalid_coordinates"})
            # Somente confirma recebimento; persistência é responsabilidade de um adaptador futuro.
            return self.send_json(202, {"accepted": True, "persisted": False, "id": p["id"], "timestamp": now()})
        except (ValueError, TypeError, KeyError):
            return self.send_json(400, {"error": "invalid_json"})

    def do_OPTIONS(self):
        self.send_response(204)
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-WMK-API-Key")
        self.end_headers()

def main():
    print(f"WMK Geo Bridge {VERSION} - http://{HOST}:{PORT}/health", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

if __name__ == "__main__":
    main()
