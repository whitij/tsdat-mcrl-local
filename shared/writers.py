import shutil
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from pydantic import BaseModel, Extra
from typing import Any, Dict, List, Optional
from mhkit.dolfyn.time import dt642epoch

from tsdat import FileWriter
from tsdat.tstring import Template
from tsdat.config.storage import StorageConfig
from tsdat.config.utils import recursive_instantiate
from tsdat.tstring import Template


def create_storage_class(data_folder):
    """----------------------------------------------------------------------------
    Creates generic Tsdat storage class

    Args:
        data_folder (str): Data folder, typically file format, for use in data
        filepath

    Returns:
        tsdat.StorageConfig: Storage model configuration
    ----------------------------------------------------------------------------"""
    parameters = {
        "data_storage_path": Path("{location_id}/{datastream}")
        / Path(f"{data_folder}")
        / Path("{year}/{month}/{day}"),
    }
    storage_model = StorageConfig(
        classname="tsdat.io.storage.FileSystem", parameters=parameters
    )
    return storage_model


def write_raw(input_key, config):
    """----------------------------------------------------------------------------
    Moves the raw file from the read location to the final storage location. Called
    from the tsdat dispatcher in registry.py

    Args:
        input_key (str): Raw file location
        config (tsdat.PipelineConfig): Pipeline configuration

    ----------------------------------------------------------------------------"""
    storage_model = create_storage_class("raw")
    storage = recursive_instantiate(storage_model)

    # Can get datastream from pipeline config
    # Can get year/month/day from input filename b/c log files are always listed in UTC
    filename = input_key.replace("\\", "/").split("/")[-1]
    date = filename.split("_")[-2]
    year = date[:4]
    month = date[4:6]
    day = date[6:8]

    # Manually set up save configuration and save raw file
    data_stub_path = Template(storage.parameters.data_storage_path.as_posix())
    datastream_dir = Path(
        data_stub_path.substitute(
            dict(
                location_id=config.dataset.attrs.location_id,
                datastream=config.dataset.attrs.datastream,
                year=year,
                month=month,
                day=day,
            ),
        )
    )
    filepath = Path("storage/root") / datastream_dir / filename
    filepath.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(input_key, filepath)  # save file by moving it from source
    # Using 'copy' on tsdat-mcrl-local, 'move' on tsdat-mcrl


def write_parquet(dataset):
    """----------------------------------------------------------------------------
    Saves pipeline data in a parquet format using a custom writer

    Args:
        dataset (xarray.dataset): Pipeline dataset

    ----------------------------------------------------------------------------"""
    storage_model = create_storage_class("parquet")
    storage = recursive_instantiate(storage_model)
    storage.handler.writer = MCRLdataParquetWriter()
    storage.save_data(dataset)


class MCRLdataParquetWriter(FileWriter):
    """---------------------------------------------------------------------------------
    Writes the dataset to a parquet file.

    Converts a `xr.Dataset` object to a pandas `DataFrame` and saves the result to a
    parquet file using `pd.DataFrame.to_parquet()`. Properties under the
    `to_parquet_kwargs` parameter are passed to `pd.DataFrame.to_parquet()` as keyword
    arguments.

    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        dim_order: Optional[List[str]] = None
        to_parquet_kwargs: Dict[str, Any] = {}
        to_parquet_kwargs.update(dict(engine="pyarrow", use_dictionary=False))

    parameters: Parameters = Parameters()
    file_extension: str = "parquet"

    def write(
        self, dataset: xr.Dataset, filepath: Optional[Path] = None, **kwargs: Any
    ) -> None:
        ds = dataset
        if len(ds.dims) > 1:
            if "iclisten" in ds.datastream:  # special handling for hydrophone
                df = pd.DataFrame(
                    {"time": ds["time"], "spl": ds["SPL"], "spl_qc": ds["qc_SPL"]}
                )
            elif "adcp" in ds.datastream:  # special handling for ADCP
                maxU = ds["U_mag"].max(dim="range")
                qc = (
                    ds["qc_U_mag"]
                    .where(ds["U_mag"] == ds["U_mag"].max(dim="range"))
                    .sum(dim="range")
                )
                qc_list = [int(each) for each in qc]
                df = pd.DataFrame(
                    {"time": ds["time"], "maxU": maxU, "maxU_qc": qc_list}
                )
            elif "pco2" in ds.datastream:  # special handling for pCO2 sensor
                pco2_water = ds["pco2_water"].values
                qc_pco2_water = ds["qc_pco2_water"].values
                pco2_air = ds["pco2_air"].values
                qc_pco2_air = ds["qc_pco2_air"].values
                o2_water = ds["o2_water"].values
                qc_o2_water = ds["qc_o2_water"].values
                o2_air = ds["o2_air"].values
                qc_o2_air = ds["qc_o2_air"].values
                df = pd.DataFrame(
                    {
                        "time": ds["time"],
                        "pco2_water": pco2_water,
                        "qc_pco2_water": qc_pco2_water,
                        "pco2_air": pco2_air,
                        "qc_pco2_air": qc_pco2_air,
                        "o2_water": o2_water,
                        "qc_o2_water": qc_o2_water,
                        "o2_air": o2_air,
                        "qc_o2_air": qc_o2_air,
                    }
                )
            else:
                raise Warning(
                    "Dataset has more than one dimension and no exception for parquet."
                )
        else:
            df = ds.to_dataframe(self.parameters.dim_order)  # type: ignore

        # Need to iterate through columns and force integer data types for qc flag
        for col in df.columns:
            if "qc" in col:
                df[col] = pd.to_numeric(df[col])
            if "time" in col:
                df[col] = (dt642epoch(df[col].values) * 1000).astype(np.int64)

        # Manually convert time to int with milliseconds for aws athena
        if not hasattr(df, "time"):
            df["time"] = (dt642epoch(df.index.values) * 1000).astype(np.int64)
            df = df.set_index("time")

        df.to_parquet(filepath, **self.parameters.to_parquet_kwargs)
