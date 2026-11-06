"""Exemplo de cliente independente. Executar com a ponte iniciada."""
import json
from urllib.request import urlopen
BASE = "http://127.0.0.1:8766"
for endpoint in ("/health", "/api/v1/capabilities", "/api/v1/vehicles"):
    with urlopen(BASE + endpoint, timeout=5) as response:
        print(endpoint, response.status)
        print(json.dumps(json.load(response), indent=2, ensure_ascii=False))
