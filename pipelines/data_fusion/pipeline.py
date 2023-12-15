import numpy as np
import xarray as xr

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from tsdat import TransformationPipeline, get_start_date_and_time_str


class DataFusion(TransformationPipeline):
    """---------------------------------------------------------------------------------
    This is an example pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area
        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        location = self.dataset_config.attrs.location_id
        datastream: str = self.dataset_config.attrs.datastream
        date, time = get_start_date_and_time_str(dataset)
        save_kwargs = {
            "root_dir": "storage/root",
            "location_id": location,
            "datastream": datastream,
            "year": date[:4],
            "month": date[4:6],
            "day": date[6:],
        }

        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        # Physical
        fig, ax = plt.subplots(4, 1)
        ax[0].plot(dataset.time, dataset["water_level"])
        ax[0].set(ylabel="Water Level [m]")
        ax[1].plot(dataset.time, dataset["temp"])
        ax[1].set(ylabel="Water Temp [deg C]")
        ax[2].plot(dataset.time, dataset["do"])
        ax[2].set(ylabel="Dissolved Oxygen [mg/L]")
        ax[3].plot(dataset.time, dataset["salinity"])
        ax[3].set(ylabel="Salinity [psu]")

        # fig.suptitle(f"Example Variable at {location} on {date} {time}")
        plot_file = self.get_ancillary_filepath(title="ctd", **save_kwargs)
        fig.savefig(plot_file)
        plt.close(fig)

        # # Biological
        # fig, ax = plt.subplots(4)
        # ax[0].plot(dataset.time, dataset["water_level"])
        # ax[0].set(ylabel="Water Level [m]")
        # ax[1].plot(dataset.time, dataset["cdom"])
        # ax[1].set(ylabel="CDOM [ppb]")
        # ax[2].plot(dataset.time, dataset["phycoerythrin"])
        # ax[2].set(ylabel="Phycoerythrin [ppb]")
        # ax[3].plot(dataset.time, dataset["chlorophyll"])
        # ax[3].set(ylabel="Chlorophyll [ug/L]")

        # plot_file = self.get_ancillary_filepath(title="cdom", **save_kwargs)
        # fig.savefig(plot_file)
        # plt.close(fig)

        # # Water level, water speed, sound pressure level
        # fig, ax = plt.subplots(3)
        # ax[0].plot(dataset.time, dataset["water_level"])
        # ax[0].set(ylabel="Water Level [m]")
        # ax[1].scatter(dataset.time.values, dataset["U_mag"].mean("range"))
        # ax[1].set(ylabel="Average Water Speed [m/s]")
        # ax[2].scatter(dataset.time.values, dataset["SPL"])
        # ax[2].set(ylabel="Sound Pressure Level [dB re 1 uPa]")

        # plot_file = self.get_ancillary_filepath(title="water", **save_kwargs)
        # fig.savefig(plot_file)
        # plt.close(fig)

        # # Current
        # U_mag = dataset["U_mag"].dropna("time")
        # fig, ax = plt.subplots(2)
        # magn = ax[0].pcolormesh(
        #     U_mag["time"].values,
        #     U_mag["range"].values,
        #     U_mag.T,
        #     cmap="Blues",
        #     shading="nearest",
        # )
        # ax[0].set_ylabel(r"Range [m]")
        # fig.colorbar(magn, ax=ax[0], label=r"Current Speed (m s$^{-1}$)")

        # U_dir = dataset["U_dir"].dropna("time")
        # dirc = ax[1].pcolormesh(
        #     U_dir["time"].values,
        #     U_dir["range"].values,
        #     U_dir.T,
        #     cmap="twilight",
        #     shading="nearest",
        # )
        # ax[1].set_ylabel(r"Range [m]")
        # fig.colorbar(dirc, ax=ax[1], label=r"Direction [deg from N]")

        # plot_file = self.get_ancillary_filepath(title="current", **save_kwargs)
        # fig.savefig(plot_file)
        # plt.close(fig)
