"""Servidor WMK protegido, separado do Bridge legado para migração controlada.
Execute: python src/protected_bridge.py (porta 8772, somente loopback).
"""
import json
import os
import threading
import time
from collections import defaultdict, deque
from http.server import ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import bridge
import security

HOST = "127.0.0.1"
PORT = int(os.getenv("WMK_SECURE_PORT", "8772"))
RATE_LIMIT = int(os.getenv("WMK_RATE_LIMIT", "60"))
WINDOW = 60
hits = defaultdict(deque)
lock = threading.Lock()


class ProtectedHandler(bridge.Handler):
    def log_message(self, fmt, *args):
        # Nunca registrar cabeçalhos de autorização.
        super().log_message(fmt, *args)

    def identity(self, scope, device=None):
        raw = self.headers.get("Authorization", "")
        if not raw.startswith("Bearer "):
            security.audit(None, scope, "missing_token", device or "")
            self.send_json(401, {"error": "authentication_required"})
            return None
        token = raw[7:]
        user = security.authorize(token, scope, device)
        if not user:
            security.audit(None, scope, "denied", device or "")
            self.send_json(403, {"error": "access_denied"})
            return None
        now = time.monotonic()
        with lock:
            q = hits[user["id"]]
            while q and q[0] < now-WINDOW:
                q.popleft()
            if len(q) >= RATE_LIMIT:
                security.audit(user["id"], scope, "rate_limited", device or "")
                self.send_json(429, {"error": "rate_limited"})
                return None
            q.append(now)
        return user

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == "/health":
            return self.send_json(200, {"status": "ok", "service": "wmk-secure-bridge"})
        if route == "/api/v1/capabilities":
            return self.send_json(200, {"schemaVersion": "1.0", "authentication": "bearer", "readProtected": True})
        if route == "/api/v1/vehicles":
            user = self.identity("gps:read")
            if not user:
                return
            try:
                items = bridge.vehicles()
                if user["devices"] is not None:
                    allowed = set(user["devices"])
                    items = [x for x in items if str(x["id"]) in allowed or str(x.get("deviceId")) in allowed]
                security.audit(user["id"], "gps:read", "allowed", "vehicles")
                return self.send_json(200, {"schemaVersion": "1.0", "source": "traccar", "items": items, "count": len(items), "timestamp": bridge.now()})
            except PermissionError:
                return self.send_json(503, {"error": "traccar_auth_not_configured"})
            except Exception:
                return self.send_json(502, {"error": "upstream_unavailable"})
        return self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        route = urlsplit(self.path).path
        if route != "/api/v1/positions":
            return self.send_json(404, {"error": "not_found"})
        user = self.identity("gps:write")
        if not user:
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= bridge.MAX_BODY:
                return self.send_json(413, {"error": "invalid_size"})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict) or not isinstance(data.get("id"), str) or not 1 <= len(data["id"]) <= 128:
                return self.send_json(400, {"error": "invalid_device"})
            if user["devices"] is not None and data["id"] not in user["devices"]:
                security.audit(user["id"], "gps:write", "device_denied", data["id"])
                return self.send_json(403, {"error": "device_access_denied"})
            lat, lon = data.get("latitude"), data.get("longitude")
            if type(lat) not in (float, int) or type(lon) not in (float, int):
                return self.send_json(400, {"error": "invalid_coordinates"})
            import math
            if not math.isfinite(lat) or not math.isfinite(lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return self.send_json(400, {"error": "invalid_coordinates"})
            security.audit(user["id"], "gps:write", "allowed", data["id"])
            # O Bridge original não persiste: não afirmar que posição foi armazenada.
            return self.send_json(202, {"accepted": True, "persisted": False, "id": data["id"], "timestamp": bridge.now()})
        except (ValueError, TypeError, UnicodeError):
            return self.send_json(400, {"error": "invalid_json"})

    def do_OPTIONS(self):
        # CORS fechado por padrão: aplicativos backend podem usar HTTP diretamente.
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()


if __name__ == "__main__":
    print(f"WMK Secure Bridge http://{HOST}:{PORT}/health", flush=True)
    ThreadingHTTPServer((HOST, PORT), ProtectedHandler).serve_forever()
