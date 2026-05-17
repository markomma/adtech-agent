"""Sync taxonomy/mapping/index data from repo root into adtech_crosswalk/data/."""
import shutil
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent
_DATA_DIR = Path(__file__).parent / "data"


def sync() -> None:
    _DATA_DIR.mkdir(exist_ok=True)

    shutil.copy(_REPO_ROOT / "index.json", _DATA_DIR / "index.json")
    print("Synced index.json")

    for dest in (_DATA_DIR / "taxonomies", _DATA_DIR / "mappings"):
        if dest.exists():
            shutil.rmtree(dest)

    shutil.copytree(_REPO_ROOT / "taxonomies", _DATA_DIR / "taxonomies")
    print("Synced taxonomies/ (including search indices)")

    shutil.copytree(_REPO_ROOT / "mappings", _DATA_DIR / "mappings")
    print("Synced mappings/")

    print(f"Done — data live at {_DATA_DIR.relative_to(_REPO_ROOT)}")


def main() -> None:
    sync()


if __name__ == "__main__":
    main()
