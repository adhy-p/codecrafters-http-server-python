import socket

OK = b"HTTP/1.1 200 OK\r\n\r\n"
NOT_FOUND = b"HTTP/1.1 404 Not Found\r\n\r\n"


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client, addr = server_socket.accept()
    msg = client.recv(1024)
    headers = msg.split(b"\r\n")[0]
    method, path, version = headers.split()
    client.sendall(OK if path == b'/' else NOT_FOUND)


if __name__ == "__main__":
    main()
