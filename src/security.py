"""WMK Geo Bridge: chaves com hash, escopos, expiração, revogação e auditoria.
Biblioteca padrão Python. A base SQLite é privada e nunca deve ir ao Git.
"""
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import threading
import time
from datetime import datetime, timezone

LOCK = threading.RLock()
DB = os.getenv("WMK_SECURITY_DB", os.path.join(os.path.dirname(__file__), "..", "data", "security.sqlite3"))
SCOPES = {"gps:read", "gps:write", "gps:history", "devices:manage", "admin"}


@contextmanager
def connect():
    os.makedirs(os.path.dirname(os.path.abspath(DB)), exist_ok=True)
    con = sqlite3.connect(DB, timeout=10)
    con.execute("PRAGMA busy_timeout=10000")
    con.execute("CREATE TABLE IF NOT EXISTS keys (id TEXT PRIMARY KEY, label TEXT NOT NULL, digest TEXT NOT NULL UNIQUE, scopes TEXT NOT NULL, devices TEXT NOT NULL, expires INTEGER, revoked INTEGER NOT NULL DEFAULT 0, created INTEGER NOT NULL)")
    con.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, at INTEGER NOT NULL, key_id TEXT, action TEXT NOT NULL, outcome TEXT NOT NULL, resource TEXT)")
    con.commit()
    try:
        yield con
        con.commit()
    finally:
        con.close()


def fingerprint(key):
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def create_key(label, scopes, devices=None, ttl_days=30):
    if not label or not isinstance(label, str) or len(label)>100:
        raise ValueError("invalid_label")
    scopes = set(scopes)
    if not scopes or not scopes <= SCOPES:
        raise ValueError("invalid_scopes")
    if devices is not None and (not isinstance(devices,list) or not devices or not all(isinstance(x,str) and x and len(x)<=128 for x in devices)):
        raise ValueError("invalid_devices")
    if ttl_days is not None and (not isinstance(ttl_days,int) or not 1<=ttl_days<=365):
        raise ValueError("invalid_ttl")
    kid = secrets.token_hex(8)
    raw = "wmk_" + secrets.token_urlsafe(32)
    expiry = int(time.time())+ttl_days*86400 if ttl_days else None
    with LOCK, connect() as con:
        con.execute("INSERT INTO keys VALUES (?,?,?,?,?,?,0,?)",
                    (kid,label,fingerprint(raw),json.dumps(sorted(scopes)),json.dumps(devices),expiry,int(time.time())))
    return {"id":kid,"key":raw,"expires":expiry}


def revoke(kid):
    with LOCK, connect() as con:
        cur=con.execute("UPDATE keys SET revoked=1 WHERE id=?",(kid,))
        return cur.rowcount>0


def audit(kid, action, outcome, resource=""):
    with LOCK, connect() as con:
        con.execute("INSERT INTO audit(at,key_id,action,outcome,resource) VALUES (?,?,?,?,?)",
                    (int(time.time()),kid,action,outcome,str(resource)[:128]))


def authorize(raw, scope, device=None):
    # Sem chave, nunca autoriza; digest em tempo constante para chave existente.
    if not isinstance(raw,str) or not raw.startswith("wmk_") or len(raw)>256:
        return None
    with LOCK, connect() as con:
        row=con.execute("SELECT id,digest,scopes,devices,expires,revoked FROM keys WHERE digest=?",(fingerprint(raw),)).fetchone()
    if not row or not hmac.compare_digest(row[1],fingerprint(raw)):
        return None
    kid,digest,scopes,devices,expiry,revoked=row
    if revoked or (expiry is not None and int(time.time())>=expiry):
        return None
    permissions=set(json.loads(scopes))
    if scope not in permissions and "admin" not in permissions:
        return None
    allowed=json.loads(devices)
    if device is not None and allowed is not None and str(device) not in allowed:
        return None
    return {"id":kid,"scopes":permissions,"devices":allowed}
