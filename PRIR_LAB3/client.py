import argparse
import socket

from receive import receive_all
from send import send_all
from task1_parallel_image import process_fragment

SERVER_IP = "172.20.10.14"


def client_main(host=SERVER_IP, port=2040):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    task = receive_all(client_socket)          # (idx, fragment, crop_top, crop_bottom)
    processed_fragment = process_fragment(task)  # (idx, przetworzony fragment)
    send_all(client_socket, processed_fragment)
    client_socket.close()
    print("Fragment przetworzony i wysłany z powrotem do serwera")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Klient: odbiera fragment, nakłada filtr Sobela, odsyła wynik.")
    parser.add_argument("--host", default=SERVER_IP, help=f"IP serwera (domyślnie {SERVER_IP})")
    parser.add_argument("--port", type=int, default=2040)
    args = parser.parse_args()
    client_main(args.host, args.port)
