import socket
import threading


def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(f"\nServer > {data.decode()}")
        except Exception as e:
            print(f"\nError recibiendo data: {e}")
            break


def start_client(host="127.0.0.1", port=5000):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))

            receiver_thread = threading.Thread(
                target=receive_messages, args=(sock,), daemon=True
            )
            receiver_thread.start()

            while True:
                msg = input("> ")
                sock.sendall(msg.encode())

                if msg.lower() == "desconexion":
                    print("Desconectando")
                    break
    except ConnectionRefusedError:
        print("Servidor no disponible")
    except Exception as e:
        print(f"Error de conexion: {e}")


if __name__ == "__main__":
    start_client()
