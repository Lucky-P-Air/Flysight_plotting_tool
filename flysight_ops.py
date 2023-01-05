# -*- coding: utf-8 -*-
"""
Logic for reading & manipulating Flysight data
"""
import typing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import flysight_plotly as fp
from concurrent.futures import ThreadPoolExecutor  # , as_completed


class FlysightTool:
    def __init__(self, gui_options: dict):
        self.options = gui_options
        self.track_builder = FlysightTrackBuilder(gui_options)
        self.track_builder.build()
        self.track: FlysightTrack = self.track_builder.get_FlysightTrack()
        # self.track_plotter = FlysightPlotter(self.track)
        # FlysightPlotter is a planned breakout module for plotting
        # self.track.plot_track()  # placeholder brute-force plotter
        self.track.plot_plotly()  # placeholder brute-force plotter
        # Add a cache for previously loaded tracks within session


class FlysightReader:
    def __init__(self, gui_options: dict):
        """
        Reader object for Flysight CSV files, configured per options set in GUI
        (Could replace with a single function if class isn't expanded further)
        :param gui_options: dict: Options from GUI for reading in data
        """
        self.options = gui_options
        self.filename = self.options["track_filename"]
        self.HEADER_COLS = [
            "time",
            "lat",
            "lon",
            "hMSL",
            "velN",
            "velE",
            "velD",
            "hAcc",
            "vAcc",
            "sAcc",
            "heading",
            "cAcc",
        ]

    @property
    def flysightcsv(self) -> pd.DataFrame:
        """Read in flysight data, omit 2nd row of dimensional units, reset index.
        :return: DataFrame"""
        raw = pd.read_csv(
            self.filename,
            parse_dates=["time"],
            comment="(",
            usecols=self.HEADER_COLS,
        )
        # OPTIONAL: read in only the units of flysight file
        # units_row = pd.read_csv(filename, nrows = 2, usecols=header_cols)
        raw.drop(labels=[0], axis=0, inplace=True)  # Delete row of units
        return raw.reset_index(drop=True)


class FlysightTrackBuilder:
    """Builder class used to build up FlysightTrack from raw Flysight csv
    recording"""

    SPEED_START = 2  # m/s. Threshold for identifying jump start
    SPEED_END = 0.5  # m/s. Threshold for identifying jump end

    def __init__(self, gui_options: dict):
        """
        Initialize builder based on GUI options
        :param gui_options: dict: Options from GUI for processing in data
        """
        self.reader = FlysightReader(gui_options)
        self.df = self.reader.flysightcsv
        self.options = gui_options
        self.HEADER_COLS = self.reader.HEADER_COLS

    def add_elev(self, system="metric"):
        """Download ground elevation from USGS National Map-Elevation Point
        Query Service API (https://nationalmap.gov/epqs/)
        API requires Latitude and longitude must be provided in decimal degrees.
        FlysightTrack DataFrame has 'lat' and 'lon' columns for
        latitude and longitude, respectively.
        :param system: str: ["metric" | "english"] : System of unit measurement
        """
        # Could be modified to take a list of tuples, or list of lists, or 2D array
        # Could be written to perform a single request for a single lat-lon combo.

        units = {"metric": "Meters", "english": "Feet"}[system.lower()]

        if self.options["elev_bool"]:
            url = "https://nationalmap.gov/epqs/pqs.php?"

            def query_usgs(address):
                """API query to USGS for ground elevation at a single point
                :param address: str: URL including with latitude, longitude
                & units"""
                USGS = "USGS_Elevation_Point_Query_Service"
                EL_QUERY = "Elevation_Query"
                q_result = requests.get(address)
                return q_result.json()[USGS][EL_QUERY]["Elevation"]

            url_list = [
                f"{url}x={point.lon}&y={point.lat}&units={units}&output=json"
                for _, point in self.df.iterrows()
            ]

            with ThreadPoolExecutor() as executor:
                elev_series = executor.map(query_usgs, url_list)

            self.df["ground_elev"] = list(elev_series)
            self.append_headers(["ground_elev"])

    def append_headers(self, new_cols: typing.Sequence):
        """Add DataFrame header columns to FlysightTrack DataFrame.
        :param new_cols: list | tuple: List of new column headers as strings"""
        for col in new_cols:
            self.HEADER_COLS.append(col)
        # TO-DO: Add validation for len(self.HEADER_COLS) == len(self.df.columns)

    def build(self):
        """Sequence of steps to convert raw Flysight recording to a more
        complete Flysight Track with additional processed data \n
        1. Calculate velocities (horizontal, vertical, total, glide-ratio)\n
        2. Identify, isolate, and crop jump from the full recording \n
        3. Reset time values for jump to begin a zero seconds
        4. OPTIONAL: Add ground elevation data to DataFrame for flight-path
        """
        self.calc_vel()
        self.crop_jump()
        self.convert_time()
        self.add_elev()

    def calc_vel(self):
        """Calculate horizontal, total speeds, and glide-ratio from
        velN, velE, velD, adds to FlysightTrack.
        Add corresponding columns 'velH', 'velT', 'gr', to DataFrame"""
        horiz_speed = np.sqrt(self.df["velN"] ** 2 + self.df["velE"] ** 2)
        vert_speed = self.df["velD"]
        total_speed = np.sqrt(horiz_speed**2 + vert_speed**2)
        self.df["velH"] = horiz_speed
        self.df["velT"] = total_speed
        self.df["gr"] = self.df["velH"] / self.df["velD"]  # glide ratio
        self.append_headers(["velH", "velT", "gr"])

    def crop_jump(self, speed_start: float = SPEED_START, speed_end: float = SPEED_END):
        """Trim the Flysight file to only include the jump data and remove
        extraneous data from moving around before and after jump

        Identifying the "jump" from the noise checks for:
            1. Points in time when the total speed is greater than threshold speed
            2. Jump is cutoff after total speed drops below 0.5 m/s
        :param speed_start: float: Speed threshold to identify start of jump
        :param speed_end: float: Speed threshold to identify end of jump
        """
        df_at_speed = self.df[self.df["velT"] >= speed_start]
        df_at_speed.reset_index(inplace=True)

        # Capture index of original df for when speed threshold is breached
        start_ind = df_at_speed.loc[0, "index"]

        df_after_exit = self.df.iloc[start_ind:]
        df_after_landing = df_after_exit[df_after_exit["velT"] <= speed_end]

        finish_ind = df_after_landing.reset_index().loc[0, "index"]
        # Jump dataframe begins 10 time steps before speed breach, ~ 2 seconds
        jump_df = self.df.iloc[(int(start_ind) - 10) : int(finish_ind)]
        self.df = jump_df.copy()

    def convert_time(self):
        """Calculate time lapsed, in seconds, of the jump and add 'time_lapsed'
        column to DataFrame from 0 seconds until landing
        """
        start = self.df["time"].iloc[0]
        end = self.df["time"].iloc[-1]
        duration = (end - start).seconds  # duration in seconds
        self.df["time_elapsed"] = np.linspace(0, duration, len(self.df))
        self.append_headers(["time_elapsed"])

    def get_FlysightTrack(self):
        """Return the processed FlysightTrack"""
        ftrack = FlysightTrack(self)
        self.reset()
        return ftrack

    def reset(self):
        """Reset the working FlysightTrack being built"""
        self.df = None
        self.options = None
        self.HEADER_COLS = None


