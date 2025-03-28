import socket
import selectors

sel = selectors.DefaultSelector()


class ClientHandler:
    def __init__(self, conn, addr, server):
        self.conn = conn
        self.addr = addr
        self.server = server

    def handle_read(self):
        try:
            data = self.conn.recv(1024)
            if data:
                message = data.decode().strip()
                response = message.upper()
                self.conn.sendall(response.encode())
            else:
                self.disconnect()
        except Exception as e:
            print(f"Error con cliente {self.addr}: {e}")
            self.disconnect()

    def disconnect(self):
        print(f"Cerrando conexion para {self.addr}")
        self.server.remove_client(self)
        sel.unregister(self.conn)
        self.conn.close()


class Server:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.clients = []

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        server_socket.setblocking(False)
        sel.register(server_socket, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = sel.select(timeout=1)
                for key, mask in events:
                    if key.data is None:
                        self._accept_connection(key.fileobj)
                    else:
                        client_handler = key.data
                        if mask & selectors.EVENT_READ:
                            client_handler.handle_read()
        except KeyboardInterrupt:
            print("\nshutting down...")
        finally:
            server_socket.close()
            sel.close()

    def _accept_connection(self, server_socket):
        conn, addr = server_socket.accept()
        conn.setblocking(False)
        client = ClientHandler(conn, addr, self)
        self.clients.append(client)
        sel.register(conn, selectors.EVENT_READ, data=client)
        print(f"Cliente conectado {addr}")

    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)


if __name__ == "__main__":
    server = Server(port=5000)
    server.start()
