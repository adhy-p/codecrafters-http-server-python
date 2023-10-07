import socket


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client, addr = server_socket.accept()
    while True:
        client.recv(2048)
        client.send(b"HTTP/1.1 200 OK\r\n\r\n")


if __name__ == "__main__":
    main()
