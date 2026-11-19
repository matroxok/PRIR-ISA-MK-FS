
import random
from multiprocessing import Pool
import math

# P_m || C_max
generator = random.Random(123)
ZADANIA = [generator.randint(1, 100) for _ in range(60)]

MASZYNY = 8
POPULACJA = 100
POKOLENIA = 200


def ocen(osobnik):
    obciazenia = [0] * MASZYNY

    for i, maszyna in enumerate(osobnik):
        obciazenia[maszyna] += ZADANIA[i]

    return max(obciazenia)


def losuj_osobnika():
    return [random.randrange(MASZYNY) for _ in ZADANIA]


def turniej(oceny, wyklucz=None):
    mozliwi = [i for i in range(len(oceny)) if i != wyklucz]
    kandydaci = random.sample(mozliwi, 3)

    return min(kandydaci, key=lambda i: oceny[i])


def dziecko(rodzic1, rodzic2):
    punkt = random.randint(1, len(ZADANIA) - 1)
    nowy = rodzic1[:punkt] + rodzic2[punkt:]

    return nowy

def mutuj(osobnik):
    nowy = osobnik[:]

    for i in range(len(nowy)):
        if random.random() < 0.05:
            nowy[i] = random.randrange(MASZYNY)

    return nowy


def main():
    random.seed(43)

    populacja = [losuj_osobnika() for _ in range(POPULACJA)]

    with Pool(processes=4) as pula:
        for pokolenie in range(POKOLENIA):

            # Rownolegla ocena populacji
            oceny = pula.map(ocen, populacja)

            indeks = oceny.index(min(oceny))
            najlepszy = populacja[indeks]

            if pokolenie % 5 == 0 or pokolenie == POKOLENIA - 1:
                print(f"Pokolenie {pokolenie}: czas = {oceny[indeks]}")

            # Tworzymy dzieci
            dzieci = []

            while len(dzieci) < POPULACJA - 1:
                i1 = turniej(oceny)
                i2 = turniej(oceny, wyklucz=i1)

                dzieci.append(
                    dziecko(populacja[i1], populacja[i2])
                )

            #  mutacja
            dzieci = pula.map(mutuj, dzieci)

            nowa_populacja = [najlepszy[:]] + dzieci

            populacja = nowa_populacja

        # Ocena ostatniej populacji
        oceny = pula.map(ocen, populacja)

    najlepszy = populacja[oceny.index(min(oceny))]

    print("\nNajlepszy czas:", ocen(najlepszy))

    for m in range(MASZYNY):
        zadania = [
            i + 1 for i, maszyna in enumerate(najlepszy)
            if maszyna == m
        ]

        obciazenie = sum(ZADANIA[i - 1] for i in zadania)

        print(f"Maszyna {m + 1}: zadania {zadania}, czas = {obciazenie}")
    minimum = math.ceil(sum(ZADANIA) / MASZYNY)

    print("Dolna granica:", minimum)
    print("Wynik algorytmu:", ocen(najlepszy))

if __name__ == "__main__":
    main()



