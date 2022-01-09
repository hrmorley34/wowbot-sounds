__all__ = [
    "SoundTracker",
    "Sound",
    "SoundDict",
    "SoundT",
    "SoundTDict",
]

from collections import defaultdict
from contextvars import ContextVar
from pathlib import Path
import random
from typing import DefaultDict, Dict, List, Optional, Sequence, Set, TypeVar

from .problem import Problem
from .types import SoundDef, SoundName
from .utils import DefaultContextVarProperty
from .verbose import context


_Files = DefaultDict[Path, Set["Sound"]]
_files: ContextVar[Optional[_Files]] = ContextVar("files")


class _SoundTrackers:
    files = DefaultContextVarProperty(_files, lambda: defaultdict(set))


SoundTracker = _SoundTrackers()


class Sound:
    _rootdir: Path

    name: SoundName

    # Random sounds and weights
    sound_arrays: Sequence[Sequence[Path]]
    sound_weights: Sequence[int]

    def __init__(self, rootdir: Path, name: SoundName, data: SoundDef):
        self._rootdir = rootdir
        self.name = name

        arrays: List[List[Path]] = []
        weights: List[int] = []
        for fd in data:
            filenames: List[Path] = []
            if "glob" in fd:
                filenames.extend(rootdir.glob(fd["glob"]))
            if "filenames" in fd:
                filenames.extend(map(rootdir.joinpath, fd["filenames"]))
            if "filename" in fd:
                filenames.append(rootdir / fd["filename"])

            if len(filenames) >= 1:
                arrays.append(filenames)
                weights.append(fd.get("weight", 1))

        self.sound_arrays = arrays
        self.sound_weights = weights

    @classmethod
    def init_verbose(cls, rootdir: Path, name: SoundName, data: SoundDef) -> "Sound":
        self = cls.__new__(cls)

        self._rootdir = rootdir
        self.name = name

        with context(self):
            if not data:
                Problem("No sounds supplied").add()

            arrays: List[List[Path]] = []
            weights: List[int] = []
            for fd in data:
                filenames: List[Path] = []
                if "glob" in fd:
                    globdata = tuple(rootdir.glob(fd["glob"]))
                    if not globdata:
                        Problem(f"No files for glob: {fd['glob']!r}").add()
                    filenames.extend(globdata)
                if "filenames" in fd:
                    fns = fd["filenames"]
                    with context(f"Filenames {fns!r}"):
                        if not fns:
                            Problem("Empty list of filenames").add()
                        for ofn, fn in zip(fns, map(rootdir.joinpath, fns)):
                            if not fn.exists():
                                Problem(f"File {ofn!r} does not exist").add()
                            else:
                                filenames.append(fn)
                if "filename" in fd:
                    ofn = fd["filename"]
                    fn = rootdir / ofn
                    if not fn.exists():
                        Problem(f"File {ofn!r} does not exist").add()
                    else:
                        filenames.append(fn)

                if len(filenames) >= 1:
                    try:
                        weight = int(fd.get("weight", 1))
                    except ValueError:
                        Problem(f"Invalid weight: {fd.get('weight')!r}").add()
                        continue
                    if weight <= 0:
                        Problem(f"Invalid weight: {fd.get('weight')!r}").add()
                        continue
                    arrays.append(filenames)
                    weights.append(weight)
                    for f in filenames:
                        SoundTracker.files[f].add(self)
                else:
                    Problem("No sounds supplied").add()

            self.sound_arrays = arrays
            self.sound_weights = weights

            return self

    def __hash__(self) -> int:
        return hash((type(self), self.name))

    def __repr__(self) -> str:
        return "<" + type(self).__name__ + f" {self.name}>"

    def get_filename(self) -> Path:
        ls = random.choices(self.sound_arrays, self.sound_weights)[0]
        if len(ls):
            return random.choice(ls)
        else:
            raise Exception("Missing filenames")


SoundDict = Dict[SoundName, Sound]

SoundT = TypeVar("SoundT", bound=Sound)
SoundTDict = Dict[SoundName, SoundT]
