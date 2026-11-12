import pickle


def _recv_exact(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(min(4096, n - len(data)))
        if not packet:
            raise ConnectionError("Połączenie zerwane przed odebraniem pełnych danych")
        data += packet
    return data


def receive_all(sock):
    length = int.from_bytes(_recv_exact(sock, 4), byteorder='big')
    return pickle.loads(_recv_exact(sock, length))
