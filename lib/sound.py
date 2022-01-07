from pathlib import Path
import random
from typing import Dict, List, Sequence

from .problem import Problem
from .types import SoundDef, SoundName
from .verbose import verbose as _v


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

        arrays: List[List[Path]] = []
        weights: List[int] = []
        for fd in data:
            filenames: List[Path] = []
            if "glob" in fd:
                globdata = tuple(rootdir.glob(fd["glob"]))
                if not globdata:
                    _v.problems.append(
                        Problem(
                            f"No files for glob: {fd['glob']!r}",
                            context=f"Sound {name!r}",
                        )
                    )
                filenames.extend(globdata)
            if "filenames" in fd:
                fns = fd["filenames"]
                if not fns:
                    _v.problems.append(
                        Problem("Empty list of filenames", context=f"Sound {name!r}")
                    )
                for ofn, fn in zip(fns, map(rootdir.joinpath, fns)):
                    if not fn.exists():
                        _v.problems.append(
                            Problem(
                                f"File {ofn!r} does not exist",
                                context=f"Sound {name!r}; filenames {fns!r}",
                            )
                        )
                    else:
                        filenames.append(fn)
            if "filename" in fd:
                ofn = fd["filename"]
                fn = rootdir / ofn
                if not fn.exists():
                    _v.problems.append(
                        Problem(
                            f"File {ofn!r} does not exist", context=f"Sound {name!r}"
                        )
                    )
                else:
                    filenames.append(fn)

            if len(filenames) >= 1:
                try:
                    weight = int(fd.get("weight", 1))
                except ValueError:
                    _v.problems.append(
                        Problem(
                            f"Invalid weight: {fd.get('weight')!r}",
                            context=f"Sound {name!r}",
                        )
                    )
                    continue
                if weight <= 0:
                    _v.problems.append(
                        Problem(
                            f"Invalid weight: {fd.get('weight')!r}",
                            context=f"Sound {name!r}",
                        )
                    )
                    continue
                arrays.append(filenames)
                weights.append(weight)
                for f in filenames:
                    _v.files[f].add(self.name)
            else:
                _v.problems.append(
                    Problem("No sounds supplied", context=f"Sound {name!r}")
                )

        self.sound_arrays = arrays
        self.sound_weights = weights

        return self

    def get_filename(self) -> Path:
        ls = random.choices(self.sound_arrays, self.sound_weights)[0]
        if len(ls):
            return random.choice(ls)
        else:
            raise Exception("Missing filenames")


SoundDict = Dict[SoundName, "Sound"]
