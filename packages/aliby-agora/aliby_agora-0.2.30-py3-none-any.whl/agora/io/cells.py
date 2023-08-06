import logging
from collections.abc import Iterable
from itertools import groupby
from pathlib import Path, PosixPath
from typing import Union

import h5py
import numpy as np
from agora.io.writer import load_complex
from numpy.lib.stride_tricks import sliding_window_view
from scipy import ndimage
from scipy.sparse.base import isdense
from utils_find_1st import cmp_equal, find_1st

# def cell_factory(store, type="hdf5"):
#     if type == "hdf5":
#         return CellsHDF(store)
#     else:
#         raise TypeError(
#             "Could not get cells for type {}:" "valid types are matlab and hdf5"
#         )


class Cells:
    """An object that gathers information about all the cells in a given
    trap.
    This is the abstract object, used for type testing
    """

    def __init__(self):
        pass

    @classmethod
    def from_source(cls, source: Union[PosixPath, str]):
        if isinstance(source, str):
            source = Path(source)
        if source.suffix == ".mat":  # Infer kind from filename
            raise ("Matlab files no longer supported")
        return cls(source)

    @staticmethod
    def _asdense(array):
        if not isdense(array):
            array = array.todense()
        return array

    @staticmethod
    def _astype(array, kind):
        # Convert sparse arrays if needed and if kind is 'mask' it fills the outline
        array = Cells._asdense(array)
        if kind == "mask":
            array = ndimage.binary_fill_holes(array).astype(bool)
        return array

    @classmethod
    def hdf(cls, fpath):
        return CellsHDF(fpath)

    # @classmethod
    # def mat(cls, path):
    #     return CellsMat(matObject(store))


class CellsHDF(Cells):
    def __init__(
        self, filename: Union[str, PosixPath], path: str = "cell_info"
    ):
        self.filename = filename
        self.cinfo_path = path
        self._edgem_indices = None
        self._edgemasks = None
        self._tile_size = None

    def __getitem__(self, item: str):
        if item == "edgemasks":
            return self.edgemasks
        _item = "_" + item
        if not hasattr(self, _item):
            setattr(self, _item, self._fetch(item))
        return getattr(self, _item)

    def _get_idx(self, cell_id: int, trap_id: int):
        return (self["cell_label"] == cell_id) & (self["trap"] == trap_id)

    def _fetch(self, path: str):
        with h5py.File(self.filename, mode="r") as f:
            return f[self.cinfo_path][path][()]

    @property
    def ntraps(self) -> int:
        with h5py.File(self.filename, mode="r") as f:
            return len(f["/trap_info/trap_locations"][()])

    @property
    def traps(self) -> list:
        return list(set(self["trap"]))

    @property
    def ntimepoints(self) -> int:
        return cells["timepoint"].max() + 1

    @property
    def tile_size(self) -> int:
        if self._tile_size is None:
            with h5py.File(self.filename, mode="r") as f:
                self._tile_size == f["trap_info/tile_size"][0]
        return self._tile_size

    @property
    def edgem_indices(self) -> np.array:
        if self._edgem_indices is None:
            edgem_path = "edgemasks/indices"
            self._edgem_indices = load_complex(self._fetch(edgem_path))
        return self._edgem_indices

    def nonempty_tp_in_trap(self, trap_id: int) -> set:
        # Returns time-points in which cells are available
        return set(self["timepoint"][self["trap"] == trap_id])

    @property
    def edgemasks(self):
        if self._edgemasks is None:
            edgem_path = "edgemasks/values"
            self._edgemasks = self._fetch(edgem_path)

        return self._edgemasks

    def _edgem_where(self, cell_id, trap_id):
        ix = trap_id + 1j * cell_id
        return find_1st(self.edgem_indices == ix, True, cmp_equal)

    @property
    def labels(self):
        """
        Return all cell labels in object
        We use mother_assign to list traps because it is the only propriety that appears even
        when no cells are found"""
        return [self.labels_in_trap(trap) for trap in self.traps]

    def where(self, cell_id, trap_id):
        """
        Returns
        Parameters
        ----------
            cell_id: int
                Cell index
            trap_id: int
                Trap index

        Returns
        ----------
            indices int array
            boolean mask array
            edge_ix int array
        """
        indices = self._get_idx(cell_id, trap_id)
        edgem_ix = self._edgem_where(cell_id, trap_id)
        return (
            self["timepoint"][indices],
            indices,
            edgem_ix,
        )  # FIXME edgem_ix makes output different to matlab's Cell

    def outline(self, cell_id, trap_id):
        times, indices, cell_ix = self.where(cell_id, trap_id)
        return times, self["edgemasks"][cell_ix, times]

    def mask(self, cell_id, trap_id):
        times, outlines = self.outline(cell_id, trap_id)
        return times, np.array(
            [ndimage.morphology.binary_fill_holes(o) for o in outlines]
        )

    def at_time(self, timepoint, kind="mask"):
        ix = self["timepoint"] == timepoint
        cell_ix = self["cell_label"][ix]
        traps = self["trap"][ix]
        indices = traps + 1j * cell_ix
        choose = np.in1d(self.edgem_indices, indices)
        edgemasks = self["edgemasks"][choose, timepoint]
        masks = [
            self._astype(edgemask, kind)
            for edgemask in edgemasks
            if edgemask.any()
        ]
        return self.group_by_traps(traps, masks)

    def group_by_traps(self, traps, data):
        # returns a dict with traps as keys and labels as value
        iterator = groupby(zip(traps, data), lambda x: x[0])
        d = {key: [x[1] for x in group] for key, group in iterator}
        d = {i: d.get(i, []) for i in self.traps}
        return d

    def labels_in_trap(self, trap_id):
        # Return set of cell ids in a trap.
        return set((self["cell_label"][self["trap"] == trap_id]))

    def labels_at_time(self, timepoint):
        labels = self["cell_label"][self["timepoint"] == timepoint]
        traps = self["trap"][self["timepoint"] == timepoint]
        return self.group_by_traps(traps, labels)


