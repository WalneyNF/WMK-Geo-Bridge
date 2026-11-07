"""Administração local de credenciais. Nunca publique a chave retornada."""
import argparse
import json
import security

parser = argparse.ArgumentParser(description="WMK Security Center - administração local")
sub = parser.add_subparsers(dest="command", required=True)
new = sub.add_parser("create", help="Cria chave de acesso")
new.add_argument("--name", required=True)
new.add_argument("--scopes", required=True, help="Ex.: gps:read,gps:write")
new.add_argument("--devices", help="IDs autorizados separados por vírgula; omitir = todos")
new.add_argument("--days", type=int, default=30)
rev = sub.add_parser("revoke", help="Revoga uma chave pelo ID")
rev.add_argument("id")
sub.add_parser("list", help="Lista metadados SEM revelar segredos")
sub.add_parser("audit", help="Mostra as 30 últimas ações")
args = parser.parse_args()

if args.command == "create":
    devices = args.devices.split(",") if args.devices else None
    result = security.create_key(args.name, args.scopes.split(","), devices, args.days)
    print("ATENÇÃO: copie agora; esta chave não será mostrada novamente.")
    print(json.dumps(result, indent=2))
elif args.command == "revoke":
    print("Revogada" if security.revoke(args.id) else "ID não encontrado")
elif args.command == "list":
    with security.connect() as con:
        for row in con.execute("SELECT id,label,scopes,devices,expires,revoked FROM keys ORDER BY created DESC"):
            print(json.dumps(dict(zip(["id","label","scopes","devices","expires","revoked"],row)),ensure_ascii=False))
elif args.command == "audit":
    with security.connect() as con:
        for row in con.execute("SELECT at,key_id,action,outcome,resource FROM audit ORDER BY id DESC LIMIT 30"):
            print(json.dumps(dict(zip(["at","key_id","action","outcome","resource"],row)),ensure_ascii=False))
