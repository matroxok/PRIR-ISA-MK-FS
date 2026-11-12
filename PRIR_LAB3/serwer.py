import argparse
import socket

import numpy as np
from PIL import Image

from receive import receive_all
from send import send_all
from task1_parallel_image import merge_fragments, split_image


def server_main(image_path, n_clients, host="0.0.0.0", port=2040, output="processed_image.png"):
    image_array = np.array(Image.open(image_path))
    fragments = split_image(image_array, n_clients, overlap=1)
    n_clients = len(fragments)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(n_clients)
    print(f"Serwer nasłuchuje na {host}:{port}, oczekuje {n_clients} klientów...")

    processed_fragments = []
    for i in range(n_clients):
        client_socket, client_address = server_socket.accept()
        print(f"Połączono z klientem {i + 1}: {client_address}")
        send_all(client_socket, fragments[i])
        processed_fragments.append(receive_all(client_socket))
        client_socket.close()
    server_socket.close()

    merged = merge_fragments(processed_fragments)
    Image.fromarray(merged, mode="L").save(output)
    print(f"Obraz przetworzony zapisany jako {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serwer: dzieli obraz i rozsyła fragmenty do klientów.")
    parser.add_argument("image", nargs="?", default="input.JPG", help="Obraz wejściowy")
    parser.add_argument("--clients", type=int, default=2, help="Liczba klientów (fragmentów)")
    parser.add_argument("--host", default="172.20.10.14", help="Adres nasłuchiwania (domyślnie wszystkie interfejsy)")
    parser.add_argument("--port", type=int, default=2040)
    parser.add_argument("--output", default="processed_image.png")
    args = parser.parse_args()
    server_main(args.image, args.clients, args.host, args.port, args.output)
