"""Exemplo de POST experimental: NÃO persiste posições. Requer chave local."""
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError
base = os.getenv("WMK_BRIDGE_URL", "http://127.0.0.1:8766")
key = os.getenv("WMK_BRIDGE_API_KEY", "")
if not key:
    raise SystemExit("Configure WMK_BRIDGE_API_KEY para habilitar a escrita.")
payload = {"id": "veiculo-demo-001", "latitude": -22.28, "longitude": -42.53}
request = Request(base + "/api/v1/positions", method="POST",
    headers={"Content-Type": "application/json", "X-WMK-API-Key": key},
    data=json.dumps(payload).encode("utf-8"))
try:
    with urlopen(request, timeout=5) as response:
        print(response.status, response.read().decode())
except HTTPError as exc:
    print(exc.code, exc.read().decode())
