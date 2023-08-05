import dataclasses
import logging as log
import numpy as np
import numpy.typing as npt
import scipy.linalg as lin

from dkdisc.finitediff import FiniteDiffFunctionParams
from dkdisc.finitediff import FiniteDiffSolver


@dataclasses.dataclass
class LinearSolverHints:
    first_step_is_circulant: bool = dataclasses.field(default=False)
    first_step_is_toepletz: bool = dataclasses.field(default=False)
    first_step_is_triangular: bool = dataclasses.field(default=False)
    further_steps_are_circulant: bool = dataclasses.field(default=False)
    further_steps_are_toepletz: bool = dataclasses.field(default=False)
    further_steps_are_triangular: bool = dataclasses.field(default=False)

    @classmethod
    def from_json(cls, json_data):
        return LinearSolverHints(**json_data)


@dataclasses.dataclass
class LinearFiniteDiffFunctionParams(FiniteDiffFunctionParams):
    first_step_matrix: npt.NDArray
    further_steps_matrix: npt.NDArray
    linear_solver_hints: LinearSolverHints


class LinearFiniteDiffSolver(FiniteDiffSolver):
    def __init__(self, params: LinearFiniteDiffFunctionParams, rng_seed=None):
        super().__init__(
            num_time_steps=params.num_time_steps,
            time_step=params.time_step,
            grid=params.grid,
            drift_func=params.drift_func,
            drift_noise=params.drift_noise,
            rng_seed=rng_seed,
        )
        self.params = params
        log.debug("Setup linear finite difference solver")

    def first_step(
        self,
        initial_density: npt.NDArray,
        initial_noise: npt.NDArray,
    ) -> npt.NDArray:

        deterministic_vector = (
            (1.0 - self.params.first_step_alpha)
            * self.params.time_step
            * self.params.drift_func(initial_density)
        )
        step_vector = initial_density + deterministic_vector + initial_noise

        if self.grid.dimension > 1:
            log.debug("Solving first step with np.linalg.tensorsolve")
            return np.linalg.tensorsolve(self.params.first_step_matrix, step_vector)
        elif self.params.linear_solver_hints.first_step_is_circulant:
            log.debug("Solving first step with scipy.linalg.solve_circulant")
            if (
                np.size(self.params.first_step_matrix)
                == self.params.first_step_matrix.shape[0]
            ):
                return lin.solve_circulant(
                    self.params.first_step_matrix, step_vector
                )
            else:
                return lin.solve_circulant(
                    self.params.first_step_matrix[:, 0], step_vector
                )
        elif self.params.linear_solver_hints.first_step_is_toepletz:
            log.debug("Solving first step with scipy.linalg.solve_toeplitz")
            return lin.solve_toeplitz(self.params.first_step_matrix, step_vector)
        elif self.params.linear_solver_hints.first_step_is_triangular:
            log.debug("Solving first step with scipy.linalg.solve_triangular")
            return lin.solve_triangular(self.params.first_step_matrix, step_vector)
        else:
            log.debug("Solving first step with scipy.linalg.solve")
            return lin.solve(self.params.first_step_matrix, step_vector)

    def further_step(
        self,
        curr_density: npt.NDArray,
        curr_noise: npt.NDArray,
        prev_density: npt.NDArray,
        prev_noise: npt.NDArray,
    ) -> npt.NDArray:

        vec = (4.0 / 3.0) * curr_density - (1.0 / 3.0) * prev_density
        step_vector = vec + curr_noise + prev_noise

        if self.grid.dimension > 1:
            log.debug("Solving next step with numpy.linalg.tensorsolve")
            return np.linalg.tensorsolve(self.params.first_step_matrix, step_vector)
        elif self.params.linear_solver_hints.further_steps_are_circulant:
            log.debug("Solving next step with scipy.linalg.solve_circulant")
            if (
                np.size(self.params.further_steps_matrix)
                == self.params.further_steps_matrix.shape[0]
            ):
                return lin.solve_circulant(
                    self.params.further_steps_matrix, step_vector
                )
            else:
                return lin.solve_circulant(
                    self.params.further_steps_matrix[:, 0], step_vector
                )
        elif self.params.linear_solver_hints.further_steps_are_toepletz:
            log.debug("Solving next step with scipy.linalg.solve_toeplitz")
            return lin.solve_toeplitz(self.params.further_steps_matrix, step_vector)
        elif self.params.linear_solver_hints.further_steps_are_triangular:
            log.debug("Solving next step with scipy.linalg.solve_triangular")
            return lin.solve_triangular(
                self.params.further_steps_matrix, step_vector
            )
        else:
            log.debug("Solving next step with scipy.linalg.solve")
            return lin.solve(self.params.further_steps_matrix, step_vector)
