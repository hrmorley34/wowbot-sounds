from collections import defaultdict
import json
import os
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence, Set, Tuple


SOUNDS_DIR = Path(".")
SOUNDS_FILE = SOUNDS_DIR / "sounds.json"
AUDIO_EXTENSIONS = (".aac", ".flac", ".m4a", ".mka", ".mp3", ".oga", ".ogg", ".opus", ".spx", ".wav")


def parse_file() -> Tuple[int, MutableMapping[str, Set[str]], MutableMapping[Path, Set[str]]]:
    problems: int = 0

    with open(SOUNDS_FILE, "r") as file:  # non-existant file will raise here
        sounds: Mapping[str, Mapping[str, Any]] = json.load(file)  # invalid json will raise here

    used_names: MutableMapping[str, Set[str]] = defaultdict(set)
    used_files: MutableMapping[Path, Set[str]] = defaultdict(set)

    for name, data in sounds.items():
        used_names[name].add(name)

        files: Sequence[Mapping[str, str]] = data["files"]
        filepaths: list[Path] = []

        for filespec in files:
            if "glob" in filespec:
                paths = tuple(SOUNDS_DIR.glob(filespec["glob"]))
                if not paths:
                    print(f"Empty glob in {name}: {filespec['glob']}")
                    problems += 1
                for p in paths:
                    used_files[p].add(name)
                    filepaths.append(p)

            if "filenames" in filespec:
                if not filespec["filenames"]:
                    print(f"Empty list of filenames in {name}")
                for path in filespec["filenames"]:
                    fullpath = SOUNDS_DIR / path
                    if not fullpath.exists():
                        print(f"Non-existant path in list in {name}: {path}")
                        problems += 1
                    used_files[fullpath].add(name)
                    filepaths.append(fullpath)

            if "filename" in filespec:
                # sounds_dir / example.opus
                path = SOUNDS_DIR / filespec["filename"]
                if not path.exists():
                    print(f"Non-existant path in {name}: {filespec['filename']}")
                    problems += 1
                used_files[path].add(name)
                filepaths.append(path)

        for alias in data.get("aliases", []):
            used_names[str(alias)].add(name)

        if not filepaths:
            print(f"No files for {name}")
            problems += 1

    return problems, used_names, used_files


def check_used_names(used_names: Mapping[str, Set[str]]) -> int:
    problems: int = 0

    for name, uses in used_names.items():
        if len(uses) < 2:
            continue
        prefix = "Name" if name in uses else "Alias"
        print(f"{prefix} {name} is reused in " + ", ".join(uses-{name}))
        problems += 1

    return problems


def check_used_files(used_files: Mapping[Path, Set[str]]) -> int:
    problems: int = 0

    for path, folders, files in os.walk(SOUNDS_DIR):
        path = Path(path)
        for fol in list(folders):  # (copy folders to avoid RuntimeError(iterator changed size))
            if fol[0] == ".":  # ignore folders beginning with "." (eg. .github)
                del folders[folders.index(fol)]
        for fil in files:
            if fil[0] == ".":  # ignore files beginning with "." (eg. .gitignore)
                continue
            if not fil.endswith(AUDIO_EXTENSIONS):
                continue
            if not used_files.get(path / fil):
                print(f"{path / fil} is not referenced")

    return problems


if __name__ == "__main__":
    problems, used_names, used_files = parse_file()
    problems += check_used_names(used_names)
    problems += check_used_files(used_files)

    if problems > 1:
        raise Exception(f"{problems} issues found.")
    elif problems == 1:
        raise Exception("1 issue found.")
    else:
        print("All good :)")
