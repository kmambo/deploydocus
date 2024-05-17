import json
import logging
import logging.config
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import cast

from dotenv import dotenv_values

CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(levelname)-8s] - %(module)s:%(lineno)d - %(message)s"}
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": [
            "stderr",
            "stdout",
            # "file"
        ],
    },
}

logger: logging.Logger


class WebRequestHandler(SimpleHTTPRequestHandler):
    def get_json_response(self) -> str:
        data = {
            "datetime": datetime.now(tz=timezone.utc).isoformat(),
            "status": "OK",
            "port": port,
            "ip_addr": ip_addr,
        }
        return json.dumps(data)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(self.get_json_response().encode("utf-8"))


if __name__ == "__main__":
    logging.config.dictConfig(CONFIG)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    dirname = Path("/var/lib/www")
    cfg = dotenv_values(dirname / ".env")
    port: int = int(cast(str, cfg["HTTP_PORT"]))
    ip_addr: str = cast(str, cfg["HTTP_ADDR"])
    server = HTTPServer((ip_addr, port), WebRequestHandler)
    server.serve_forever()
