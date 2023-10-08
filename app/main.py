import socket

OK = b"HTTP/1.1 200 OK\r\n"
NOT_FOUND = b"HTTP/1.1 404 Not Found\r\n"
CONTENT_TYPE = b"Content-Type: text/plain\r\n"
END = b"\r\n"


def parse_headers(headers) -> dict:
    headers = headers.split(b"\r\n")
    method, path, version = headers[0].split()  # status line
    parsed_header = {
        'method': method,
        'path': path,
        'version': version,
        }
    for header in headers[1:]:
        key, *value = [h.strip() for h in header.split(b':')]
        parsed_header[key.decode()] = b"".join(value)
    return parsed_header


def gen_content_len(n: int):
    return f"Content-Length: {n}\r\n".encode()


def handle_echo(path, echo_idx):
    message = path[echo_idx + len("/echo/"):]
    resp_header = OK + CONTENT_TYPE + gen_content_len(len(message)) + END
    return resp_header + message


def handle_user_agent(agent):
    resp_header = OK + CONTENT_TYPE + gen_content_len(len(agent)) + END
    return resp_header + agent


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client, addr = server_socket.accept()
    msg = client.recv(1024)
    headers, *body = msg.split(b"\r\n\r\n")
    headers_dict = parse_headers(headers)

    response = b""
    path = headers_dict['path']

    if path == b"/":
        response = OK + END
    elif (echo_idx := path.find(b"/echo")) != -1:
        response = handle_echo(path, echo_idx)
    elif path.find(b"/user-agent") != -1:
        response = handle_user_agent(headers_dict['User-Agent'])
    else:
        response = NOT_FOUND + END

    client.sendall(response)


if __name__ == "__main__":
    main()
