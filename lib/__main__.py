from pathlib import Path

from .manager import WowbotSounds


SOUNDS_DIR = Path(".")


def main(dir: Path = SOUNDS_DIR) -> int:
    w = WowbotSounds(dir)

    if w.main():
        print("Fixes required")
        return 1
    else:
        print("All good :)")
        return 0


if __name__ == "__main__":
    exit(main())
