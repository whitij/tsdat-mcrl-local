import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_tidegauge_pipeline():
    config_path = Path("pipelines/tide_gauge/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/tide_gauge/test/data/input/tidegage_20230201_000502.log"
    expected_file = "pipelines/tide_gauge/test/data/expected/tide_gauge.mcrl_pier-ysi_nile_1-5min.a1.20230201.000517.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
