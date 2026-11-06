import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bridge import normalize

class TestBridge(unittest.TestCase):
    def test_device_without_position(self):
        result = normalize({"id": 5, "name": "Teste"})
        self.assertEqual(result["deviceId"], 5)
        self.assertIsNone(result["position"])
    def test_speed_conversion(self):
        result = normalize({"id": 1}, {"latitude": -22.28, "longitude": -42.53,
                         "speed": 10, "course": 90, "fixTime": "2026-11-06T12:00:00Z"})
        self.assertEqual(result["position"]["speedKmh"], 18.52)
    def test_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            normalize({"id": 1}, {"latitude": 100, "longitude": 0})
    def test_unknown_simulation(self):
        self.assertIsNone(normalize({"id": 1})["simulated"])

if __name__ == "__main__":
    unittest.main()
