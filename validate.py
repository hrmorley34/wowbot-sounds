import json
import os
from pathlib import Path
from typing import Any, Dict, Generator, Mapping, Optional, Set, Tuple

from lib.command import Command
from lib.slash import BaseSlashCommand, SlashCommand, SlashOptionCommand
from lib.problem import Problem
from lib.sound import Sound, SoundDict
from lib.types import (
    SOUNDS_JSON,
    COMMANDS_JSON,
    COMMANDS_SLASH_JSON,
    CommandCommonName,
    CommandName,
    SlashGroup,
    SlashName,
    SoundName,
)
from lib.verbose import verbose


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
            verbose.problems.append(
                Problem(f"Reuse of name {name!r}", context=f"Command {name!r}")
            )
        aliases.add(name)

        try:
            cmd = Command(name, data, sounds=sounds)
        except KeyError as e:
            verbose.problems.append(
                Problem(f"Missing key {e.args[0]}", context=f"Command {name!r}")
            )
            continue
        # except Exception as e:
        #     verbose.problems.append(Problem(f"{e!r}", context=f"Command {name!r}"))
        #     continue
        else:
            commands[name] = cmd
            verbose.commandsounds[cmd.sound.name].add(name)
            for a in cmd.aliases:
                if a in aliases:
                    verbose.problems.append(
                        Problem(f"Reuse of alias {a!r}", context=f"Command {name!r}")
                    )
                aliases.add(a)


def parse_slash_commands(sounds: SoundDict):
    # non-existant file will raise here
    with open(COMMANDS_SLASH_FILE, "r") as file:
        # invalid json will raise here
        slash_commands_json: COMMANDS_SLASH_JSON = json.load(file)

    commands: Dict[Tuple[Optional[SlashGroup], SlashName], BaseSlashCommand] = dict()

    for group, cmds in slash_commands_json.items():
        if not group:
            group = None
        for name, data in cmds.items():
            try:
                command = BaseSlashCommand(group, name, data, sounds=sounds)
            except KeyError as e:
                verbose.problems.append(
                    Problem(
                        f"Missing key {e.args[0]}",
                        context=f"Slashcommand {group!r}.{name!r}",
                    )
                )
                continue
            # except Exception as e:
            #     verbose.problems.append(Problem(f"{e!r}", context=f"Slashcommand {group!r}.{name!r}"))
            #     continue
            else:
                commands[group, name] = command
                if isinstance(command, SlashCommand):
                    verbose.slashsounds[command.sound.name].add(
                        (command.group, command.name)
                    )
                elif isinstance(command, SlashOptionCommand):
                    for sound in command.options.values():
                        verbose.slashsounds[sound.name].add(
                            (command.group, command.name)
                        )
                    if command.default not in command.options:
                        verbose.problems.append(
                            Problem(
                                f"Default sound {command.default!r}",
                                context=f"Slashcommand {group!r}.{name!r}",
                            )
                        )


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
    sounds: SoundDict, used_sounds: Mapping[SoundName, Set[Any]]
) -> Generator[SoundName, None, None]:
    for sound in sounds.keys():
        if not used_sounds.get(sound):
            yield sound


def check_used_sounds(
    sounds: SoundDict,
    command_sounds: Mapping[SoundName, Set[Any]],
    slash_sounds: Mapping[SoundName, Set[Any]],
):
    command_unused = set(_unused_sounds(sounds, command_sounds))
    slash_unused = set(_unused_sounds(sounds, slash_sounds))
    for sound in command_unused | slash_unused:
        command_notin = sound not in command_sounds
        slash_notin = sound not in slash_sounds
        if command_notin and slash_notin:
            print(f"Sound {sound!r} is not referenced")
        elif command_notin:
            print(f"Sound {sound!r} is not referenced in commands (slash only)")
        elif slash_notin:
            print(
                f"Sound {sound!r} is not referenced in slash commands (commands only)"
            )


if __name__ == "__main__":
    sounds = parse_sounds()
    check_used_files(verbose.files)
    parse_commands(sounds)
    parse_slash_commands(sounds)
    check_used_sounds(sounds, verbose.commandsounds, verbose.slashsounds)

    problemcount = len(verbose.problems)
    if problemcount > 1:
        raise Exception(f"{problemcount} issues found.")
    elif problemcount == 1:
        raise Exception("1 issue found.")
    else:
        print("All good :)")
