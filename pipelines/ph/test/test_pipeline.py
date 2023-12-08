import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_ph_pipeline_onset():
    config_path = Path("pipelines/ph/config/pipeline_onset.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/ph/test/data/input/ph_20210813_160005.txt"
    expected_file = "pipelines/ph/test/data/expected/ph_.mcrl_pier-onset_mx2501_1-5min.a1.20210813.154505.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)


def test_ph_pipeline_isami():
    config_path = Path("pipelines/ph/config/pipeline_isami.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/ph/test/data/input/SAMI_Data_Export_20230921_212501.txt"
    expected_file = "pipelines/ph/test/data/expected/ph.mcrl_pier-isami_ph_1-15min.a1.20230921.212501.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
