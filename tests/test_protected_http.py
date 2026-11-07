"""Teste HTTP real com porta efêmera e SQLite isolado."""
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import security
import protected_bridge

class ProtectedHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.old=security.DB
        security.DB=os.path.join(cls.tmp.name,"keys.sqlite3")
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),protected_bridge.ProtectedHandler)
        cls.port=cls.server.server_address[1]
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.reader=security.create_key("read",["gps:read"],["CAR-01"])["key"]
        cls.writer=security.create_key("write",["gps:write"],["CAR-01"])["key"]
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=3)
        security.DB=cls.old;cls.tmp.cleanup()
    def request(self,path,token=None,payload=None):
        headers={"Content-Type":"application/json"}
        if token:headers["Authorization"]="Bearer "+token
        data=json.dumps(payload).encode() if payload is not None else None
        req=Request(f"http://127.0.0.1:{self.port}{path}",headers=headers,data=data,method="POST" if data else "GET")
        try:
            with urlopen(req,timeout=4) as r:return r.status,json.load(r)
        except HTTPError as e:return e.code,json.load(e)
    def test_health(self):
        self.assertEqual(self.request("/health")[0],200)
    def test_read_requires_key(self):
        self.assertEqual(self.request("/api/v1/vehicles")[0],401)
    def test_read_denies_write_only(self):
        self.assertEqual(self.request("/api/v1/vehicles",self.writer)[0],403)
    def test_write_requires_key(self):
        self.assertEqual(self.request("/api/v1/positions",payload={"id":"CAR-01","latitude":1,"longitude":2})[0],401)
    def test_write_restricts_device(self):
        self.assertEqual(self.request("/api/v1/positions",self.writer,{"id":"CAR-02","latitude":1,"longitude":2})[0],403)
    def test_write_accepts_without_persisting(self):
        status,result=self.request("/api/v1/positions",self.writer,{"id":"CAR-01","latitude":1,"longitude":2})
        self.assertEqual(status,202);self.assertFalse(result["persisted"])
    def test_write_invalid_coordinates(self):
        self.assertEqual(self.request("/api/v1/positions",self.writer,{"id":"CAR-01","latitude":100,"longitude":2})[0],400)
if __name__=="__main__":unittest.main()
