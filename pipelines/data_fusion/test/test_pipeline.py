import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


# def test_data_fusion_pipeline():
#     config_path = Path("pipelines/data_fusion/config/pipeline.yaml")
#     config = PipelineConfig.from_yaml(config_path)
#     pipeline = config.instantiate_pipeline()

#     start = "20230401.000000"
#     end = "20230402.000000"
#     expected_file = "pipelines/data_fusion/test/data/expected/mcrl.data_fusion.b1.20230401.000000.nc"

#     dataset = pipeline.run(inputs=[start, end])
#     expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
#     assert_close(dataset, expected, check_attrs=False)