class CellsLinear(CellsHDF):
    """
    Reimplement functions from CellsHDF to save edgemasks in a (N,tile_size, tile_size) array

    This overrides the previous implementation of at_time.
    """

    def __init__(self, filename, path="cell_info"):
        super().__init__(filename, path=path)

    def __getitem__(self, item):
        assert item != "edgemasks", "Edgemasks must not be loaded as a whole"

        _item = "_" + item
        if not hasattr(self, _item):
            setattr(self, _item, self._fetch(item))
        return getattr(self, _item)

    def _fetch(self, path):
        with h5py.File(self.filename, mode="r") as f:
            return f[self.cinfo_path][path][()]

    def _edgem_from_masking(self, mask):
        with h5py.File(self.filename, mode="r") as f:
            edgem = f[self.cinfo_path + "/edgemasks"][mask, ...]
        return edgem

    def _edgem_where(self, cell_id, trap_id):
        id_mask = self._get_idx(cell_id, trap_id)
        edgem = self._edgem_from_masking(id_mask)

        return edgem

    def outline(self, cell_id, trap_id):
        id_mask = self._get_idx(cell_id, trap_id)
        times = self["timepoint"][id_mask]

        return times, self.edgem_from_masking(id_mask)

    def at_time(self, timepoint, kind="mask"):
        ix = self["timepoint"] == timepoint
        traps = self["trap"][ix]
        edgemasks = self._edgem_from_masking(ix)
        masks = [
            self._astype(edgemask, kind)
            for edgemask in edgemasks
            if edgemask.any()
        ]
        return self.group_by_traps(traps, masks)

    @property
    def ntimepoints(self) -> int:
        return self["timepoint"].max() + 1

    @property
    def ncells_matrix(self):
        ncells_mat = np.zeros(
            (self.ntraps, self["cell_label"].max(), self.ntimepoints),
            dtype=bool,
        )
        ncells_mat[
            self["trap"], self["cell_label"] - 1, self["timepoint"]
        ] = True
        return ncells_mat

    def matrix_trap_tp_where(
        self,
        min_ncells: int = None,
        min_consecutive_tps: int = None,
        label_modulo: int = None,
    ):
        """
        Return a matrix of shape (ntraps x ntps - min_consecutive_tps to
        indicate traps and time-points where min_ncells are available for at least min_consecutive_tps

        Parameters
        ---------
        min_ncells: int Minimum number of cells
        min_consecutive_tps: int
                Minimum number of time-points a
        label_modulo: int that discards traps with any cell X labels away from another. This is useful for quick plotting without repeated colours (pyplot's 'Set1' colormap has 9 colours)


        Returns
        ---------
            (ntraps x ( ntps-min_consecutive_tps )) 2D boolean numpy array where rows are trap ids and columns are timepoint windows.
            If the value in a cell is true its corresponding trap and timepoint contains more than min_ncells for at least min_consecutive time-points.
        """
        if min_ncells is None:
            min_ncells = 2
        if min_consecutive_tps is None:
            min_consecutive_tps = 5

        matrix = self.ncells_matrix
        if label_modulo:
            swapped = matrix.swapaxes(1, 2)
            modulos = ~(
                np.array(
                    [
                        np.tile(
                            np.arange(i, label_modulo + i),
                            int(np.ceil(matrix.shape[1] / label_modulo)),
                        )
                        for i in range(1, label_modulo + 1)
                    ]
                )[:, : matrix.shape[1]]
                % label_modulo
            ).astype(bool)

            reds = (
                np.array(
                    [
                        np.logical_and(swapped, mod).sum(axis=2)
                        for mod in modulos
                    ]
                ).sum(axis=0)
                > 2
            )
            swapped[reds] = False
            matrix = swapped.swapaxes(1, 2)

        window = sliding_window_view(matrix, min_consecutive_tps, axis=2)
        tp_min = window.sum(axis=-1) == min_consecutive_tps
        ncells_tp_min = tp_min.sum(axis=1) >= min_ncells
        return ncells_tp_min

    def random_valid_trap_tp(
        self,
        min_ncells: int = None,
        min_consecutive_tps: int = None,
        label_modulo: int = None,
    ):
        """
        Return a randomly-selected pair of trap_id and timepoints
        min_ncells: int Minimum number of cells
        min_consecutive_tps: int
                Minimum number of time-points a
        label_modulo: int that discards traps with any cell X labels away from another. This is useful for quick plotting without repeated colours (pyplot's 'Set1' colormap has 9 colours)
        """

        mat = self.matrix_trap_tp_where(
            min_ncells=min_ncells,
            min_consecutive_tps=min_consecutive_tps,
            label_modulo=label_modulo,
        )
        traps, tps = np.where(mat)

        rand = np.random.randint(mat.sum())
        return (traps[rand], tps[rand])


