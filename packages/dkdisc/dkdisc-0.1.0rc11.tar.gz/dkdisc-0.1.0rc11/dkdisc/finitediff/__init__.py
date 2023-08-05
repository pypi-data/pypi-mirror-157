import abc
import dataclasses
import logging as log
import numpy as np
import numpy.typing as npt
import typing as typ

from dkdisc.finitediff.grid import Grid


@dataclasses.dataclass
class FiniteDiffFunctionParams:
    num_time_steps: int
    time_step: float
    grid: Grid
    drift_func: typ.Callable[[npt.NDArray], npt.NDArray]
    drift_noise: typ.Callable[[npt.NDArray, npt.NDArray], npt.NDArray]
    first_step_alpha: float


class FiniteDiffSolver(metaclass=abc.ABCMeta):
    def __init__(
        self,
        num_time_steps: int,
        time_step: float,
        grid: Grid,
        drift_func: typ.Callable[[npt.NDArray], npt.NDArray],
        drift_noise: typ.Callable[[npt.NDArray, npt.NDArray], npt.NDArray],
        rng_seed=None,
    ):
        """
        Basic method that creates the grid parameters, random number generator
        and time/space discretizations to save for access in solver steps.
        """
        self.num_time_steps = num_time_steps
        self.time_step = time_step
        self.grid = grid
        self.drift_func = drift_func
        self.drift_noise = drift_noise
        self.rng = np.random.default_rng(seed=rng_seed)

    def solve_ivp(
        self,
        initial_density: npt.NDArray,
        keep_all_steps: bool = False,
        keep_bm_paths: bool = False,
    ) -> typ.Tuple[npt.NDArray, npt.NDArray]:

        # TODO: Modify API to include to option to accumulate weak soln's
        densities_to_keep = []
        bm_paths_to_keep = []
        curr_time = 0.0

        prev_density = initial_density
        dWiener = self.rng.normal(
            scale=np.sqrt(self.time_step), size=self.grid.shape
        )

        log.debug(
            f"""Starting to solve the IVP problem with parameters:
            num_time_steps: {self.num_time_steps}
            time_step: {self.time_step}
            mesh_size: {self.grid.mesh_size}
            grid_start: {self.grid.start}
            grid_stop: {self.grid.stop}
            space_dim: {self.grid.dimension}
            num_grid_points: {self.grid.size}
            initial_density: {prev_density} 
            keep_all_steps: {keep_all_steps}
            keep_bm_paths: {keep_bm_paths}
            """
        )

        # First time step depends only on initial density.
        prev_noise = self.drift_noise(prev_density, dWiener)
        curr_density = self.first_step(
            prev_density,
            prev_noise,
        )
        curr_time += self.time_step

        if keep_all_steps:
            densities_to_keep.append(prev_density)
            densities_to_keep.append(curr_density)

        if keep_bm_paths:
            bm_paths_to_keep.append(np.zeros(self.grid.shape))
            bm_paths_to_keep.append(dWiener)

        log.debug("Completed first step of finite difference algorithm")

        # For subsequent steps, each step is allowed to depend on the
        # density at the current time and the density at the time immediately
        # preceeding the current one.
        for step_num in range(1, self.num_time_steps):
            dWiener = self.rng.normal(scale=self.time_step, size=self.grid.shape)

            curr_noise = self.drift_noise(curr_density, dWiener)
            curr_time += self.time_step
            next_density = self.further_step(
                curr_density,
                curr_noise,
                prev_density,
                prev_noise,
            )

            if keep_all_steps:
                densities_to_keep.append(next_density)

            if keep_bm_paths:
                bm_paths_to_keep.append(dWiener)

            prev_density = curr_density
            curr_density = next_density
            prev_noise = curr_noise

            log.debug(f"Completed step {step_num} of finite difference algorithm")

        if keep_all_steps:
            densities = np.stack(densities_to_keep)
        else:
            densities = curr_density

        if keep_bm_paths:
            bm_paths = np.cumsum(np.stack(bm_paths_to_keep))
        else:
            bm_paths = np.zeros((1, 1))

        log.debug("Completed finite difference algorithm!")

        return densities, bm_paths

    @abc.abstractmethod
    def first_step(
        self,
        initial_density: npt.NDArray,
        initial_noise: npt.NDArray,
    ) -> npt.NDArray:
        """
        Method (to be implemented by child classes) that computes the first
        step in the initial value problem solver using just the initial values.

        Args:
            initial_density: NDArray of initial density of the same shape as
                             self.params.grid.shape

            time_step: The time step to take in the first step

        Returns:
            density: NDArray of the solution to the IVP at time t=time_step.
        """
        pass

    @abc.abstractmethod
    def further_step(
        self,
        curr_density: npt.NDArray,
        curr_noise: npt.NDArray,
        prev_density: npt.NDArray,
        prev_noise: npt.NDArray,
    ) -> npt.NDArray:
        """
        Method (to be implemented by child classes) that computes the later
        steps in the initial value problem solver using both the current value
        of the IVP solution and the value at the previous time step.

        Args:
            curr_density: NDArray of the current solution to the IVP. Of the
                          same shape as self.params.grid.shape.


            prev_density: NDArray of the previous step's solution to the IVP.
                          Of the same shape as self.params.grid.shape.

            time_step: The time step to take in the current computation.

        Returns:
            density: NDArray of the solution to the IVP at time
                     t=curr_time+time_step.
        """
        pass
