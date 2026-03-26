from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import NOTES_DIR


def get_folders():
    folders = []

    for folder in NOTES_DIR.rglob("*"):
        if not folder.is_dir():
            continue

        if (
            folder.name == "Assets"
            or any(part.startswith(".obsidian") for part in folder.parts)
        ):
            continue

        rel_path = folder.relative_to(NOTES_DIR)

        folders.append(rel_path.as_posix())

    return sorted(folders)

def get_file_names(folder_path: str):
    base = NOTES_DIR / folder_path if folder_path else NOTES_DIR

    if not base.exists():
        return []

    return [f.name for f in base.iterdir() if f.is_file()]