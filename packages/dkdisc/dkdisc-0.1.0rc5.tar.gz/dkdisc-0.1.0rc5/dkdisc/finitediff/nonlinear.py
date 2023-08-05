import dataclasses
import logging as log
import numpy.typing as npt
import scipy.optimize as opt
import typing as typ

from dkdisc.finitediff import FiniteDiffFunctionParams
from dkdisc.finitediff import FiniteDiffSolver


@dataclasses.dataclass
class NonlinearSolverTolerences:
    nonlinear_solver_max_iter: int = 10
    nonlinear_solver_ftol: float = 1e-6
    nonlinear_solver_xtol: float = 1e-8

    @classmethod
    def from_json(cls, json_data):
        return NonlinearSolverTolerences(**json_data)


@dataclasses.dataclass
class NonlinearFiniteDiffFunctionParams(FiniteDiffFunctionParams):
    solver_tolerences: NonlinearSolverTolerences

    # Automatically calculated Jacobians, if not specified
    drift_jacobian: typ.Optional[typ.Callable] = dataclasses.field(default=None)

    def __post_init__(self):
        """Automatically calculate drift jacobian"""
        if self.drift_jacobian is None:

            def drift_jacobian_py(val):
                from autograd import jacobian

                drift = self.drift_func(val)
                drift_jacob = jacobian(drift)
                return drift_jacob

            self.drift_jacobian = drift_jacobian_py


class NonlinearFiniteDiffSolver(FiniteDiffSolver):
    def __init__(self, params: NonlinearFiniteDiffFunctionParams, rng_seed=None):
        super().__init__(
            num_time_steps=params.num_time_steps,
            time_step=params.time_step,
            grid=params.grid,
            drift_func=params.drift_func,
            drift_noise=params.drift_noise,
            rng_seed=rng_seed,
        )
        self.params = params
        log.debug("Setup nonlinear finite difference solver")

    def first_step(
        self, initial_density: npt.NDArray, initial_noise: npt.NDArray
    ) -> npt.NDArray:
        def euler_nonlinear_func(next_density, prev_density, dTime):
            log.debug("Executing (first step) nonlinear function eval")
            return (
                next_density - prev_density - (self.drift_func(next_density) * dTime)
            )

        def euler_nonlinear_jacob(next_density, _, dTime):
            log.debug("Executing (first step) nonlinear function jacobian eval")
            if not self.params.drift_jacobian:
                raise RuntimeError(
                    "Unable to compute the required drift"
                    + " Jacobian for Implicit Euler Method"
                )
            return (
                self.grid.get_identity()
                - (2.0 / 3.0) * self.params.drift_jacobian(next_density) * dTime
            )

        deterministic_vector = (
            (1.0 - self.params.first_step_alpha)
            * self.time_step
            * self.drift_func(initial_density)
        )
        step_vector = initial_density + deterministic_vector + initial_noise

        log.debug("Solving for nonlinear FD first step with scipy.optimize.fsolve")
        step_solution = opt.fsolve(
            func=euler_nonlinear_func,
            x0=initial_density,
            args=(step_vector, self.time_step),
            fprime=euler_nonlinear_jacob,
            xtol=self.params.solver_tolerences.nonlinear_solver_xtol,
            maxfev=self.params.solver_tolerences.nonlinear_solver_max_iter,
            full_output=False,
        )

        return step_solution

    def further_step(
        self,
        curr_density: npt.NDArray,
        curr_noise: npt.NDArray,
        prev_density: npt.NDArray,
        prev_noise: npt.NDArray,
    ) -> npt.NDArray:
        def bdf2_nonlinear_func(next_density, step_vector, dTime):
            log.debug("Executing nonlinear function eval")
            return (
                curr_density
                - step_vector
                - (2.0 / 3.0) * self.drift_func(next_density) * dTime
            )

        def bdf2_nonlinear_jacob(next_density, _, dTime):
            log.debug("Executing nonlinear function jacobian eval")
            if not self.params.drift_jacobian:
                raise RuntimeError(
                    "Unable to compute drift Jacobian needed" + " for BDF2 step"
                )
            return (
                self.grid.get_identity()
                - (2.0 / 3.0) * self.params.drift_jacobian(next_density) * dTime
            )

        vec = (4.0 / 3.0) * curr_density - (1.0 / 3.0) * prev_density
        step_vector = vec + curr_noise + prev_noise

        log.debug("Solving for nonlinear FD next step with scipy.optimize.fsolve")
        step_solution = opt.fsolve(
            func=bdf2_nonlinear_func,
            x0=curr_density,
            args=(step_vector, self.time_step),
            fprime=bdf2_nonlinear_jacob,
            xtol=self.params.solver_tolerences.nonlinear_solver_xtol,
            maxfev=self.params.solver_tolerences.nonlinear_solver_max_iter,
        )

        return step_solution
