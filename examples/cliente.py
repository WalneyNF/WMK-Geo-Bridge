"""Cliente Python WMK Geo Bridge. Exemplo de diagnóstico sem dependências."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

BASE = os.getenv("WMK_BRIDGE_URL", "http://127.0.0.1:8766")
for endpoint in ("/health", "/api/v1/capabilities", "/api/v1/vehicles"):
    try:
        with urlopen(BASE + endpoint, timeout=5) as response:
            status, data = response.status, json.load(response)
    except HTTPError as exc:
        status = exc.code
        data = json.loads(exc.read().decode("utf-8"))
    except URLError as exc:
        print(endpoint, "Falha de conexão:", exc.reason)
        continue
    print(endpoint, "HTTP", status)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    if status == 503:
        print("Traccar ainda não configurado: resultado esperado no laboratório.")
