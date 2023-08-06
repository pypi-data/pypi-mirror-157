"""
json rpc helper
"""

import socket
from dataclasses import dataclass, field
from json import dumps, loads
from typing import Dict
from uuid import uuid4

from sanic import Sanic


@dataclass
class EmptyApp:
    """
    empty dummy app in case sanic is unavailable
    """

    config: Dict = field(default_factory=dict)


def jsonrpc(data: dict, host: str = "localhost", port: int = 7583):
    """
    json rpc connection
    """
    request_id = str(uuid4())
    data.update({"jsonrpc": "2.0", "id": request_id})
    recv_buffer = []
    try:
        app = Sanic.get_app()
    except Exception:  # pylint: disable=broad-except
        app = EmptyApp()
    host = app.config.get("JSONRPC_HOST", host)
    port = app.config.get("JSONRPC_PORT", port)
    sock_type = socket.AF_INET
    sock_conn = (host, port)
    if host.startswith("unix://"):
        sock_type = socket.AF_UNIX
        sock_conn = host.replace("unix://", "")
    with socket.socket(sock_type, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(sock_conn)
            sock.settimeout(10)
            sock.sendall(dumps(data).encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)
            while True:
                chunk = sock.recv(1)
                recv_buffer.append(chunk)
                if chunk == b"\n":
                    res = loads(b"".join(recv_buffer).decode("utf-8"))
                    recv_buffer = []
                    if res.get("id") == request_id:
                        return res
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise RuntimeError(
                f"Unable to connect to signal-cli JSON RPC: {error}"
            ) from err
