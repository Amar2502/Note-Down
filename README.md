# NoteDown

An always-on-top quick capture tool for Obsidian users. NoteDown lets you capture text, screenshots, and audio into a single Markdown “session” note without breaking your workflow.

## Download

Get the latest Windows build here: https://github.com/Amar2502/NoteDown/releases/latest

## What It Does

- **Session-based notes**: start a session (creates/continues a `.md` file) and keep appending captures until you end it.
- **Text capture**: Copy any important text, then click the Clip button – the text is instantly added as a bullet point in your session note.
- **Screenshot capture**: Take a screenshot (using your usual shortcut), then click the Image button – the latest screenshot is grabbed from your screenshots folder, copied to your Obsidian `Assets/`, and embedded in your note.
- **Audio capture**: press once to start recording, press again to stop; saves a `.wav` into `Assets/` and embeds it in the note.
- **Obsidian-friendly output**: attachments are embedded using `![[filename.ext]]` so they resolve inside your vault.
- **Always on top UI**: a small PyQt6 window designed for fast capture while you stay in your current app.

## How Notes Are Saved

When you start a session, NoteDown creates (or reuses) a Markdown file named after your session:

- Location: **your Obsidian vault root** (or a subfolder you choose in the UI)
- Filename: session name “sanitized” into a slug (spaces -> `-`, lowercase)
- Frontmatter: title/date/tags

During the session, captures are appended under `# Session Notes`.

## First Run Setup (Paths)

On first run, NoteDown asks you to configure:

- **Obsidian Vault path** (folder that contains `.obsidian/`)
- **Assets folder path** (defaults to `<vault>/Assets` and will be created if missing)
- **Screenshots folder path** (where NoteDown looks for your latest screenshot)

These settings are stored at:

`%APPDATA%/NoteDown/config.json`

To reconfigure later, delete that file and run NoteDown again.

## Usage (Typical Flow)

1. **Start session** → choose a session name (and optional subfolder in your vault)
2. **Text** → copy something, then press Text to append clipboard content
3. **Image** → take a screenshot (Win+Shift+S, etc.), then press Image
4. **Audio** → press Audio to start recording, press again to stop and save
5. **End session** when you’re done

## Development

### Requirements

- Python 3.x (Windows)
- Dependencies in `requirements.txt`:
  - PyQt6 (UI)
  - pyperclip (clipboard text)
  - PyAudio (microphone recording)

### Run from source

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python start.py
```

### Build an executable (PyInstaller)

This repo includes `NoteDown.spec` for PyInstaller.

```bash
pip install pyinstaller
pyinstaller NoteDown.spec
```

## Notes / Troubleshooting

- **No text captured**: NoteDown reads from the clipboard; make sure you copied text first.
- **No screenshot captured**: NoteDown picks the newest `.png/.jpg/.jpeg` from your configured screenshots folder.
- **Audio issues**: PyAudio depends on audio drivers/devices; ensure a working microphone is selected and permissions allow recording.

## License

MIT (see `LICENSE`).

