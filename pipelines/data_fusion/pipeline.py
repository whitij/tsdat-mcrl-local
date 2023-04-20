import numpy as np
import xarray as xr

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from tsdat import TransformationPipeline, get_filename, get_start_date_and_time_str


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

        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        with self.storage.uploadable_dir(datastream) as tmp_dir:
            # Physical
            fig, ax = plt.subplots(4)
            ax[0].plot(dataset.time, dataset["water_level"])
            ax[0].set(ylabel="Water Level [m]")
            ax[1].plot(dataset.time, dataset["temp"])
            ax[1].set(ylabel="Water Temp [deg C]")
            ax[2].plot(dataset.time, dataset["do"])
            ax[2].set(ylabel="Dissolved Oxygen [mg/L]")
            ax[3].plot(dataset.time, dataset["salinity"])
            ax[3].set(ylabel="Salinity [psu]")

            # fig.suptitle(f"Example Variable at {location} on {date} {time}")
            plot_file = get_filename(dataset, title="ctd", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)

            # Biological
            fig, ax = plt.subplots(4)
            ax[0].plot(dataset.time, dataset["water_level"])
            ax[0].set(ylabel="Water Level [m]")
            ax[1].plot(dataset.time, dataset["cdom"])
            ax[1].set(ylabel="CDOM [ppb]")
            ax[2].plot(dataset.time, dataset["phycoerythrin"])
            ax[2].set(ylabel="Phycoerythrin [ppb]")
            ax[3].plot(dataset.time, dataset["chlorophyll"])
            ax[3].set(ylabel="Chlorophyll [ug/L]")

            plot_file = get_filename(dataset, title="cdom", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)

            # Water level, water speed, sound pressure level
            fig, ax = plt.subplots(3)
            ax[0].plot(dataset.time, dataset["water_level"])
            ax[0].set(ylabel="Water Level [m]")
            ax[1].scatter(dataset.time.values, dataset["U_mag"].mean("range"))
            ax[1].set(ylabel="Average Water Speed [m/s]")
            ax[2].scatter(dataset.time.values, dataset["SPL"])
            ax[2].set(ylabel="Sound Pressure Level [dB re 1 uPa]")

            plot_file = get_filename(dataset, title="water", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)

            # Current
            U_mag = dataset["U_mag"].dropna("time")
            fig, ax = plt.subplots(2)
            magn = ax[0].pcolormesh(
                U_mag["time"].values,
                U_mag["range"].values,
                U_mag.T,
                cmap="Blues",
                shading="nearest",
            )
            ax[0].set_ylabel(r"Range [m]")
            fig.colorbar(magn, ax=ax[0], label=r"Current Speed (m s$^{-1}$)")

            U_dir = dataset["U_dir"].dropna("time")
            dirc = ax[1].pcolormesh(
                U_dir["time"].values,
                U_dir["range"].values,
                U_dir.T,
                cmap="twilight",
                shading="nearest",
            )
            ax[1].set_ylabel(r"Range [m]")
            fig.colorbar(dirc, ax=ax[1], label=r"Direction [deg from N]")

            plot_file = get_filename(dataset, title="current", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)

            # Acoustic Spectra
            def plot_spectra_by_color(auto_spectra, U_mag, U_max, fig, ax):
                U = U_mag.values

                # Average spectra
                speed_bins = np.arange(0, U_max, 0.1)
                time = [t for t in auto_spectra.dims if "time" in t][0]
                S_group = auto_spectra.assign_coords({time: U}).rename({time: "speed"})
                S = S_group.groupby_bins("speed", speed_bins).mean()

                # create colormap by speed
                norm = plt.Normalize(vmin=0, vmax=2.0)
                colors = plt.cm.turbo(norm(speed_bins))
                sm = plt.cm.ScalarMappable(cmap="turbo", norm=norm)

                for i in range(len(speed_bins) - 1):
                    ax.plot(auto_spectra["frequency"], S[i], c=colors[i])

                ax.grid()
                ax.set(xscale="log", ylim=(0, 30))
                return ax, sm

            fig, ax = plt.subplots(1, 2)
            ax[0], sm = plot_spectra_by_color(
                dataset["spectra"],
                dataset["U_mag"].mean("range"),
                dataset["U_mag"].max() - 0.1,
                fig,
                ax[0],
            )
            fig.colorbar(sm, ax=ax[0], label=r"Flow Speed [m/s]")
            ax[0].set(xlabel="Frequency [Hz]", ylabel=r"SPL [dB re 1 uPa]")

            SPL_spectra = dataset["spectra"].dropna("time")
            spl = ax[1].pcolormesh(
                SPL_spectra["time"].values,
                SPL_spectra["frequency"].values,
                SPL_spectra.T,
                cmap="inferno",
                shading="nearest",
            )
            ax[1].set(yscale="log", ylim=(100, 1e5), ylabel=r"Frequency [Hz]")
            fig.colorbar(spl, ax=ax[1], label=r"SPL [dB re 1 uPa]")

            plot_file = get_filename(dataset, title="sound", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)

        # TODO: Better x-axis ticks:
        # Set the x-axis to have ticks spaced by the hour
        # hours = mdates.HourLocator(interval=1)
        # ax.xaxis.set_major_locator(hours)

        # # Set the format of the x-axis tick labels
        # time_format = mdates.DateFormatter('%H:%M')
        # ax.xaxis.set_major_formatter(time_format)
        pass
