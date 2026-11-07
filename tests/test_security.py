"""Testes de autorização com banco temporário, sem alterar dados reais."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import security

class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old=security.DB
        security.DB=os.path.join(self.tmp.name,"test.sqlite3")
    def tearDown(self):
        security.DB=self.old
        self.tmp.cleanup()
    def test_missing_or_wrong_key(self):
        self.assertIsNone(security.authorize("","gps:read"))
        self.assertIsNone(security.authorize("wmk_wrong","gps:read"))
    def test_scopes_and_device_ownership(self):
        key=security.create_key("app",["gps:read"],["CAR-01"])["key"]
        self.assertIsNotNone(security.authorize(key,"gps:read","CAR-01"))
        self.assertIsNone(security.authorize(key,"gps:read","CAR-02"))
        self.assertIsNone(security.authorize(key,"gps:write"))
    def test_revoke(self):
        k=security.create_key("app",["gps:write"])
        self.assertTrue(security.revoke(k["id"]))
        self.assertIsNone(security.authorize(k["key"],"gps:write"))
    def test_expiry(self):
        k=security.create_key("app",["gps:read"])
        with security.connect() as con:
            con.execute("UPDATE keys SET expires=1 WHERE id=?",(k["id"],))
        self.assertIsNone(security.authorize(k["key"],"gps:read"))
    def test_invalid_scopes(self):
        with self.assertRaises(ValueError):
            security.create_key("app",["root:everything"])
    def test_audit_no_raw_key(self):
        k=security.create_key("app",["gps:read"])
        security.audit(k["id"],"gps:read","allowed","CAR-01")
        with security.connect() as con:
            row=con.execute("SELECT key_id,action,outcome FROM audit").fetchone()
        self.assertEqual(row,(k["id"],"gps:read","allowed"))
        self.assertNotIn(k["key"],str(row))
if __name__=="__main__":unittest.main()
