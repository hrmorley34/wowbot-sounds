from collections import defaultdict
import json
import os
from pathlib import Path
from typing import (
    Any,
    DefaultDict,
    Generator,
    Iterable,
    Mapping,
    Optional,
    Set,
    Tuple,
    Union,
)

from pydantic import ValidationError, parse_obj_as

from lib.command import COMMANDS_JSON, CommandName
from lib.slash import (
    COMMANDS_SLASH_JSON,
    AnySlashCommand,
    SlashCommand,
    SlashOption,
    SlashOptionCommand,
    SlashSubcommand,
    SlashName,
)
from lib.sound import SOUNDS_JSON, Sound, SoundName

# from lib.verbose import verbose


SOUNDS_DIR = Path(".")
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


def parse_sounds() -> SOUNDS_JSON:
    with open(SOUNDS_FILE, "r") as file:  # non-existant file will raise here
        sounds_json = json.load(file)  # invalid json will raise here

    return parse_obj_as(SOUNDS_JSON, sounds_json)


def get_used_files(sounds: SOUNDS_JSON) -> Mapping[Path, Set[SoundName]]:
    uses: defaultdict[Path, set[SoundName]] = defaultdict(set)

    for name, sound in sounds.items():
        for fileset in sound:
            for file in fileset.resolve_filenames(SOUNDS_DIR):
                uses[file].add(name)

    return uses


def parse_commands():  # sounds: SoundDict):
    with open(COMMANDS_FILE, "r") as file:  # non-existant file will raise here
        commands_json = json.load(file)  # invalid json will raise here

    return parse_obj_as(COMMANDS_JSON, commands_json)


def parse_slash_commands():  # sounds: SoundDict):
    # non-existant file will raise here
    with open(COMMANDS_SLASH_FILE, "r") as file:
        # invalid json will raise here
        slash_commands_json: COMMANDS_SLASH_JSON = json.load(file)

    return parse_obj_as(COMMANDS_SLASH_JSON, slash_commands_json)


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


def get_used_sounds_in_commands(
    commands: COMMANDS_JSON,
) -> Mapping[SoundName, Set[CommandName]]:
    uses: defaultdict[SoundName, Set[CommandName]] = defaultdict(set)

    for name, command in commands.items():
        uses[command.sound].add(name)

    return uses


def get_used_sounds_in_slash(
    slashes: COMMANDS_SLASH_JSON,
) -> Mapping[SoundName, Set[Tuple[Union[SlashName, SlashOption], ...]]]:
    uses: DefaultDict[
        SoundName, Set[Tuple[Union[SlashName, SlashOption], ...]]
    ] = defaultdict(set)
    _get_used_sounds_in_slashes(slashes.values(), uses=uses)
    return uses


def _get_used_sounds_in_slashes(
    slashes: Iterable[AnySlashCommand],
    *,
    uses: DefaultDict[SoundName, Set[Tuple[Union[SlashName, SlashOption], ...]]],
    prefix: Tuple[SlashName, ...] = (),
) -> None:
    for slash in slashes:
        if isinstance(slash, SlashCommand):
            uses[slash.sound].add((*prefix, slash.name))
        elif isinstance(slash, SlashOptionCommand):
            for optname, option in slash.options.items():
                uses[option.sound].add((*prefix, slash.name, optname))
        else:
            assert isinstance(slash, SlashSubcommand)
            _get_used_sounds_in_slashes(
                slash.subcommands.values(), prefix=(*prefix, slash.name), uses=uses
            )


def _unused_sounds(
    sounds: Mapping[SoundName, Sound], used_sounds: Mapping[SoundName, Set[Any]]
) -> Generator[SoundName, None, None]:
    for sound in sounds.keys():
        if not used_sounds.get(sound):
            yield sound


def check_used_sounds(
    sounds: SOUNDS_JSON,
    command_sounds: Optional[Mapping[SoundName, Set[Any]]],
    slash_sounds: Optional[Mapping[SoundName, Set[Any]]],
) -> bool:
    checks: Set[SoundName] = set()
    if command_sounds is not None:
        checks |= set(_unused_sounds(sounds, command_sounds))
    if slash_sounds is not None:
        checks |= set(_unused_sounds(sounds, slash_sounds))

    for sound in checks:
        if command_sounds is None:
            command_notin = None
        else:
            command_notin = sound not in command_sounds
        if slash_sounds is None:
            slash_notin = None
        else:
            slash_notin = sound not in slash_sounds

        if command_notin and slash_notin:
            print(f"Sound {sound!r} is not referenced")
        elif command_notin:
            if slash_notin is None:
                print(f"Sound {sound!r} is not referenced in commands")
            else:
                print(f"Sound {sound!r} is not referenced in commands (slash only)")
        elif slash_notin:
            if command_notin is None:
                print(f"Sound {sound!r} is not referenced in slash commands")
            else:
                print(
                    f"Sound {sound!r} is not referenced in slash commands (commands only)"
                )

    command_missing = {s for s in command_sounds or {} if s not in sounds}
    slash_missing = {s for s in slash_sounds or {} if s not in sounds}
    for sound in command_missing | slash_missing:
        print(f"Sound {sound!r} does not exist")

    return len(command_missing | slash_missing) != 0


if __name__ == "__main__":
    errored = False

    sounds = parse_sounds()
    check_used_files(get_used_files(sounds))

    commands = None
    commands_used_sounds = None
    try:
        commands = parse_commands()
    except ValidationError as err:
        print(err)
    else:
        commands_used_sounds = get_used_sounds_in_commands(commands)

    slashes = None
    slashes_used_sounds = None
    try:
        slashes = parse_slash_commands()
    except ValidationError as err:
        print(err)
    else:
        slashes_used_sounds = get_used_sounds_in_slash(slashes)

    errored |= check_used_sounds(
        sounds,
        commands_used_sounds,
        slashes_used_sounds,
    )

    if errored:
        exit(1)
    else:
        print("All good :)")
