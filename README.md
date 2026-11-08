# Boomb0y0 spell timer

A small, free overlay for League of Legends that tracks enemy **summoner spell cooldowns** (Flash, Ignite, Teleport...).
You click when you see an enemy use a spell, and it counts down for you and tells you when it is back.

> **It is fully manual.** It does not read the game, does not touch the game process, and does not automate anything. Every timer starts only when *you* click.

مؤقّت بسيط لسبلات الأعداء في ليج أوف ليجندز. إنت اللي بتدوس لما تشوف العدو استخدم السبيل، والبرنامج بيعد لك الكول داون وبيقولك لما يرجع. **يدوي بالكامل**، مبيقراش حاجة من اللعبة.

## Features

- Five rows: Top (3 spells), Jungle, Mid, Support, ADC (2 spells each), in that order.
- **Left click** a spell icon to start its cooldown. **Right click** to cancel it or change the spell.
- Voice callout when a spell is back, for example "Top Flash is back" (uses the built-in Windows voice, works offline).
- **AH button** next to each row cycles summoner-spell haste presets (0 / 12 / 18 / 30).
- Real transparent overlay that does not take focus from the game.
- **Show / Hide hotkey**: you choose the key yourself. Hiding it gives the game its full speed back.
- Resizable (A- / A+ in the settings, or Ctrl + mouse wheel), draggable, remembers its size and position.
- Settings (gear icon, top right): size, reset, voice, transparent or dark background, always-on-top, hotkey, hide, exit.
- Tray icon next to the clock to hide / show or exit.

## Download

Get the latest `Boomb0y0.exe` from the [Releases](../../releases) page. No installer, no Python needed.

- The first launch needs internet once, to download the spell icons from Riot's official Data Dragon CDN. After that it works offline.
- Windows may show "Windows protected your PC" because the file is not code-signed. Click **More info** then **Run anyway**. You can also read the source here and build it yourself.
- Tip: set the game to **Borderless** so the overlay can appear on top.

## Build it yourself

You need Windows and [Python 3](https://www.python.org/downloads/) (tick "Add python.exe to PATH").

1. Put `lol_timer.py`, `build.bat` and `Boomb0y0.spec` in one folder.
2. Double-click `build.bat`.
3. Your program is in `dist\Boomb0y0.exe`.

If the lite build does not open, run `build.bat safe`.

To just run it from source: `pip install PyQt6`, then `python lol_timer.py`.

## Customize

Open `lol_timer.py`:

- `SPELLS`: base cooldowns in seconds. They change with patches, so check them against the current game values.
- `ROLES`: which spells each row starts with.
- `HASTE_STEPS`: the presets the AH button cycles through.

## Privacy

No accounts, no tracking, no data sent anywhere. The only network request is downloading the spell icons from Riot's CDN. Settings are saved locally (next to the script, or in `%APPDATA%\LoLSpellTimer` for the exe).

## License

GNU GPL v3 (see `LICENSE`). The program uses PyQt6, which is GPL-licensed.

## Disclaimer

Boomb0y0 spell timer is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and League of Legends are trademarks or registered trademarks of Riot Games, Inc. Use at your own risk; check Riot's current third-party application policy.
