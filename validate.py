import json
import os
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Set, Tuple

from lib.command import BaseSlashCommand, Command, SlashOptionCommand
from lib.problem import Problem
from lib.sound import Sound, SoundDict
from lib.typing import SOUNDS_JSON, COMMANDS_JSON, COMMANDS_SLASH_JSON, CommandCommonName, CommandName, SlashGroup, SlashName
from lib.verbose import verbose


SOUNDS_DIR = Path(".")
SOUNDS_FILE = SOUNDS_DIR / "sounds.json"
COMMANDS_FILE = SOUNDS_DIR / "commands.json"
COMMANDS_SLASH_FILE = SOUNDS_DIR / "commands_slash.json"
AUDIO_EXTENSIONS = (".aac", ".flac", ".m4a", ".mka", ".mp3", ".oga", ".ogg", ".opus", ".spx", ".wav")


def parse_sounds() -> SoundDict:
    with open(SOUNDS_FILE, "r") as file:  # non-existant file will raise here
        sounds_json: SOUNDS_JSON = json.load(file)  # invalid json will raise here

    sounds: SoundDict = dict()
    for name, sound in sounds_json.items():
        sounds[name] = Sound.init_verbose(SOUNDS_DIR, name, sound)

    return sounds


def parse_commands(sounds: SoundDict):
    with open(COMMANDS_FILE, "r") as file:  # non-existant file will raise here
        commands_json: COMMANDS_JSON = json.load(file)  # invalid json will raise here

    commands: Dict[CommandName, Command] = dict()
    aliases: Set[CommandCommonName] = set()
    for name, data in commands_json.items():
        if name in aliases:
            verbose.problems.append(Problem(f"Reuse of name {name!r}", context=f"Command {name!r}"))
        aliases.add(name)

        try:
            cmd = Command(name, data, sounds=sounds)
        except KeyError as e:
            verbose.problems.append(Problem(f"Missing key {e.args[0]}", context=f"Command {name!r}"))
            continue
        # except Exception as e:
        #     verbose.problems.append(Problem(f"{e!r}", context=f"Command {name!r}"))
        #     continue
        else:
            commands[name] = cmd
            for a in cmd.aliases:
                if a in aliases:
                    verbose.problems.append(Problem(f"Reuse of alias {a!r}", context=f"Command {name!r}"))
                aliases.add(a)


def parse_slash_commands(sounds: SoundDict):
    with open(COMMANDS_SLASH_FILE, "r") as file:  # non-existant file will raise here
        slash_commands_json: COMMANDS_SLASH_JSON = json.load(file)  # invalid json will raise here

    commands: Dict[Tuple[Optional[SlashGroup], SlashName], BaseSlashCommand] = dict()

    for group, cmds in slash_commands_json.items():
        if not group:
            group = None
        for name, data in cmds.items():
            try:
                command = BaseSlashCommand(group, name, data, sounds=sounds)
            except KeyError as e:
                verbose.problems.append(Problem(f"Missing key {e.args[0]}", context=f"Slashcommand {group!r}.{name!r}"))
                continue
            # except Exception as e:
            #     verbose.problems.append(Problem(f"{e!r}", context=f"Slashcommand {group!r}.{name!r}"))
            #     continue
            else:
                commands[group, name] = command
                if isinstance(command, SlashOptionCommand):
                    if command.default not in command.options:
                        verbose.problems.append(Problem(f"Default sound {command.default!r}", context=f"Slashcommand {group!r}.{name!r}"))


# def parse_file() -> Tuple[int, MutableMapping[str, Set[str]], MutableMapping[Path, Set[str]]]:
#     problems: int = 0

#     with open(SOUNDS_DIR / "sounds.json", "r") as file:  # non-existant file will raise here
#         sounds: SOUNDS_JSON = json.load(file)  # invalid json will raise here

#     with open(SOUNDS_DIR / "commands.json", "r") as file:  # non-existant file will raise here
#         commands: COMMANDS_JSON = json.load(file)  # invalid json will raise here

#     with open(SOUNDS_DIR / "commands_slash.json", "r") as file:  # non-existant file will raise here
#         slash_commands: COMMANDS_SLASH_JSON = json.load(file)  # invalid json will raise here

#     used_names: MutableMapping[str, Set[str]] = defaultdict(set)
#     used_files: MutableMapping[Path, Set[str]] = defaultdict(set)

#     for name, data in sounds.items():
#         used_names[name].add(name)

#         filepaths: list[Path] = []

#         for filespec in data:
#             if "glob" in filespec:
#                 paths = tuple(SOUNDS_DIR.glob(filespec["glob"]))
#                 if not paths:
#                     print(f"Empty glob in {name}: {filespec['glob']}")
#                     problems += 1
#                 for p in paths:
#                     used_files[p].add(name)
#                     filepaths.append(p)

#             if "filenames" in filespec:
#                 if not filespec["filenames"]:
#                     print(f"Empty list of filenames in {name}")
#                 for path in filespec["filenames"]:
#                     fullpath = SOUNDS_DIR / path
#                     if not fullpath.exists():
#                         print(f"Non-existant path in list in {name}: {path}")
#                         problems += 1
#                     used_files[fullpath].add(name)
#                     filepaths.append(fullpath)

#             if "filename" in filespec:
#                 # sounds_dir / example.opus
#                 path = SOUNDS_DIR / filespec["filename"]
#                 if not path.exists():
#                     print(f"Non-existant path in {name}: {filespec['filename']}")
#                     problems += 1
#                 used_files[path].add(name)
#                 filepaths.append(path)

#         for alias in data.get("aliases", []):
#             used_names[str(alias)].add(name)

#         if not filepaths:
#             print(f"No files for {name}")
#             problems += 1

#     return problems, used_names, used_files


# def check_used_names(used_names: Mapping[str, Set[str]]) -> int:
#     problems: int = 0

#     for name, uses in used_names.items():
#         if len(uses) < 2:
#             continue
#         prefix = "Name" if name in uses else "Alias"
#         print(f"{prefix} {name} is reused in " + ", ".join(uses-{name}))
#         problems += 1

#     return problems


def check_used_files(used_files: Mapping[Path, Set[Any]]) -> int:
    problems: int = 0

    for path, folders, files in os.walk(SOUNDS_DIR / "audio"):
        path = Path(path)
        for fol in list(folders):  # (copy list to avoid RuntimeError(iterator changed size))
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
    # problems, used_names, used_files = parse_file()
    # problems += check_used_names(used_names)
    # problems += check_used_files(used_files)

    sounds = parse_sounds()
    check_used_files(verbose.files)
    parse_commands(sounds)
    parse_slash_commands(sounds)

    problemcount = len(verbose.problems)
    if problemcount > 1:
        raise Exception(f"{problemcount} issues found.")
    elif problemcount == 1:
        raise Exception("1 issue found.")
    else:
        print("All good :)")
