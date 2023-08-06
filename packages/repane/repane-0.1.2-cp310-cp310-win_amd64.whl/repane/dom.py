from math import isnan
from typing import Callable, List, Tuple, Optional

from .expr import exmat
from .mesh import Mesh, Group
from .repane import Nexus


class Dom:
    __nexus: Nexus

    def __init__(self, mesh: Mesh):
        self.__nexus = Nexus(mesh.pts, mesh.edges, mesh.cells)

    def plot_sys(self) -> Tuple[List[float], List[float], List[float]]:
        x, y = self.__nexus.plot_sys()
        z = [0. if not isnan(v) else v for v in x]
        return x, y, z

    def set_boundary(self, *groups):
        for group in groups:
            self.__nexus.set_boundary(group.vers, group.edges)
        self.__nexus.set_dofs()
        self.__nexus.set_solver()

    def dofs(self) -> Tuple[int, int]:
        return self.__nexus.tot_dofs()

    def embed_bcond(self, bcond: Callable[[float, float], List[float]], group):
        arena, vec = exmat(bcond)
        assert len(vec) == 2
        self.__nexus.embed_bcond(list(group.vers), list(group.edges), arena, vec)

    def set_force(self, force: Callable[[float, float], List[float]], group: Optional[Group] = None):
        if group is None:
            arena, vec = exmat(force)
            assert len(vec) == 2
            self.__nexus.set_force(0, set(), arena, vec)
        else:
            arena, vec = exmat(force)
            assert len(vec) == 2
            self.__nexus.set_force(group.id, group.cells, arena, vec)

    def set_moment(self, force: Callable[[float, float], List[float]], group: Optional[Group] = None):
        if group is None:
            arena, vec = exmat(force)
            assert len(vec) == 4
            self.__nexus.set_moment(0, set(), arena, vec)
        else:
            arena, vec = exmat(force)
            assert len(vec) == 4
            self.__nexus.set_moment(group.id, group.cells, arena, vec)

    def set_consts(self, c_ec: List[List[float]], c_ecm: List[List[float]], mulc: float):
        self.__nexus.set_consts(c_ec, c_ecm, mulc)

    def solve(self, tol: float = 1e-10, solver: str = "cg"):
        self.__nexus.assemble()
        self.__nexus.solve(tol, solver)

    def set_vals(self):
        self.__nexus.set_vals()

    def plot_curves(self, res: int, group: Group = None) -> Tuple[List[float], List[float], List[float]]:
        if group is None:
            x, y = self.__nexus.plot_curves(res, set())
            z = [0. if not isnan(v) else v for v in x]
            return x, y, z
        else:
            x, y = self.__nexus.plot_curves(res, group.edges)
            z = [0. if not isnan(v) else v for v in x]
            return x, y, z

    def plot_disp(self, res: int, group: Group = None) -> \
            Tuple[List[float], List[float], List[float], List[float], List[Tuple[int, int, int]]]:
        if group is None:
            (x, y, w), cells = self.__nexus.plot_disp(res, set())
            z = [0. for _ in range(len(x))]
            return x, y, z, w, cells
        else:
            (x, y, w), cells = self.__nexus.plot_disp(res, group.cells)
            z = [0. for _ in range(len(x))]
            return x, y, z, w, cells

    def plot_flux(self, res: int, axis: int, group: Group = None) -> \
            Tuple[List[float], List[float], List[float], List[float], List[float], List[float]]:
        assert axis == 0 or axis == 1
        if group is None:
            x, y, u, v = self.__nexus.plot_flux(res, set(), axis)
            z = [0. for _ in range(len(x))]
            return x, y, z, u, v, z
        else:
            x, y, u, v = self.__nexus.plot_flux(res, group.cells, axis)
            z = [0. for _ in range(len(x))]
            return x, y, z, u, v, z

    def plot_dist(self, res: int, group: Group = None) -> Tuple[List[float], List[float], List[float], List[float]]:
        if group is None:
            x, y, w = self.__nexus.plot_dist(res, set())
            z = [0. for _ in range(len(x))]
            return x, y, z, w
        else:
            x, y, w = self.__nexus.plot_dist(res, group.cells)
            z = [0. for _ in range(len(x))]
            return x, y, z, w

    def disp_err(self, disp: Callable[[float, float], List[float]]) -> float:
        disp = exmat(disp)
        assert len(disp[1]) == 2
        return self.__nexus.disp_err(disp)

    def flux_err(self, flux: Callable[[float, float], List[float]]) -> float:
        flux = exmat(flux)
        assert len(flux[1]) == 4
        return self.__nexus.flux_err(flux)

    def energy(self) -> float:
        return self.__nexus.energy()
