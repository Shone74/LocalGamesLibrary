LOCAL GAME LIBRARY - TRENUTNO STANJE APLIKACIJE
===============================================

Datum pregleda: 28.07.2026.
Verzija aplikacije: 0.1
Platforma: Windows desktop aplikacija
Tehnologija: Python + PySide6

1. NAMENA
---------
Local Game Library je lokalna desktop aplikacija za ručno vođenje biblioteke
PC igara instaliranih na računaru. Korisnik bira .exe fajl igre, čuva osnovne
metapodatke i može da je pokrene direktno iz aplikacije.

Aplikacija nije vezana za Steam, Epic Games ili drugi launcher: može se dodati
bilo koji Windows izvršni (.exe) fajl. Steam se koristi samo kao javni izvor
za pokušaj automatskog preuzimanja slike naslovnice prilikom dodavanja igre.

2. TRENUTNO DOSTUPNE FUNKCIJE
-----------------------------

- Dodavanje igre izborom .exe fajla.
  - Putanja do izvršnog fajla se čuva.
  - Instalacioni direktorijum se automatski određuje iz putanje .exe fajla.
  - Početni naslov se automatski popunjava iz naziva .exe fajla, a korisnik
    može da ga izmeni.
  - Mogu se uneti žanr, opis, developer, publisher i datum izlaska.

- Naslovnice igara.
  - Aplikacija najpre traži lokalnu sliku u instalacionom direktorijumu igre
    (do jednog nivoa poddirektorijuma).
  - Ako je ne pronađe, u pozadinskoj niti pretražuje Steam Store i preuzima
    header sliku najbliže pronađenog rezultata u assets/covers/.
  - Korisnik može ručno da odabere PNG, JPG ili JPEG sliku.
  - Kada naslovnica nije dostupna, prikazuje se assets/default_cover.png.

- Pregled biblioteke.
  - Igre su prikazane kao kartice u mreži od četiri kolone.
  - Svaka kartica prikazuje naslovnicu, naslov, žanr, dugme PLAY i Details.
  - Postoji bočni meni: Home, All Games, Favorites, Genres i Settings.
  - Home i All Games trenutno prikazuju isti prikaz svih igara.

- Pretraga i filtriranje.
  - Polje za pretragu filtrira po naslovu, žanru, developeru i publisheru.
  - Padajući meni sadrži sve neprazne žanrove koji postoje u biblioteci.
  - Favorites prikazuje samo omiljene igre.
  - Genres uz izbor "All Genres" sortira igre po žanru, zatim po naslovu;
    izbor konkretnog žanra ograničava prikaz na taj žanr.

- Upravljanje igrom.
  - Igra može biti označena ili uklonjena iz omiljenih.
  - Details otvara modalni prozor sa većom naslovnicom, metapodacima, opisom
    i statistikama igranja.
  - Podaci igre mogu se izmeniti, osim putanje .exe fajla i instalacionog
    direktorijuma.
  - Brisanje uklanja samo zapis iz biblioteke; fajlovi same igre se ne brišu.

- Pokretanje i statistika.
  - PLAY pokreće izabrani .exe preko njegovog instalacionog direktorijuma.
  - Pre pokretanja se proverava da li izvršni fajl postoji.
  - Kod uspešnog pokretanja uvećava se play_count i upisuje ISO vreme
    last_played.

- Podešavanja (data/settings.json).
  - Tema: Dark ili Light.
  - Početni prikaz: All Games, Favorites ili Genres.
  - Potvrda pre brisanja igre.
  - Ponašanje pri pokretanju: zadržati biblioteku otvorenom ili je minimizovati
    kada se igra pokrene iz detaljnog prikaza.

3. TRENUTNI PODACI U BIBLIOTECI
-------------------------------

U data/games.json trenutno je upisano 8 igara:

1. MadMax            - omiljena, pokrenuta 1 put
2. ApexRush          - nije omiljena, nije pokretana
3. bf4               - nije omiljena, nije pokretana
4. bf6               - nije omiljena, nije pokretana
5. destiny2          - nije omiljena, nije pokretana
6. ForzaHorizon5     - nije omiljena, nije pokretana
7. GTA5              - nije omiljena, nije pokretana
8. BeamNG.drive      - nije omiljena, nije pokretana

Za svih osam igara postoje lokalno sačuvane naslovnice u assets/covers/.
Polja žanra, opisa, developera, publishera i datuma izlaska su trenutno prazna
za sve postojeće zapise.

Poslednje zabeleženo pokretanje:
- MadMax: 2026-07-28T18:26:08.534980

Aktivna podešavanja:
- Tema: Light
- Početni prikaz: All Games
- Potvrda brisanja: uključena
- Ponašanje pri pokretanju: Keep library open

