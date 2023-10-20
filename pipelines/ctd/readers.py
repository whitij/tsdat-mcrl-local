from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
from tsdat import DataReader


class CTDReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        df = pd.read_csv(
            input_key,
            sep=",| ",
            header=None,
            engine="python",
            names=(
                "date",
                "time",
                "ms",
                "tlabel",
                "temp",
                "dolabel",
                "do",
                "slabel",
                "salinity",
                "clabel",
                "conductivity",
            ),
        )
        df["time"] = df["date"] + " " + df["time"] + "." + [str(x) for x in df["ms"]]
        df = df.drop(columns=["tlabel", "slabel", "dolabel", "clabel", "date", "ms"])
        return df.to_xarray()
