"""
Założenia:

- Możliwość przejechania się jeden raz po pliku i rozdzielenia według ustawień od użytkownika
- Możliwość przekazania pliku tekstowego jako tekst jaki chcemy aby tool znalazł samodzielnie
  W tym przypadku tool powinien każdy podzielony plik wav sprawdzić co wypowiada postać i sprawdzić czy już takie coś gdzieś w tekście występuje
  Jeżeli wystepuje to powinien taki plik przenieść na osobną listę wygenerowanych plików a pozostałe pliki zachować do dalszego przetwarzania lub skasować (zalezy od usera)

- Możliwość automatycznego przejechania się po np 10 podanych wartościach od użytkownika i porównaniu czy wyłapie tekst z pliku tekstowego

- pliki tekstowe powinny być podzielone na listę zdań a następnie każde zdanie musi być pozbawione znaków interpunkcyjnych, spacji i zmienione na małe litery
  To oczywiście może nie być najlepsza opcja ale zawsze coś

- możliwość wyplucia plików audio i plików z outputem w formacie zip aby nie korzystać z dodatkowego kodu w colabie

- jeżeli podany plik to nie wav to przetestować czy da się podzielić tak samo dobrze - w innym przypadku przekonwertować na mono 22050 wav i wtedy działać

- zrobić kopie zdań jeżeli w zdaniu występują liczby i zamienić je na słownie i na odwrót (to może być problematyczne)

-
path_to_wav_file = "/content/input/roch siemianowski _ audiobook.wav"            #@param {type:"string"}
silence_length_1 = 300 #@param {type:"slider", min:0, max:1000, step:10}
silence_length_2 = 150 #@param {type:"slider", min:0, max:999, step:10}
silence_threshold = -60 #@param {type:"slider", min:-100, max:0, step:1}


vst-splitter -i /path/to/file.wav -o /path/to/folder -b 300 -e 150 -t -60
vst-splitter -i /path/to/file.wav -o /path/to/folder -m -b "350,300,250,200" -e "200,150,100,50" -t "-70,-60,-50,-40"
  Wymagane jest identyczna ilość parametrów (4) lub powinno robić tyle razy ile parametrów razem mnożonych czyli:
  4*3*2 = 24 podejścia (no może z pominięciem powtarzania o ile wystąpi)

"""