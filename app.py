import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer
import boto3

sns = boto3.client("sns")
TOPIC_ARN = os.environ["TOPIC_ARN"]

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, text):
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, "ok")
        else:
            self._send(200, f"Hello from ECS Fargate! container={os.uname().nodename}")

    def do_POST(self):
        if self.path != "/orders":
            return self._send(404, "not found")
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            json.loads(raw)
        except ValueError:
            return self._send(400, "body must be JSON")
        # the consumer validates the content; here we only publish OrderPlaced
        sns.publish(TopicArn=TOPIC_ARN, Message=raw.decode(),
                    MessageAttributes={"eventType": {"DataType": "String", "StringValue": "OrderPlaced"}})
        self._send(202, "OrderPlaced published")

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
