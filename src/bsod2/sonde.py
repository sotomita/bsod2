#! /usr/bin/env python3

from dataclasses import dataclass, field
from datetime import datetime
import io
from metpy.units import units
from pathlib import Path
import pandas as pd
import pint
import warnings

from .qc import get_qc_df, interp_df


@dataclass(frozen=True)
class Sonde:
    """
    Sonde Class

    Parameters
    ----------
    fpath : Path
        path of raw file
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

    fpath: Path
    rm_descending: bool = False
    interp: str | None = None
    interp_pmin: float = 50.0
    interp_pmax: float = 1100.0
    interp_dp: float = 1.0
    interp_zmin: float = 0.0
    interp_zmax: float = 20000.0
    interp_dz: float = 10.0
    sonde_no: str = field(init=False)
    launch_time: datetime = field(init=False)
    product_name: str = field(init=False)
    df: pd.DataFrame = field(init=False)
    kwargs: dict | None = None

    def __post_init__(self) -> None:

        with open(self.fpath, "r") as f:
            raw_data = f.read()

        # parse the header lines
        head_lines = raw_data.splitlines()[:6]
        line1 = head_lines[0].split(",")
        product_name = line1[0]
        __sonde_no = line1[1]
        __launch_time = datetime.strptime(f"{line1[4]} {line1[5]}", "%Y/%m/%d %H:%M:%S")

        object.__setattr__(self, "sonde_no", __sonde_no)
        object.__setattr__(self, "launch_time", __launch_time)
        object.__setattr__(self, "product_name", product_name)

        df = self.__get_df(raw_data)

        object.__setattr__(self, "df", df)

    def __get_df(self, raw_data: str | None = None) -> pd.DataFrame:

        if raw_data is None:
            with open(self.fpath, "r") as f:
                raw_data = f.read()

        # add column name "V" if it is not included in the raw data.
        if ",V,Press0," not in raw_data:
            raw_data = raw_data.replace(",,,Press0,", ",V,Press0,")

        # read the raw data into a DataFrame.
        df = pd.read_csv(io.StringIO(raw_data), skiprows=6, low_memory=False)

        if len(df) == 0:
            warnings.warn(f"No vertical records found in {self.fpath}.")
            return df

        # conduct QC.
        df = get_qc_df(df, self.sonde_no, self.launch_time)

        # remove records with descending height.
        if self.rm_descending or (self.interp is not None):
            df = df[df["Height"].cummax() == df["Height"]].reset_index(drop=True)

        # interpolate the data if specified.
        if self.interp == "p":
            df = interp_df(df, "p", self.interp_pmin, self.interp_pmax, self.interp_dp)
        elif self.interp == "z":
            df = interp_df(df, "z", self.interp_zmin, self.interp_zmax, self.interp_dz)

        # sort by altitude.
        df = df.sort_values("Height")

        return df

    @property
    def time(self) -> pd.Series:
        """time

        Returns
        -------
        pd.Series
            time series
        """

        return self.df["Time"]

    @property
    def lat(self) -> pint.Quantity:
        """latitude

        Returns
        -------
        pint.Quantity
            latitude with units("degrees")
        """

        return self.df["GeodetLat"].values * units.degrees

    @property
    def lon(self) -> pint.Quantity:
        """longitude

        Returns
        -------
        pint.Quantity
            longitude with units ("degrees")
        """

        return self.df["GeodetLon"].values * units.degrees

    @property
    def x(self) -> pint.Quantity:
        """x-displacement from the launch point

        Returns
        -------
        pint.Quantity
            x-displacement with units("m")
        """

        return self.df["Xdistanc"].values * units.meters

    @property
    def y(self) -> pint.Quantity:
        """y-displacement from the launch point

        Returns
        -------
        pint.Quantity
            y-displacement with units("m")
        """

        return self.df["Ydistanc"].values * units.meters

    @property
    def p(self) -> pint.Quantity:
        """pressure

        Returns
        -------
        pint.Quantity
            pressure with units("hPa")
        """

        return self.df["Prs"].values * units.hPa

    @property
    def z(self) -> pint.Quantity:
        """height

        Returns
        -------
        pint.Quantity
            height with units("m")
        """

        return self.df["Height"].values * units.m

    @property
    def t(self) -> pint.Quantity:
        """temperature

        Returns
        -------
        pint.Quantity
            temperature with units("degC")
        """

        return self.df["Tmp"].values * units.degC

    @property
    def rh(self) -> pint.Quantity:
        """relative humidity

        Returns
        -------
        pint.Quantity
            relative humidity with units("percent")
        """

        return self.df["Hum"].values * units.percent

    @property
    def wd(self) -> pint.Quantity:
        """wind direction

        Returns
        -------
        pint.Quantity
            wind direction with units("degrees")
        """

        return self.df["WD"].values * units.degrees

    @property
    def ws(self) -> pint.Quantity:
        """wind speed

        Returns
        -------
        pint.Quantity
            wind speed with units("m/s")
        """

        return self.df["WS"].values * units.meter / units.second

    def __len__(self) -> int:

        return len(self.df)

    def save_df(self, fpath: Path) -> None:
        """save as csv

        Parameters
        ----------
        fpath : Path
            file path the df saved
        """

        self.df.to_csv(fpath, index=False)

    def __str__(self) -> str:

        return f"Sonde(sonde_no={self.sonde_no}, launch_time={self.launch_time}, product_name={self.product_name}, num_records={len(self.df)})"