class FlysightTrack:
    """Flysight Track containing DataFrame augmented with additional fields
    & data beyond the CSV"""

    def __init__(self, built_track: FlysightTrackBuilder):
        self.df = built_track.df
        self.options = built_track.options

    def plot_track(self):
        """Placeholder function for testing app logic up until plotting stage.
        Placeholder plotting before creating breakout FlysightPlotter module"""

        def build_figure(df, title=""):
            """Blob of procedures to generate matplotlib figure with plotted
            Flysight track
            :param df: DataFrame: FlysightTrack's DataFrame
            :param title: str: {Optional} Title of the track
            """
            if plt.fignum_exists(1):
                plt.close()
            fig = plt.figure(1)
            ax1 = fig.subplots()

            line_h = ax1.plot(
                df["time_elapsed"],
                df["velH"],
                color="blue",
                label="Horiz V",
            )
            line_v = ax1.plot(
                df["time_elapsed"],
                df["velD"],
                color="green",
                label="Vert V",
            )
            line_total = ax1.plot(
                df["time_elapsed"],
                df["velT"],
                color="red",
                label="Total V",
            )
            ax1.set_xlabel("Time Elapsed (s)")
            ax1.set_ylabel("Velocity (m/s)")  # TO-DO: toggle units
            ax1.set_title("{} Jump Data".format(title))
            ax1.grid()

            ax2 = ax1.twinx()
            line_hmsl = ax2.plot(
                df["time_elapsed"],
                df["hMSL"],
                color="black",
                label="H (MSL)",
            )
            ax2.set_ylabel("Height-MSL (m)")

            lines = line_h + line_v + line_total + line_hmsl

            if "ground_elev" in df.columns:
                line_gelev = ax2.plot(
                    df["time_elapsed"],
                    df["ground_elev"],
                    color="brown",
                    label="Ground Elevation",
                )
                ax2.fill_between(
                    df["time_elapsed"],
                    df["ground_elev"],
                    df["ground_elev"].min(),
                    color="brown",
                    alpha=0.2,
                )
                lines += line_gelev

            labs = [line.get_label() for line in lines]
            # fig.legend(['Horiz V', 'Vert V', 'Total V', 'H-MSL'], loc=1)
            ax1.legend(lines, labs, loc=1)

        print(self.df.head())
        print(self.options["track_filename"])
        print(self.options["track_title"])
        print(self.options["elev_bool"])
        build_figure(self.df, self.options["track_title"])
        plt.show()

    def plot_plotly(self):
        """Use Plotly library to generate a visualization of dataframe"""
        # fp.make_plotly(self.df, self.options)
        fp.make_dash(self)


# if __name__ == '__main__':
