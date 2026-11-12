
using System;
using System.Threading;
using System.Threading.Tasks;

int zloze = 2000;
int magazyn = 0;
int liczbaGornikow = 5;
string[] statusy = new string[liczbaGornikow];
bool odswiezac = true;

object blokada = new object();

SemaphoreSlim kopalnia = NewMethod();
SemaphoreSlim sklad = new SemaphoreSlim(1);

void Status(int numer, string tekst)
{
    lock (blokada)
    {
        statusy[numer - 1] = tekst;
    }
}

void Ekran()
{
    lock (blokada)
    {
        Console.SetCursorPosition(0, 0);

        Console.WriteLine($"Zloze: {zloze}".PadRight(50));
        Console.WriteLine($"Magazyn: {magazyn}".PadRight(50));
        Console.WriteLine();

        for (int i = 0; i < statusy.Length; i++)
        {
            Console.WriteLine(
                $"Gornik {i + 1}: {statusy[i]}".PadRight(50)
            );
        }
    }
}


void Gornik(int numer)
{
    while (true)
    {
        int ladunek = 0;

        Status(numer, "Czeka na kopalnie");

        kopalnia.Wait();

        Status(numer, "Wydobywa wegiel");

        for (int i = 0; i < 200; i++)
        {
            Thread.Sleep(10);

            lock (blokada)
            {
                if (zloze == 0) break;

                zloze--;
                ladunek++;
            }
        }

        kopalnia.Release();

        if (ladunek == 0) break;

        Status(numer, "Transportuje wegiel");

        Thread.Sleep(10000);

        Status(numer, "Czeka na magazyn");

        sklad.Wait();

        Status(numer, "Rozladowuje wegiel");

        for (int i = 0; i < ladunek; i++)
        {
            Thread.Sleep(10);

            lock (blokada)
                magazyn++;
        }

        sklad.Release();

        lock (blokada)
        {
            if (zloze == 0) break;
        }

        Status(numer, "Wraca do kopalni");

        Thread.Sleep(10000);
    }

    Status(numer, "Zakonczyl prace");
}

Console.Clear();

Task monitor = Task.Run(() =>
{
    while (true)
    {
        lock (blokada)
        {
            if (!odswiezac) break;
        }

        Ekran();
        Thread.Sleep(200);
    }
});

Task[] zadania = new Task[liczbaGornikow];

for (int i = 0; i < liczbaGornikow; i++)
{
    int numer = i + 1;
    zadania[i] = Task.Run(() => Gornik(numer));
}

Task.WaitAll(zadania);
lock (blokada)
    odswiezac = false;

monitor.Wait();
Ekran();

Console.WriteLine($"Pozostalo w zlozu: {zloze}");
Console.WriteLine($"W magazynie: {magazyn}");

static SemaphoreSlim NewMethod()
{
    return new SemaphoreSlim(2);
}