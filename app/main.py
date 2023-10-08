from select import select
from socket import create_server
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

OK = b"HTTP/1.1 200 OK\r\n"
CREATED = b"HTTP/1.1 201 OK\r\n"
NOT_FOUND = b"HTTP/1.1 404 Not Found\r\n"
CT_TEXTPLAIN = b"Content-Type: text/plain\r\n"
CT_APPSTREAM = b"Content-Type: application/octet-stream\r\n"
END = b"\r\n"


class HTTPServer:
    def __init__(self, dir: str | None = None):
        dir_path = Path(dir) if dir else Path('.')
        self.server_socket = create_server(
                ("localhost", 4221),
                reuse_port=True)
        self.server_socket.setblocking(0)
        self.active_conn = [self.server_socket]
        self.content_dir = dir_path
        self.SUPPORTED_GET_ENDPOINTS = {
                b'': self.handle_index,
                b'echo': self.handle_echo,
                b'user-agent': self.handle_user_agent,
                b'files': self.handle_get_file,
            }
        self.SUPPORTED_POST_ENDPOINTS = {
                b'files': self.handle_post_file,
            }

    def handle_new_client(self, server_sock):
        client, addr = server_sock.accept()
        self.active_conn.append(client)

    def handle_request(self, client):
        msg: bytes = client.recv(4096)

        if not msg:
            self.active_conn.remove(client)
            return

        headers: bytes
        body: list[bytes]
        headers, *body = msg.split(b"\r\n\r\n")
        body: bytes
        body = body[0] if len(body) == 1 else b"\r\n\r\n".join(body)
        headers_dict: dict[str, bytes] = self.parse_headers(headers)
        while len(body) < int(headers_dict.get('Content-Length', 0)):
            body += client.recv(4096)

        response: bytes
        method: bytes = headers_dict['method']
        path: list[bytes] = headers_dict['path'].split(b'/')[1]

        if method == b'GET':
            if path in self.SUPPORTED_GET_ENDPOINTS:
                response = self.SUPPORTED_GET_ENDPOINTS[path](headers_dict, body)
            else:
                response = self.handle_not_found()
        elif method == b'POST':
            if path in self.SUPPORTED_POST_ENDPOINTS:
                response = self.SUPPORTED_POST_ENDPOINTS[path](headers_dict, body)
            else:
                response = self.handle_not_found()
        else:
            response = self.handle_not_found()

        print(response)
        client.sendall(response)

    def serve(self):
        while True:
            readable: list[Any]
            writable: list[Any]
            exceptions: list[Any]

            readable, writable, exceptions = select(self.active_conn, [], [])

            for s in readable:
                if s is self.server_socket:
                    self.handle_new_client(s)
                else:
                    self.handle_request(s)

            for s in exceptions:
                self.active_conn.remove(s)
                s.close()

    def parse_headers(self, headers: bytes) -> dict[str, bytes]:
        headers: list[bytes] = headers.split(b"\r\n")

        method: bytes
        path: bytes
        version: bytes

        method, path, version = headers[0].split()  # status line

        parsed_header: dict[str, bytes] = {
            'method': method,
            'path': path,
            'version': version,
            }

        for header in headers[1:]:
            key: bytes
            value: list[bytes]
            key, *value = [h.strip() for h in header.split(b':')]
            parsed_header[key.decode()] = b"".join(value)
        return parsed_header

    def gen_content_len(self, n: int) -> bytes:
        return f"Content-Length: {n}\r\n".encode()

    def handle_index(self, headers: dict[str, bytes], body: bytes) -> bytes:
        return OK + CT_TEXTPLAIN + self.gen_content_len(0) + END

    def handle_not_found(self) -> bytes:
        return NOT_FOUND + CT_TEXTPLAIN + self.gen_content_len(0) + END

    def handle_echo(self, headers: dict[str, bytes], body: bytes) -> bytes:
        message = headers['path'].split(b'/')[2:]
        message: bytes = b"/".join(message)
        resp_header = OK + CT_TEXTPLAIN\
            + self.gen_content_len(len(message)) + END
        return resp_header + message

    def handle_user_agent(self, headers: dict[str, bytes], body: bytes)\
            -> bytes:
        agent = headers['User-Agent']
        resp_header = OK + CT_TEXTPLAIN\
            + self.gen_content_len(len(agent)) + END
        return resp_header + agent

    def handle_get_file(self, headers: dict[str, bytes], body: bytes) -> bytes:
        requested_file = headers['path'].split(b'/')[2:]
        requested_file: str = b"".join(requested_file).decode()
        try:
            with open(f"{self.content_dir}/{requested_file}", "rb") as f:
                data = f.read()
                header = OK + CT_APPSTREAM + self.gen_content_len(len(data))\
                    + END
                return header + data
        except FileNotFoundError:
            return self.handle_not_found()

    def handle_post_file(self, headers: dict[str, bytes], body: bytes)\
            -> bytes:
        uploaded_file = headers['path'].split(b'/')[2:]
        uploaded_file: str = b"".join(uploaded_file).decode()
        try:
            with open(f"{self.content_dir}/{uploaded_file}", "wb") as f:
                f.write(body)
            return CREATED + CT_TEXTPLAIN + self.gen_content_len(0) + END
        except FileNotFoundError:
            return self.handle_not_found()


def main():
    print("Logs from your program will appear here!")
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-d', '--directory')
    args = arg_parser.parse_args()
    server = HTTPServer(args.directory)
    server.serve()


if __name__ == "__main__":
    main()
