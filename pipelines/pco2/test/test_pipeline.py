import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_pco2_pipeline():
    config_path = Path("pipelines/pco2/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/pco2/test/data/input/pco2_raw_20231003_060000.nc"
    expected_file = "pipelines/pco2/test/data/expected/pco2.mcrl_pier-battelle_seaology_1-3hr.a1.20231003.060000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
