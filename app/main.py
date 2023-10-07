import socket

OK = b"HTTP/1.1 200 OK\r\n"
NOT_FOUND = b"HTTP/1.1 404 Not Found\r\n"
CONTENT_TYPE = b"Content-Type: text/plain\r\n"
END = b"\r\n"


def gen_content_len(n: int):
    return f"Content-Length: {n}\r\n".encode()


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client, addr = server_socket.accept()
    msg = client.recv(1024)
    headers = msg.split(b"\r\n")[0]
    method, path, version = headers.split()
    response = b""
    echo_idx = path.find(b"/echo")
    if echo_idx != -1:
        message = path[echo_idx + len("/echo/"):]
        resp_header = OK + CONTENT_TYPE + gen_content_len(len(message)) + END
        response = resp_header + message
    else:
        response = NOT_FOUND + END
    client.sendall(response)


if __name__ == "__main__":
    main()
