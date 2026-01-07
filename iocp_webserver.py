import socket
import select
import sys


def read_index_page():
    """
    Membaca file index.html dan mengembalikan isinya sebagai string
    """
    with open("index.html", "r", encoding="utf-8") as file:
        return file.read()


def run_server():
    # Membuat socket server (IPv4, TCP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind socket ke alamat localhost dan port 8080
    server_socket.bind(("127.0.0.1", 8080))

    # Mendengarkan koneksi masuk
    server_socket.listen(5)

    # Set socket ke mode non-blocking
    server_socket.setblocking(False)

    # List socket yang dipantau oleh select
    clients = [server_socket]

    # Membaca konten index.html
    index_page = read_index_page()

    print("Server listening on port 8080...")

    try:
        while True:
            # select() akan menunggu hingga ada socket yang siap dibaca
            readable, _, _ = select.select(clients, [], [])

            for sock in readable:
                # Jika socket adalah server_socket, berarti ada koneksi baru
                if sock is server_socket:
                    client_socket, client_address = server_socket.accept()
                    client_socket.setblocking(False)

                    clients.append(client_socket)
                    print(f"New connection from {client_address}")

                # Jika socket adalah client_socket, berarti ada data dari client
                else:
                    data = sock.recv(1024)

                    # Jika data kosong, koneksi ditutup oleh client
                    if not data:
                        print(f"Connection closed by {sock.getpeername()}")
                        clients.remove(sock)
                        sock.close()
                    else:
                        # Membuat HTTP response
                        response = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: text/html\r\n"
                            f"Content-Length: {len(index_page)}\r\n"
                            "\r\n"
                            f"{index_page}"
                        )

                        # Mengirim response ke client
                        sock.sendall(response.encode("utf-8"))
                        print(f"Sent index page to {sock.getpeername()}")

    except KeyboardInterrupt:
        print("\nServer shutting down...")
        server_socket.close()
        sys.exit(0)


if __name__ == "__main__":
    run_server()
