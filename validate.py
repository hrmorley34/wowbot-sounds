import json
import os
from pathlib import Path
import sys
from typing import Any, Generator, Mapping, Set

from lib.command import Command, CommandTracker
from lib.problem import Problem
from lib.slash import SlashCommand, SlashTracker
from lib.sound import Sound, SoundDict, SoundTracker
from lib.types import SOUNDS_JSON, COMMANDS_JSON, COMMANDS_SLASH_JSON
from lib.verbose import set_verbose


SOUNDS_DIR = Path(sys.argv[0]).parent
SOUNDS_FILE = SOUNDS_DIR / "sounds.json"
COMMANDS_FILE = SOUNDS_DIR / "commands.json"
COMMANDS_SLASH_FILE = SOUNDS_DIR / "commands_slash.json"
AUDIO_EXTENSIONS = (
    ".aac",
    ".flac",
    ".m4a",
    ".mka",
    ".mp3",
    ".oga",
    ".ogg",
    ".opus",
    ".spx",
    ".wav",
)


set_verbose(True)


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

    Command.from_json(commands_json, sounds=sounds)


def parse_slash_commands(sounds: SoundDict):
    # non-existant file will raise here
    with open(COMMANDS_SLASH_FILE, "r") as file:
        # invalid json will raise here
        slash_commands_json: COMMANDS_SLASH_JSON = json.load(file)

    SlashCommand.from_json(slash_commands_json, sounds=sounds)


def check_used_files(used_files: Mapping[Path, Set[Any]]):
    for path, folders, files in os.walk(SOUNDS_DIR / "audio"):
        path = Path(path)
        # (copy list to avoid RuntimeError(iterator changed size))
        for fol in list(folders):
            if fol[0] == ".":  # ignore folders beginning with "." (eg. .github)
                del folders[folders.index(fol)]
        for fil in files:
            if fil[0] == ".":  # ignore files beginning with "." (eg. .gitignore)
                continue
            if not fil.endswith(AUDIO_EXTENSIONS):
                continue
            if not used_files.get(path / fil):
                print(f"File {path / fil} is not referenced")


def _unused_sounds(
    sounds: SoundDict, used_sounds: Mapping[Sound, Set[Any]]
) -> Generator[Sound, None, None]:
    for sound in sounds.values():
        if not used_sounds.get(sound):
            yield sound


def check_used_sounds(
    sounds: SoundDict,
    command_sounds: Mapping[Sound, Set[Any]],
    slash_sounds: Mapping[Sound, Set[Any]],
):
    command_unused = set(_unused_sounds(sounds, command_sounds))
    slash_unused = set(_unused_sounds(sounds, slash_sounds))
    for sound in command_unused | slash_unused:
        command_notin = sound not in command_sounds
        slash_notin = sound not in slash_sounds
        if command_notin and slash_notin:
            print(f"Sound {sound.name} is not referenced")
        elif command_notin:
            print(f"Sound {sound.name} is not referenced in commands (slash only)")
        elif slash_notin:
            print(
                f"Sound {sound.name} is not referenced in slash commands (commands only)"
            )


if __name__ == "__main__":
    sounds = parse_sounds()
    check_used_files(SoundTracker.files)
    parse_commands(sounds)
    parse_slash_commands(sounds)
    check_used_sounds(sounds, CommandTracker.commandsounds, SlashTracker.slashsounds)

    problemcount = len(Problem.get_problems())
    if problemcount > 1:
        raise Exception(f"{problemcount} issues found.")
    elif problemcount == 1:
        raise Exception("1 issue found.")
    else:
        print("All good :)")