# class CellsMat(Cells):
#     def __init__(self, mat_object):
#         super(CellsMat, self).__init__()
#         # TODO add __contains__ to the matObject
#         timelapse_traps = mat_object.get(
#             "timelapseTrapsOmero", mat_object.get("timelapseTraps", None)
#         )
#         if timelapse_traps is None:
#             raise NotImplementedError(
#                 "Could not find a timelapseTraps or "
#                 "timelapseTrapsOmero object. Cells "
#                 "from cellResults not implemented"
#             )
#         else:
#             self.trap_info = timelapse_traps["cTimepoint"]["trapInfo"]

#             if isinstance(self.trap_info, list):
#                 self.trap_info = {
#                     k: list([res.get(k, []) for res in self.trap_info])
#                     for k in self.trap_info[0].keys()
#                 }

#     def where(self, cell_id, trap_id):
#         times, indices = zip(
#             *[
#                 (tp, np.where(cell_id == x)[0][0])
#                 for tp, x in enumerate(self.trap_info["cellLabel"][:, trap_id].tolist())
#                 if np.any(cell_id == x)
#             ]
#         )
#         return times, indices

#     def outline(self, cell_id, trap_id):
#         times, indices = self.where(cell_id, trap_id)
#         info = self.trap_info["cell"][times, trap_id]

#         def get_segmented(cell, index):
#             if cell["segmented"].ndim == 0:
#                 return cell["segmented"][()].todense()
#             else:
#                 return cell["segmented"][index].todense()

#         segmentation_outline = [
#             get_segmented(cell, idx) for idx, cell in zip(indices, info)
#         ]
#         return times, np.array(segmentation_outline)

#     def mask(self, cell_id, trap_id):
#         times, outlines = self.outline(cell_id, trap_id)
#         return times, np.array(
#             [ndimage.morphology.binary_fill_holes(o) for o in outlines]
#         )

#     def at_time(self, timepoint, kind="outline"):

#         """Returns the segmentations for all the cells at a given timepoint.

#         FIXME: this is extremely hacky and accounts for differently saved
#             results in the matlab object. Deprecate ASAP.
#         """
#         # Case 1: only one cell per trap: trap_info['cell'][timepoint] is a
#         # structured array
#         if isinstance(self.trap_info["cell"][timepoint], dict):
#             segmentations = [
#                 self._astype(x, "outline")
#                 for x in self.trap_info["cell"][timepoint]["segmented"]
#             ]
#         # Case 2: Multiple cells per trap: it becomes a list of arrays or
#         # dictionaries,  one for each trap
#         # Case 2.1 : it's a dictionary
#         elif isinstance(self.trap_info["cell"][timepoint][0], dict):
#             segmentations = []
#             for x in self.trap_info["cell"][timepoint]:
#                 seg = x["segmented"]
#                 if not isinstance(seg, np.ndarray):
#                     seg = [seg]
#                 segmentations.append([self._astype(y, "outline") for y in seg])
#         # Case 2.2 : it's an array
#         else:
#             segmentations = [
#                 [self._astype(y, type) for y in x["segmented"]] if x.ndim != 0 else []
#                 for x in self.trap_info["cell"][timepoint]
#             ]
#             # Return dict for compatibility with hdf5 output
#         return {i: v for i, v in enumerate(segmentations)}

#     def labels_at_time(self, tp):
#         labels = self.trap_info["cellLabel"]
#         labels = [_aslist(x) for x in labels[tp]]
#         labels = {i: [lbl for lbl in lblset] for i, lblset in enumerate(labels)}
#         return labels

#     @property
#     def ntraps(self):
#         return len(self.trap_info["cellLabel"][0])

#     @property
#     def tile_size(self):
#         pass


# class ExtractionRunner:
#     """An object to run extraction of fluorescence, and general data out of
#     segmented data.

#     Configure with what extraction we want to run.
#     Cell selection criteria.
#     Filtering criteria.
#     """

#     def __init__(self, tiler, cells):
#         pass

#     def run(self, keys, store, **kwargs):
#         pass


# def _aslist(x):
#     if isinstance(x, Iterable):
#         if hasattr(x, "tolist"):
#             x = x.tolist()
#     else:
#         x = [x]
#     return x
