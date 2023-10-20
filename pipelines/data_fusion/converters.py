"""-------------------------------------------------------------------------------------
I wrote this data converter to transpose any multi-dimensional variables whose first 
dimension is not time. As one can see it's quite simple; however, this data converter 
fails to work with the VAP because tsdat automatically grabs the variable and any 
associated qc variable. Since one doesn't have access to the qc variable in the pipeline
 it's not currently possible to tranpose it, and the pipeline won't perform properly.

Therefore, it's better to go back and transpose any variables that don't have time as 
the first variable in the ingest-pipeline.
-------------------------------------------------------------------------------------"""

from typing import Any

import xarray as xr
from tsdat import DataConverter, DatasetConfig, RetrievedDataset


class DimensionTranspose(DataConverter):
    """---------------------------------------------------------------------------------
    Custom DataConverter that can be used to preprocess input datasets and convert them
    into a suitable format for downstream processing.

    Tranposes a variable whose first dimension is not time, which tsdat requires.
    ---------------------------------------------------------------------------------"""

    def convert(
        self,
        data: xr.DataArray,
        variable_name: str,
        dataset_config: DatasetConfig,
        retrieved_dataset: RetrievedDataset,
        **kwargs: Any,
    ) -> xr.DataArray:
        """----------------------------------------------------------------------------
        Applies a custom conversion to the retrieved data.

        Args:
            data (xr.DataArray): The DataArray corresponding with the retrieved data
                variable to convert.
            variable_name (str): The name of the variable to convert.
            dataset_config (DatasetConfig): The output dataset configuration.
            retrieved_dataset (RetrievedDataset): The retrieved dataset structure.

        Returns:
            xr.DataArray: The converted DataArray.

        ----------------------------------------------------------------------------"""

        return data.T
