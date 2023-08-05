import dataclasses
import logging as log
import numpy as np
import numpy.typing as npt
import typing as typ
import multiprocessing.pool as pl

from dkdisc.utils.output import SavedOutputConfig
from dkdisc.utils.plotting import FigureConfig
from dkdisc.finitediff.grid import Grid
from dkdisc.finitediff.linear import LinearFiniteDiffFunctionParams
from dkdisc.finitediff.linear import LinearSolverHints
from dkdisc.finitediff.linear import LinearFiniteDiffSolver
from dkdisc.finitediff.nonlinear import NonlinearFiniteDiffFunctionParams
from dkdisc.finitediff.nonlinear import NonlinearSolverTolerences
from dkdisc.finitediff.nonlinear import NonlinearFiniteDiffSolver


@dataclasses.dataclass
class ExperimentConfig:
    num_simulations: int
    num_threads: int
    figures: typ.Collection[FigureConfig]
    output: SavedOutputConfig
    initial_density: npt.NDArray
    linear_finitediff_params: typ.Optional[LinearFiniteDiffFunctionParams]
    nonlinear_finitediff_params: typ.Optional[NonlinearFiniteDiffFunctionParams]

    def __post_init__(self):
        if (
            not self.linear_finitediff_params
            and not self.nonlinear_finitediff_params
        ):
            raise ValueError(
                "ExperimentConfig needs either a linear_finitediff_params or a "
                + "nonlinear_finitediff_params."
            )

    @classmethod
    def from_json(cls, json_data):
        params_available = [k for k in json_data.keys() if k.endswith("_params")]

        if len(params_available) != 1:
            raise ValueError(
                "Can only have one '_params' element in ExperimentConfig"
            )
        params = params_available[0]

        kwargs = {
            "num_simulations": json_data["num_simulations"],
            "num_threads": json_data["num_threads"],
            "initial_density": np.asarray(json_data["initial_density"]),
            "output": SavedOutputConfig.from_json(json_data["output"]),
            "figures": [],
        }

        for plot_def in json_data["figures"]:
            kwargs["figures"].append(FigureConfig.from_json(plot_def))

        if "finitediff" in params:
            num_time_steps = json_data[params]["num_time_steps"]
            time_step = json_data[params]["time_step"]
            grid = Grid.from_json(json_data[params]["grid"])
            first_step_alpha = json_data[params]["first_step_alpha"]

            def drift_func(density: npt.NDArray) -> npt.NDArray:
                return np.matmul(grid.get_laplacian(), density)

            def drift_noise(
                density: npt.NDArray, dWiener: npt.NDArray
            ) -> npt.NDArray:
                pos_root_value = np.sqrt(np.maximum(density, 0))
                distorted_value = np.multiply(pos_root_value, dWiener)
                return np.gradient(distorted_value)

            if params.startswith("linear"):
                if "first_step_matrix" in json_data[params]:
                    first_step_matrix = np.asarray(
                        json_data[params]["first_step_matrix"]
                    )
                else:
                    first_step_matrix = grid.get_identity() - (
                        0.25 * time_step * grid.get_laplacian()
                    )
                if "further_steps_matrix" in json_data[params]:
                    further_steps_matrix = np.asarray(
                        json_data[params]["further_steps_matrix"]
                    )
                else:
                    further_steps_matrix = grid.get_identity() - (
                        (2.0 * time_step / 3.0) * grid.get_laplacian()
                    )
                linear_solver_hints = LinearSolverHints.from_json(
                    json_data[params]["linear_solver_hints"]
                )
                kwargs["linear_finitediff_params"] = LinearFiniteDiffFunctionParams(
                    num_time_steps=num_time_steps,
                    time_step=time_step,
                    grid=grid,
                    drift_func=drift_func,
                    drift_noise=drift_noise,
                    first_step_alpha=first_step_alpha,
                    first_step_matrix=first_step_matrix,
                    further_steps_matrix=further_steps_matrix,
                    linear_solver_hints=linear_solver_hints,
                )
                kwargs["nonlinear_finitediff_params"] = None

            elif params.startswith("nonlinear"):

                kwargs[
                    "nonlinear_finitediff_params"
                ] = NonlinearFiniteDiffFunctionParams(
                    num_time_steps=num_time_steps,
                    time_step=time_step,
                    grid=grid,
                    drift_func=drift_func,
                    drift_noise=drift_noise,
                    first_step_alpha=first_step_alpha,
                    solver_tolerences=NonlinearSolverTolerences.from_json(
                        json_data[params]["solver_tolerences"]
                    ),
                )
                kwargs["linear_finitediff_params"] = None
            else:
                raise ValueError(f"{params} not a supported finitediff solver")

        else:
            raise NotImplementedError(
                "ExperiementConfig only supports finitediff experiements"
            )

        return ExperimentConfig(**kwargs)

    def run_experiments(self):
        if self.num_threads > 1:
            self._run_experiments_parallel()
        else:
            self._run_experiments_serial()

    def _run_experiments_serial(self):
        if self.linear_finitediff_params:
            solver = LinearFiniteDiffSolver(
                params=self.linear_finitediff_params,
            )
        elif self.nonlinear_finitediff_params:
            solver = NonlinearFiniteDiffSolver(
                params=self.nonlinear_finitediff_params
            )
        else:
            raise ValueError("No parameters specified")

        for exp_num in range(self.num_simulations):
            prefix = f"exp{exp_num+1}_"

            densities, bm_paths = solver.solve_ivp(
                initial_density=self.initial_density,
                keep_all_steps=self.output.keep_all_steps,
                keep_bm_paths=self.output.keep_bm_paths,
            )

            self.output.write_output(
                densities=densities, bm_paths=bm_paths, prefix=prefix
            )

            for figure in self.figures:
                figure.plot(
                    grid=solver.params.grid, densities=densities, prefix=prefix
                )

    def _run_experiments_parallel(self):
        num_processes_per_thr = int(self.num_simulations / self.num_threads)

        def run_experiments_func(thread_num: int, num_experiments: int):
            if self.linear_finitediff_params:
                solver = LinearFiniteDiffSolver(
                    params=self.linear_finitediff_params,
                )
            elif self.nonlinear_finitediff_params:
                solver = NonlinearFiniteDiffSolver(
                    params=self.nonlinear_finitediff_params
                )
            else:
                raise ValueError("No parameters specified")

            for exp_num in range(num_experiments):
                prefix = f"th{thread_num}_exp{exp_num+1}_"

                densities, bm_paths = solver.solve_ivp(
                    initial_density=self.initial_density,
                    keep_all_steps=self.output.keep_all_steps,
                    keep_bm_paths=self.output.keep_bm_paths,
                )

                self.output.write_output(
                    densities=densities, bm_paths=bm_paths, prefix=prefix
                )

                for figure in self.figures:
                    figure.plot(
                        grid=solver.params.grid, densities=densities, prefix=prefix
                    )

        remainder = self.num_simulations % self.num_threads
        num_tasks = int(self.num_simulations / self.num_threads)
        task_for_thread = [num_tasks] * (self.num_threads)
        task_for_thread[-1] = task_for_thread[-1] + remainder
        thread_numbers = range(1, self.num_threads + 1)
        run_experiments_func_args = list(zip(thread_numbers, task_for_thread))

        pool = pl.ThreadPool(self.num_threads)
        pool.starmap(run_experiments_func, run_experiments_func_args)
