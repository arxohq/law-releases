#!/usr/bin/env python3
"""Exercise installed CLI and LSP in an empty directory, outside the checkout."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def frame(message):
    body = json.dumps(message).encode()
    return f"Content-Length: {len(body)}\r\n\r\n".encode() + body


def smoke(bin_dir):
    law, lsp = (str((bin_dir / name).resolve()) for name in ("law", "law-lsp"))
    with tempfile.TemporaryDirectory(prefix="arxo-nix-smoke-") as scratch:
        def run(*args):
            return subprocess.run(args, cwd=scratch, check=True, capture_output=True, timeout=60)
        run(law, "version", "--json")
        run(law, "init", "example", "--name", "nix.smoke")
        run(law, "case", "check", "--project", "example", "--case", "Main", "--json")
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"processId": None, "rootUri": None, "capabilities": {}}},
            {"jsonrpc": "2.0", "method": "initialized", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "shutdown", "params": None},
            {"jsonrpc": "2.0", "method": "exit", "params": None},
        ]
        result = subprocess.run([lsp, "--stdio"], input=b"".join(map(frame, messages)), cwd=scratch,
                                capture_output=True, check=True, timeout=30)
        data, replies = result.stdout, {}
        while data:
            headers, body = data.split(b"\r\n\r\n", 1)
            length = int(next(line.split(b":", 1)[1] for line in headers.split(b"\r\n")
                              if line.lower().startswith(b"content-length:")))
            reply = json.loads(body[:length])
            if "id" in reply:
                replies[reply["id"]] = reply
            data = body[length:]
        assert "capabilities" in replies[1]["result"], replies
        assert replies[2].get("result", "missing") is None, replies
    print("Arxo Nix smoke: CLI project + LSP initialize/shutdown passed")


if __name__ == "__main__":
    smoke(Path(sys.argv[1]))
