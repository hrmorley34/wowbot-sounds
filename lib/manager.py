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

from .command import COMMANDS_JSON, CommandName
from .slash import (
    COMMANDS_SLASH_JSON,
    AnySlashCommand,
    SlashCommand,
    SlashOption,
    SlashOptionCommand,
    SlashSubcommand,
    SlashName,
)
from .sound import SOUNDS_JSON, Sound, SoundName


def print_validation_error(err: ValidationError, pad: str = "") -> None:
    for e in err.errors():
        print(
            pad
            + " -> ".join(str(loc) for loc in e["loc"] if loc != "__root__")
            + f"\n{pad}  {e['msg']!s}"
        )


class WowbotSounds:
    root_dir: Path
    sounds_file: Union[str, Path] = "sounds.json"
    commands_file: Union[str, Path] = "commands.json"
    slashes_file: Union[str, Path] = "commands_slash.json"

    audio_extensions = (
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

    def __init__(self, folder: Union[str, Path]):
        self.root_dir = Path(folder)

    def parse_sounds(self) -> SOUNDS_JSON:
        with open(
            self.root_dir / self.sounds_file, "r"
        ) as file:  # non-existant file will raise here
            sounds_json = json.load(file)  # invalid json will raise here

        return parse_obj_as(SOUNDS_JSON, sounds_json)

    def get_used_files(self, sounds: SOUNDS_JSON) -> Mapping[Path, Set[SoundName]]:
        uses: DefaultDict[Path, Set[SoundName]] = defaultdict(set)

        for name, sound in sounds.items():
            for fileset in sound:
                for file in fileset.resolve_filenames(self.root_dir):
                    uses[file].add(name)

        return uses

    def check_used_files(self, used_files: Mapping[Path, Set[Any]]) -> None:
        for path, folders, files in os.walk(self.root_dir / "audio"):
            path = Path(path)
            # (copy list to avoid RuntimeError(iterator changed size))
            for fol in list(folders):
                if fol[0] == ".":  # ignore folders beginning with "." (eg. .github)
                    del folders[folders.index(fol)]
            for fil in files:
                if fil[0] == ".":  # ignore files beginning with "." (eg. .gitignore)
                    continue
                if not fil.endswith(self.audio_extensions):
                    continue
                if not used_files.get(path / fil):
                    print(f"File {path / fil} is not referenced")

    def check_missing_files(self, used_files: Mapping[Path, Set[Any]]) -> None:
        missing = False
        for f in used_files:
            if not f.exists():
                missing = True
                print(f"File {f} does not exist")
        if missing:
            raise ValueError("Missing files")

    def parse_commands(self) -> COMMANDS_JSON:
        with open(
            self.root_dir / self.commands_file, "r"
        ) as file:  # non-existant file will raise here
            commands_json = json.load(file)  # invalid json will raise here

        return parse_obj_as(COMMANDS_JSON, commands_json)

    def parse_slashes(self) -> COMMANDS_SLASH_JSON:
        # non-existant file will raise here
        with open(self.root_dir / self.slashes_file, "r") as file:
            # invalid json will raise here
            slash_commands_json = json.load(file)

        return parse_obj_as(COMMANDS_SLASH_JSON, slash_commands_json)

    def get_used_sounds_in_commands(
        self,
        commands: COMMANDS_JSON,
    ) -> Mapping[SoundName, Set[CommandName]]:
        uses: DefaultDict[SoundName, Set[CommandName]] = defaultdict(set)

        for name, command in commands.items():
            uses[command.sound].add(name)

        return uses

    def get_used_sounds_in_slashes(
        self,
        slashes: COMMANDS_SLASH_JSON,
    ) -> Mapping[SoundName, Set[Tuple[Union[SlashName, SlashOption], ...]]]:
        uses: DefaultDict[
            SoundName, Set[Tuple[Union[SlashName, SlashOption], ...]]
        ] = defaultdict(set)
        self._recursive_get_used_sounds_in_slashes(slashes.values(), uses=uses)
        return uses

    def _recursive_get_used_sounds_in_slashes(
        self,
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
                self._recursive_get_used_sounds_in_slashes(
                    slash.subcommands.values(), prefix=(*prefix, slash.name), uses=uses
                )

    @staticmethod
    def _unused_sounds(
        sounds: Mapping[SoundName, Sound],
        used_sounds: Mapping[SoundName, Set[Any]],
    ) -> Generator[SoundName, None, None]:
        for sound in sounds.keys():
            if not used_sounds.get(sound):
                yield sound

    def check_used_sounds(
        self,
        sounds: SOUNDS_JSON,
        command_sounds: Optional[Mapping[SoundName, Set[Any]]],
        slash_sounds: Optional[Mapping[SoundName, Set[Any]]],
    ) -> None:
        checks: Set[SoundName] = set()
        if command_sounds is not None:
            checks |= set(self._unused_sounds(sounds, command_sounds))
        if slash_sounds is not None:
            checks |= set(self._unused_sounds(sounds, slash_sounds))

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

    def check_sounds_exist(
        self,
        sounds: SOUNDS_JSON,
        command_sounds: Optional[Mapping[SoundName, Set[Any]]],
        slash_sounds: Optional[Mapping[SoundName, Set[Any]]],
    ) -> None:
        command_missing = {s for s in command_sounds or {} if s not in sounds}
        slash_missing = {s for s in slash_sounds or {} if s not in sounds}
        for sound in command_missing | slash_missing:
            print(f"Sound {sound!r} does not exist")

        if len(command_missing | slash_missing) != 0:
            raise ValueError("Some sounds do not exist")

    def main(self) -> bool:
        errored = False

        sounds = None
        try:
            sounds = self.parse_sounds()
        except json.JSONDecodeError as err:
            print(f"JSONDecodeError in {self.sounds_file!s}: {err!s}")
            errored = True
        except ValidationError as err:
            print(f"Error in {self.sounds_file!s}:")
            print_validation_error(err, pad="  ")
            errored = True
        else:
            used_sounds = self.get_used_files(sounds)
            self.check_used_files(used_sounds)
            try:
                self.check_missing_files(used_sounds)
            except ValueError:
                errored = True

            commands = None
            commands_used_sounds = None
            try:
                commands = self.parse_commands()
            except json.JSONDecodeError as err:
                print(f"JSONDecodeError in {self.commands_file!s}: {err!s}")
                errored = True
            except ValidationError as err:
                print(f"Error in {self.commands_file!s}:")
                print_validation_error(err, pad="  ")
                errored = True
            else:
                commands_used_sounds = self.get_used_sounds_in_commands(commands)

            slashes = None
            slashes_used_sounds = None
            try:
                slashes = self.parse_slashes()
            except json.JSONDecodeError as err:
                print(f"JSONDecodeError in {self.slashes_file!s}: {err!s}")
                errored = True
            except ValidationError as err:
                print(f"Error in {self.slashes_file!s}")
                print_validation_error(err, pad="  ")
                errored = True
            else:
                slashes_used_sounds = self.get_used_sounds_in_slashes(slashes)

            self.check_used_sounds(sounds, commands_used_sounds, slashes_used_sounds)
            try:
                self.check_sounds_exist(
                    sounds, commands_used_sounds, slashes_used_sounds
                )
            except ValueError:
                errored = True

        return errored
