import dataclasses
import json
import logging as log
import numpy as np
import numpy.typing as npt
import pathlib
import typing as typ

from dkdisc.utils.encoders import DataclassJSONEncoder


@dataclasses.dataclass
class ExpirementOutputData:
    densities: typ.Optional[npt.NDArray]
    bm_paths: typ.Optional[npt.NDArray]

    @classmethod
    def from_json(cls, json_data):
        if "densities" in json_data:
            densities = np.asarray(json_data["densities"])
        else:
            densities = None

        if "bm_paths" in json_data:
            bm_paths = np.asarray(json_data["bm_paths"])
        else:
            bm_paths = None

        return ExpirementOutputData(densities=densities, bm_paths=bm_paths)


@dataclasses.dataclass
class SavedOutputConfig:
    output_name: str
    output_dir: typ.Union[str, pathlib.Path]
    keep_all_steps: bool = dataclasses.field(default=False)
    keep_bm_paths: bool = dataclasses.field(default=False)

    def __post_init__(self):
        if isinstance(self.output_dir, str):
            self.output_dir = pathlib.Path(self.output_dir)

        if self.output_dir.exists() and not self.output_dir.is_dir():
            raise RuntimeError(
                f"{self.output_dir.absolute} should be a " + "directory, not a file."
            )
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_output(
        self,
        densities: typ.Optional[npt.NDArray] = None,
        bm_paths: typ.Optional[npt.NDArray] = None,
        prefix: typ.Optional[str] = None,
    ):

        assert isinstance(self.output_dir, pathlib.Path)
        if not prefix:
            prefix = ""
        output_path = self.output_dir.joinpath(prefix + self.output_name)
        if not str(output_path.absolute()).lower().endswith("json"):
            output_path = output_path.with_suffix(".json")

        if densities is None and bm_paths is None:
            raise RuntimeError("write_output(...) method passed empty data")

        results = ExpirementOutputData(densities=densities, bm_paths=bm_paths)

        output_path.touch(exist_ok=True)
        with output_path.open(mode="w") as output_file:
            output_file.write(json.dumps(results, cls=DataclassJSONEncoder))

        log.debug(f"Wrote expirement output to {output_path.absolute}")

    @classmethod
    def from_json(cls, json_data):
        return SavedOutputConfig(**json_data)
