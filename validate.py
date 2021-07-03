from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence, Set


SOUNDS_DIR = Path(".")
SOUNDS_FILE = SOUNDS_DIR / "sounds.json"


with open(SOUNDS_FILE, "r") as file:  # non-existant file will raise here
    sounds: Mapping[str, Mapping[str, Any]] = json.load(file)  # invalid json will raise here


problems = 0
used_names: MutableMapping[str, Set[str]] = defaultdict(set)


for name, data in sounds.items():
    if name in used_names:
        print(f"Sound name {name} is already used in {used_names[name]}")
        problems += 1
    used_names[name].add(name)

    files: Sequence[Mapping[str, str]] = data["files"]

    # arrays: Sequence[Sequence[Path]] = []
    # weights: Sequence[int] = []
    for filespec in files:
        # filenames = []

        if "glob" in filespec:
            # sounds_dir / something-*.opus
            paths = tuple(SOUNDS_DIR.glob(filespec["glob"]))
            if not paths:
                print(f"Empty glob in {name}: {filespec['glob']}")
                problems += 1
            # filenames.extend(paths)

        if "filenames" in filespec:
            # sounds_dir / 1.opus , sounds_dir / 2.opus , ...
            paths = tuple(map(SOUNDS_DIR.joinpath, filespec["filenames"]))
            if not paths:
                print(f"Empty list of filenames in {name}: {filespec['filenames']}")
            for orig, path in zip(filespec["filenames"], paths):
                if not path.exists():
                    print(f"Non-existant path in list in {name}: {orig}")
                    problems += 1
            # filenames.extend(paths)

        if "filename" in filespec:
            # sounds_dir / example.opus
            path = SOUNDS_DIR / filespec["filename"]
            if not path.exists():
                print(f"Non-existant path in {name}: {filespec['filename']}")
                problems += 1
            # filenames.append(path)

        # if len(filenames) >= 1:
        #     arrays.append(filenames)
        #     weights.append(filespec.get("weight", 1))

    for alias in data.get("aliases", []):
        if alias in used_names:
            print(f"Sound name alias {alias} (of {name}) is already used in {used_names[name]}")
            problems += 1
        used_names[str(alias)].add(name)


if problems > 1:
    raise Exception(f"{problems} issues found.")
elif problems == 1:
    raise Exception("1 issue found.")
else:
    print("All good :)")
