from abc import abstractmethod
from pathlib import Path
from pydantic import PositiveInt, conlist
from typing import Dict, Iterable, List, NewType, Union

from .types import BaseModel


SoundName = NewType("SoundName", str)


class BaseSoundPath(BaseModel):
    weight: PositiveInt = 1

    @abstractmethod
    def resolve_filenames(self, root: Path = Path(".")) -> Iterable[Path]:
        pass


class GlobSoundPath(BaseSoundPath):
    glob: str

    def resolve_filenames(self, root: Path = Path(".")) -> Iterable[Path]:
        return root.glob(self.glob)


NonEmptyStrList = conlist(str, min_items=1)


class FilenamesSoundPath(BaseSoundPath):
    filenames: NonEmptyStrList

    def resolve_filenames(self, root: Path = Path(".")) -> Iterable[Path]:
        return map(root.joinpath, self.filenames)


class FilenameSoundPath(BaseSoundPath):
    filename: str

    def resolve_filenames(self, root: Path = Path(".")) -> Iterable[Path]:
        return (root / self.filename,)


SoundPath = Union[GlobSoundPath, FilenamesSoundPath, FilenameSoundPath]
Sound = List[SoundPath]


class SoundRequiredMixin(BaseModel):
    sound: SoundName


SOUNDS_JSON = Dict[SoundName, Sound]
