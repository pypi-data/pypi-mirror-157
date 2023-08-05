import dataclasses
import numpy as np
import numpy.typing as npt
import scipy.linalg as lin


@dataclasses.dataclass
class Grid:
    mesh_size: float
    dimension: int
    start: float = dataclasses.field(default=-np.pi)
    stop: float = dataclasses.field(default=np.pi)

    def __post_init__(self):
        if self.dimension <= 0:
            raise ValueError("Must provide a positive dimension")

        if self.dimension == 1:
            self.points = np.arange(self.start, self.stop, self.mesh_size)
        else:
            # TODO: Figure out best way for this for numpy, because tensors are
            #       slow at scale. Likely better to do reshaping and solve
            #       linear equations.
            gridbounds = [
                np.arange(self.start, self.stop, self.mesh_size)
                for _ in range(self.dimension)
            ]
            mesh_list = np.meshgrid(*gridbounds)
            self.points = np.stack(mesh_list)

        self.shape = self.points.shape
        self.size = np.size(self.points)
        self.num_points_1d = self.shape[0]

        # Lazily compute these only when absolutely required
        self.identity = None
        self.laplacian = None

    def get_identity(self) -> npt.NDArray:
        if not isinstance(self.identity, np.ndarray):
            if self.dimension == 1:
                self.identity = np.eye(self.num_points_1d)
            else:
                tensor_dimension = (self.num_points_1d,) * self.dimension
                diagonal = tuple([np.arange(self.num_points_1d)] * self.dimension)
                identity_tensor = np.zeros(tensor_dimension)
                identity_tensor[diagonal] = 1.0
                self.identity = identity_tensor
        return self.identity

    def get_laplacian(self) -> npt.NDArray:
        if not isinstance(self.laplacian, np.ndarray):
            if self.dimension == 1:
                lap_col = np.zeros(self.num_points_1d)
                lap_col[0] = -2.0
                lap_col[1] = 1.0
                lap_col[-1] = 1.0
                self.laplacian = lin.circulant(lap_col)
            else:
                self.laplacian = -2.0 * self.get_identity().copy()
                diagonal = np.ndarray(
                    [np.arange(self.num_points_1d)] * self.dimension
                )
                off_diagonal = []

                for index in range(self.num_points_1d):
                    for dim in range(self.dimension):
                        upper = diagonal.copy()
                        if upper[dim, index] == self.num_points_1d:
                            upper[dim, index] = 0
                        else:
                            upper[dim, index] = upper[dim, index] + 1.0

                        lower = diagonal.copy()
                        if lower[dim, index] == 0:
                            lower[dim, index] = self.num_points_1d
                        else:
                            lower[dim, index] = lower[dim, index] - 1.0

                        off_diagonal.append(upper)
                        off_diagonal.append(lower)

                for off_diagonal_elem in off_diagonal:
                    self.laplacian[off_diagonal_elem] = 1.0

        return self.laplacian

    @classmethod
    def from_json(cls, json_data):
        return Grid(**json_data)
