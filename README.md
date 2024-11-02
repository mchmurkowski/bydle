# 🐮 ByDLe - wydój dane z GUS

## ByDLe mówi Muuuu!

Każdy urzędnik czy analityk, który regularnie pozyskuje dane z [Banku Danych Lokalnych GUS](https://bdl.stat.gov.pl), wie, że może to być uciążliwy proces. Przeklikiwanie się przez witrynę w poszukiwaniu jednostki terytorialnej, potem wybieranie odpowiednich tematów, zakresów lat, ...

ByDLe pozwala hurtowo ściągać dane z BDL GUS dla wybranej jednostki terytorialnej przy pomocy prostego wizualnego interfejsu za pośrednictwem [API BDL GUS](https://api.stat.gov.pl/Home/BdlApi).

> [!NOTE]
> Póki co, ByDLe nie radzi sobie z dużymi zbiorami danych, czyli takimi, które mają więcej niż 100 zmiennych na temat, np. *Ludność wg pojedynczych roczników wieku i płci (dane półroczne) (P3472)*.

## ByDLe jest z wolnego wybiegu

ByDLe pasie się na [licencji MIT](LICENSE) - korzystaj z niego swobodnie i za darmo.

## Jak uruchomić ByDLe?

> [!IMPORTANT]
> Do uruchomienia ByDLa potrzebujesz zainstalowanych `python>=3.9` z obsługą modułu `tkinter` i bibliotek `requests` oraz `pandas`.

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/mchmurkowski/bydle.git
   ```
2. Przejdź do folderu i uruchom skrypt:
   ```bash
   python app.py
   ```

> [!TIP]
> Jeżeli użycie `git` nie wchodzi w grę (np. na służbowym komputerze), możesz pobrać repozytorium klikając zielony przycisk *Code* na górze strony, a następnie w opcję *Download ZIP*.

## Przykład użycia

ByDLe ma prosty wizualny interfejs. Aby pobrać dane:

1. Pierwsze **wyszukaj**, a potem **wybierz** jednostkę terytorialną z listy.
2. **Wpisz** interesujące Cię identyfikatory tematów (podgrup) oddzielone spacjami - np. `P2914 P3256` - i kliknij przycisk **Pobierz**.

ByDLe zapisze pobrane dane w formacie `csv` w wybranym przez Ciebie folderze.

## Wsparcie i rozwój

ByDLe jest młode i jak każdemu cielakowi czasem zdarza mu się zwariować i pogubić. Jeżeli natrafiłeś na błąd lub uważasz, że ByDLe powinno mieć więcej dzwonków i gwizdków, daj mi znać, np. zgłaszając to poprzez *Issues* w repozytorium - zobaczę co uda mi się z tym zrobić.