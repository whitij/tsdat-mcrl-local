from typing import Dict, Union
import xarray as xr
import pandas as pd
from tsdat import DataReader


class OnsetReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        df = pd.read_csv(
            input_key,
            sep=" ",
            header=None,
            names=("date", "time", "temperature", "millivolts", "pH"),
        )
        df["time"] = df["date"] + " " + df["time"]
        return df.to_xarray()


class SamiReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        df = pd.read_csv(
            input_key,
            sep="\t",
            header=0,
        )
        df["time"] = df["DateStr"] + " " + df["TimeStr"]
        df["pH"] = df["pHConstSal"]
        df["temperature"] = df["Temperature C"]
        return df.to_xarray()