Napomena: postojeće putanje igara vode na D:/GAMES/. Pokretanje će uspeti samo
na računaru na kom te putanje i odgovarajući .exe fajlovi zaista postoje.

4. STRUKTURA PROJEKTA
---------------------

main.py
  Ulazna tačka. Kreira potrebne direktorijume, QApplication i glavni prozor.

models/game.py
  Dataclass Game: model sa ID-jem, putanjama, metapodacima, statusom omiljene
  igre, brojem pokretanja i datumom poslednjeg pokretanja.

storage/json_storage.py
  Čitanje i upis biblioteke u data/games.json i podešavanja u data/settings.json.

services/game_library.py
  Poslovna logika za dodavanje, izmenu, brisanje, čuvanje i filtriranje omiljenih.

services/game_launcher.py
  Provera putanje, pokretanje igre i ažuriranje statistike.

services/cover_finder.py
  Pronalaženje lokalne slike i Steam pretraga/preuzimanje naslovnice.

ui/main_window.py
  Glavni prozor, navigacija, kartice, pretraga, filtriranje i tema.

ui/add_game_dialog.py
  Dijalog za dodavanje igre i asinhrono automatsko pronalaženje naslovnice.

ui/edit_game_dialog.py
  Dijalog za izmenu metapodataka postojeće igre.

ui/detailed_view_widget.py
  Detaljan prikaz, pokretanje, izmena i brisanje igre.

ui/game_card.py
  Komponenta kartice igre u glavnoj mreži.

ui/settings_dialog.py
  Dijalog za podešavanja.

data/games.json
  Lokalna perzistentna baza biblioteke u JSON formatu.

data/settings.json
  Lokalna perzistentna podešavanja korisničkog interfejsa.

assets/
  Podrazumevana slika i preuzete naslovnice.

5. POKRETANJE
-------------

Preduslovi:
- Python 3.8 ili noviji (projekat trenutno koristi Python 3.14 okruženje).
- Zavisnost iz requirements.txt: PySide6 >= 6.0.0.

Instalacija zavisnosti:
  pip install -r requirements.txt

Pokretanje:
  python main.py

Pri prvom pokretanju aplikacija automatski pravi data/, assets/, assets/icons/
i assets/backgrounds/ ako ne postoje. Ako nedostaje data/games.json, pravi se
prazna biblioteka. Ako nedostaje default_cover.png, generiše se jednostavna
siva zamenska slika.

6. POZNATA OGRANICENJA I NEDOVRSENE STVARI
------------------------------------------

- Aplikacija nema automatsko skeniranje diskova niti uvoz biblioteke sa Steam-a,
  Epic-a, GOG-a ili drugih launchera. Igre se dodaju pojedinačno.

- Naslovnice se preuzimaju sa Steam-a bez dodatne potvrde tačnog rezultata.
  Ako naziv .exe fajla nije prepoznatljiv, može biti odabrana naslovnica druge igre.

- Steam pretraga zahteva internet vezu; neuspeh mreže se prikazuje samo kao
  poruka da naslovnica nije pronađena.

- Preuzete naslovnice se ne kopiraju pri ručnom izboru slike. Ručno izabrana
  putanja ostaje vezana za originalni fajl, pa slika može nestati ako se taj
  fajl kasnije premesti ili obriše.

- Ne postoji sortiranje po naslovu, datumu ili broju pokretanja, osim sortiranja
  po žanru u Genres prikazu.

- Nema vizuelne poruke za praznu biblioteku ili prazne rezultate pretrage.

- Dugme za omiljene na kartici funkcionalno menja status, ali nema vidljiv tekst
  ili ikonu zvezdice, pa status nije jasno prikazan na samoj kartici.

- Opcija "Minimize library" primenjuje se iz prozora Details; pokretanje preko
  PLAY dugmeta na kartici ne minimizuje glavni prozor.

- Greške pri čitanju/upisu JSON fajlova se evidentiraju interno i ispisuju u
  konzolu; nema detaljnog ekrana za oporavak podataka ili rezervnih kopija.

- Ne postoje testovi, CI konfiguracija, instalacioni paket ni generisan .exe u
  projektu. Postoje samo uputstva za ručno PyInstaller pakovanje u README.md.

- Korisnički interfejs i većina poruka su na engleskom, dok je ovaj dokument na
  srpskom jeziku.

7. BEZBEDNOST PODATAKA
----------------------

Aplikacija čuva samo lokalne podatke o biblioteci i putanjama do igara. Ne briše
instalacije igara. Brisanje iz aplikacije uklanja samo odgovarajući JSON zapis.
Pre izmene ili većeg čišćenja biblioteke preporučuje se kopiranje fajlova:

- data/games.json
- data/settings.json

u rezervnu lokaciju.

