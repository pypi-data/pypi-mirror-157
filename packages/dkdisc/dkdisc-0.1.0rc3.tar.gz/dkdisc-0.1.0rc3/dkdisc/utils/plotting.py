import abc
import dataclasses
import enum
import json
import logging as log
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pathlib
import typing as typ

from dkdisc.finitediff.grid import Grid


class FigureType(str, enum.Enum):
    FIGURE_1D_PLOT = "figure_1d_plot"


class FigureConfig:
    figure_type: FigureType

    def plot(self, *args, **kwargs):
        raise NotImplementedError(
            "plot(...) expected to be implmemented by sublcasses"
        )

    @classmethod
    def from_json(cls, json_data):
        figure_type = json_data.pop("figure_type", None)
        if figure_type == FigureType.FIGURE_1D_PLOT:
            density_configs = json_data.pop("densities_to_plot", [])
            densities_to_plot = []
            for density_to_plot in density_configs:
                densities_to_plot.append(
                    Figure1dPlotConfig.DensityStepPlot(**density_to_plot)
                )
            return Figure1dPlotConfig(
                densities_to_plot=densities_to_plot, **json_data
            )
        else:
            raise ValueError(f"Figure type {figure_type} is currently unsupported")


@dataclasses.dataclass
class Figure1dPlotConfig(FigureConfig):
    figure_name: str
    output_dir: typ.Union[str, pathlib.Path]
    create_legend: bool
    x_axis_label: str
    y_axis_label: str

    def __post_init__(self):
        if isinstance(self.output_dir, str):
            self.output_dir = pathlib.Path(self.output_dir)

        if self.output_dir.exists() and not self.output_dir.is_dir():
            raise RuntimeError(
                f"{self.output_dir.absolute} should be a " + "directory, not a file."
            )
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        # TODO: Add more advanced plotting as needed
        self.figure = plt.figure()

    @dataclasses.dataclass
    class DensityStepPlot:
        step_number: int
        color: str
        label: str
        transparency: float = dataclasses.field(default=1.0)
        linestyle: str = dataclasses.field(default="solid")
        marker: str = dataclasses.field(default=".")

    densities_to_plot: typ.Collection[DensityStepPlot]

    def plot(
        self,
        grid: typ.Union[Grid, npt.NDArray],
        densities: npt.NDArray,
        prefix: typ.Optional[str] = None,
    ):
        ax = self.figure.subplots()

        if isinstance(grid, Grid):
            grid = grid.points

        ax.set_xlim(left=np.min(grid), right=np.max(grid))
        ax.set_ylim(bottom=np.min(densities), top=np.max(densities))
        ax.set_xlabel(self.x_axis_label)
        ax.set_ylabel(self.y_axis_label)

        for density_plot in self.densities_to_plot:
            ax.plot(
                grid,
                densities[density_plot.step_number, :],
                color=density_plot.color,
                label=density_plot.label,
                alpha=density_plot.transparency,
                linestyle=density_plot.linestyle,
                marker=density_plot.marker,
            )

        if self.create_legend:
            self.figure.legend()

        assert isinstance(self.output_dir, pathlib.Path)
        if not prefix:
            prefix = ""

        figure_path = self.output_dir.joinpath(prefix + self.figure_name)
        if not str(figure_path.absolute()).lower().endswith("pdf"):
            figure_path = figure_path.with_suffix(".pdf")

        self.figure.savefig(figure_path)
        log.debug(f"Saved figure {self.figure_name} at {figure_path.absolute}")
