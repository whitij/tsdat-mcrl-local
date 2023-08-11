import shutil
import pandas as pd
import xarray as xr
from pathlib import Path
from pydantic import BaseModel, Extra
from typing import Any, Dict, List, Optional

from tsdat import FileWriter
from tsdat.tstring import Template
from tsdat.config.storage import StorageConfig
from tsdat.config.utils import recursive_instantiate


def create_storage_class(instrument, data_folder):
    """----------------------------------------------------------------------------
    Creates generic Tsdat storage class

    Args:
        instrument (str): Instrument handle, for use in data filepath
        data_folder (str): Data folder, typically file format, for use in datafilepath

    Returns:
        tsdat.StorageConfig: Storage model configuration
    ----------------------------------------------------------------------------"""
    parameters = {
        "storage_root": Path.cwd() / "storage" / instrument,
        "data_folder": data_folder,
        "data_storage_path": Path(
            "{storage_root}/{datastream}/{data_folder}/{year}/{month}/{day}"
        ),
    }
    storage_model = StorageConfig(
        classname="tsdat.io.storage.FileSystem", parameters=parameters
    )
    return storage_model


def write_raw(input_key, config, instrument):
    """----------------------------------------------------------------------------
    Moves the raw file from the read location to the final storage location. Called
    from the tsdat dispatcher in registry.py

    Args:
        input_key (str): Raw file location
        config (tsdat.PipelineConfig): Pipeline configuration
        instrument (str): Instrument handle, for use in data filepath

    ----------------------------------------------------------------------------"""
    storage_model = create_storage_class(instrument, "raw")
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
                datastream=config.dataset.attrs.datastream,
                year=year,
                month=month,
                day=day,
            ),
        )
    )
    filepath = datastream_dir / filename
    filepath.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(input_key, filepath)  # save file by moving it from source
    # Using 'copy' on tsdat-mcrl-local, 'move' on tsdat-mcrl


def write_parquet(dataset, instrument):
    """----------------------------------------------------------------------------
    Saves pipeline data in a parquet format using a custom writer

    Args:
        dataset (xarray.dataset): Pipeline dataset
        instrument (str): Instrument handle, for use in data filepath

    ----------------------------------------------------------------------------"""
    storage_model = create_storage_class(instrument, "parquet")
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
    file_extension: str = ".parquet"

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
            else:
                raise Warning(
                    "Dataset has more than one dimension and no exception for parquet."
                )
                return
        else:
            df = ds.to_dataframe(self.parameters.dim_order)  # type: ignore

        # Need to iterate through columns and force integer data types for qc flag
        for col in df.columns:
            if "qc" in col:
                df[col] = pd.to_numeric(df[col])

        # print(df)
        df.to_parquet(filepath, **self.parameters.to_parquet_kwargs)
