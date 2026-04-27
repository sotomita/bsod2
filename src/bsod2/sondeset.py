#! /usr/bin/env python3

from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from pathlib import Path
from tqdm import tqdm
import xarray as xr

from .sonde import Sonde


@dataclass(frozen=True)
class Sondeset:
    """
    Sonde Class

    Parameters
    ----------
    fpath : Path | list[Path]
        Path or list of Path to a raw file, or a directory.
    rm_descending : bool, optimal
        True to remove descending records, by default False
    interp : str | None, optimal
        name of interpolation axis. if None, interpolation is not performed, by default None
    interp_pmin : float, optimal
        minimum value of interpolated pressure axis, by default 50.0
    interp_pmax : float, optimal
        maximum value of interpolated pressure axis, by default 1100.0
    interp_dp : float, optimal
        step value of interpolated pressure axis, by default 1.0
    interp_zmin : float, optimal
        minimum value of interpolated z axis, by default 0.0
    interp_zmax : float, optimal
        maximum value of interpolated z axis, by default 20000.0
    interp_dz : float, optimal
        step value of interpolated z axis, by default 10.0

    """

    fpath: Path | list[Path]
    rm_descending: bool = False
    interp: str | None = None
    interp_pmin: float = 50.0
    interp_pmax: float = 1100.0
    interp_dp: float = 1.0
    interp_zmin: float = 0.0
    interp_zmax: float = 20000.0
    interp_dz: float = 10.0
    sonde_no: list[str] = field(init=False, repr=False)
    launch_time: list[datetime] = field(init=False, repr=False)
    sonde: list[Sonde] = field(init=False, repr=False)
    _ds: xr.Dataset = field(init=False, repr=False)
    kwargs: dict | None = None

    def __post_init__(self) -> None:

        if isinstance(self.fpath, Path):
            fpath_list = [self.fpath]

        raw_fpath_list = []
        for f in fpath_list:
            if f.is_dir():
                raw_fpath_list += list(f.glob("F*S*.CSV"))
            else:
                raw_fpath_list.append(f)

        sondes = []

        fpath_loop = (
            raw_fpath_list if len(raw_fpath_list) == 1 else tqdm(raw_fpath_list)
        )
        for f in fpath_loop:
            sondes.append(
                Sonde(
                    f,
                    self.rm_descending,
                    self.interp,
                    self.interp_pmin,
                    self.interp_pmax,
                    self.interp_dp,
                    self.interp_zmin,
                    self.interp_zmax,
                    self.interp_dz,
                    self.kwargs,
                )
            )

        sondes.sort(key=lambda x: x.launch_time)

        object.__setattr__(self, "sonde", sondes)

        # sonde no.
        sonde_no = []
        for s in sondes:
            sonde_no.append(s.sonde_no)

        object.__setattr__(self, "sonde_no", sonde_no)

        # launch time
        launch_time = []
        for s in sondes:
            launch_time.append(s.launch_time)

        object.__setattr__(self, "launch_time", launch_time)

        # create interpolated xr.Dataset
        arr_dict = {}
        if self.interp is not None:
            for old_name, new_name in {
                "Time": "time",
                "Tmp": "tmp",
                "Prs": "p",
                "WD": "wd",
                "WS": "ws",
                "Hum": "rh",
            }.items():
                arr = []

                for s in self.sonde:
                    arr.append(s.df[old_name].values)
                arr_dict[new_name] = np.array(arr)

            ds = xr.Dataset(
                data_vars={
                    "p": (("n", "z"), arr_dict["p"]),
                    "tmp": (("n", "z"), arr_dict["tmp"]),
                    "wd": (("n", "z"), arr_dict["wd"]),
                    "ws": (("n", "z"), arr_dict["ws"]),
                    "rh": (("n", "z"), arr_dict["rh"]),
                    "launch_time": ("n", self.launch_time),
                    "time": (("n", "z"), arr_dict["time"]),
                },
                coords={
                    "n": self.sonde_no,
                    "z": self.sonde[0].df["Height"].values,
                },
            )

            object.__setattr__(self, "_ds", ds)

    @property
    def ds(self) -> xr.Dataset:

        if (self.interp is not None) and len(self) > 1:
            return self._ds
        else:
            raise ValueError

    def __getitem__(self, key) -> Sonde:

        if isinstance(key, int):
            return self.sonde[key]
        elif key in self.sonde_no:
            return self.sonde[self.sonde_no.index(key)]
        else:
            raise KeyError

    def __len__(self) -> int:

        return len(self.sonde)

    def __str__(self) -> str:

        if self.interp is None:
            interp_str = ""
        elif self.interp == "z":
            interp_str = f"interp z: zmin={self.interp_zmin}, zmax={self.interp_zmax}, dz={self.interp_dz}"
        elif self.interp == "p":
            interp_str = f"interp p: pmin={self.interp_pmin}, pmax={self.interp_pmax}, dp={self.interp_dp}"

        nums = ", ".join(f'"{x}"' for x in self.sonde_no)
        return f"""N={len(self)}, sonde_no=[{nums}]
        {interp_str}"""

    def _repr_html_(self):

        if self.interp is None:
            interp_str = ""
        elif self.interp == "z":
            interp_str = f"interp by z: zmin={self.interp_zmin}, zmax={self.interp_zmax}, dz={self.interp_dz}"
        elif self.interp == "p":
            interp_str = f"interp by p: pmin={self.interp_pmin}, pmax={self.interp_pmax}, dp={self.interp_dp}"

        nums = ", ".join(f'"{x}"' for x in self.sonde_no)

        return f"""N={len(self)}, sonde_no=[{nums}]
                      {interp_str}"""
