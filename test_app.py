import os
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer

# app.py reads these at import time; no real AWS call is made in these tests
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-central-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("TOPIC_ARN", "arn:aws:sns:eu-central-1:123456789012:test-topic")

import app  # noqa: E402


class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), app.Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_health_returns_ok(self):
        with urllib.request.urlopen(f"{self.base}/health") as r:
            self.assertEqual(r.status, 200)
            self.assertEqual(r.read().decode(), "ok")

    def test_root_greets(self):
        with urllib.request.urlopen(f"{self.base}/") as r:
            self.assertEqual(r.status, 200)
            self.assertIn("Hello from ECS Fargate", r.read().decode())

    def test_orders_rejects_non_json(self):
        req = urllib.request.Request(f"{self.base}/orders", data=b"not json", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)

    def test_unknown_post_path_is_404(self):
        req = urllib.request.Request(f"{self.base}/nope", data=b"{}", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
