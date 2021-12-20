# -*- coding: utf-8 -*-
"""
Wingsuit Base Jump Flysight Data Interpreter

Planning to:
    DONE Read in Flysight CSV
    DONE Calculate Additional Data (Total Speed, etc)
    DONE Extract the jump from the superfluous noise data
    DONE Calculate Time Elapsed
    DONE Retrieve Ground Elevation Data from USGS,
    - Calculate horizontal distance covered
    - Employ threading for get_elev()
    - Plot key data (altitude, different speeds, gr) over jump duration
    - Plot ground elevation underneath it all (with transparency)
    - Plot 4D flight data with error bars & color changing for speed & gr
    - Streamlit to deploy this to webpage
    - Plotly/Dash for interactive plots
@author: mattc
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from collections import OrderedDict
# from datetime import datetime
from tkinter import Tk
from tkinter import filedialog

# Reference Notes for development
# Converting GPS coordinates:
# Geopy (https://pypi.org/project/geopy/)
# LatLon (https://pypi.org/project/LatLon/)


class Flysight:
    # Design this class with Object Oriented SOLID Design (specifically L)
    pass


class Jump(Flysight):
    pass


def calc_vel(df_in):
    """Calculate horizontal and total speeds from velN, velE, velD.
    Input is a dataframe"""
    df = df_in.copy()
    horiz_speed = np.sqrt(df['velN']**2 + df['velE']**2)  # horizontal speed
    vert_speed = df['velD']
    total_speed = np.sqrt(horiz_speed**2 + vert_speed**2)
    df['velH'] = horiz_speed
    df['velT'] = total_speed
    df['gr'] = df['velH'] / df['velD']   # glide ratio
    return df


def convert_time(df_in):
    """Calculate time lapsed, in seconds, of the flight/jump/DataFrame and
    add 'time_lapsed' column to dataframe from 0 seconds to [duration] seconds
    """
    df = df_in.copy()
    start = df['time'].iloc[0]
    end = df['time'].iloc[-1]
    duration = (end - start).seconds  # duration in seconds
    df['time_elapsed'] = np.linspace(0, duration, len(df))
    return df


def find_jump(df, speed=2):
    """Trim the Flysight file to only include the jump data and remove
    extraneous data from moving around before and after jump
    Input is a dataframe.
    Optional argument is a threshold total-speed (int or float) in m/s, used
    to check for "start" of jump by reaching given threshold total-speed (m/s).
    Default is 2 m/s

    Identifying the "jump" from the noise checks for:
        1. Points in time where the total speed is greater than threshold speed
        2. Jump is cutoff after total speed drops below 0.5 m/s
    """
    # df = df2.copy()
    # horiz_speed = np.sqrt(df['velN']**2 + df['velE']**2)  # horizontal speed
    # vert_speed = df['velD']
    # total_speed = np.sqrt(horiz_speed**2 + vert_speed**2)
    # df['velT'] = total_speed

    df_at_speed = df[df['velT'] >= 2]
    df_at_speed.reset_index(inplace=True)

    # Capture time_elapsed in seconds for when speed threshold is breached
    # Capture index of original df for when speed threshold is breached
    start_ind = df_at_speed.loc[0, 'index']

    df_after_exit = df.iloc[(start_ind):]
    df_after_landing = df_after_exit[df_after_exit['velT'] <= 0.5]

    finish_ind = df_after_landing.reset_index().loc[0, 'index']
    # Jump dataframe begins 10 time steps before speed breach, ~ 2 seconds
    jump_df = df.iloc[(int(start_ind) - 10):int(finish_ind)]
    return jump_df


def get_elev(df, units='Meters'):
    # Could be modified to take a list of tuples, or list of lists, or 2D array
    # Could be written to perform a single request for a single lat-lon combo.
    """GET Elevation from USGS National Map-Elevation Point Query Service API
    (https://nationalmap.gov/epqs/)
    Input is a dataframe, within which there are 'lat' and 'lon' columns for
    latitude and longitude, respectively.
    Latitude and longitude must be provided in decimal degrees

    Optional positional argument is units as either 'Meters' or 'Feet'.
    Default is Meters
    """
    # Apply input checkingn for 'meters'/'feet'
    if units.lower() in ['feet', 'ft', 'f']:
        units = 'Feet'
    else:
        units = 'Meters'

    elev_series = OrderedDict()
    for i, point in df.iterrows():
        url = "https://nationalmap.gov/epqs/pqs.php?"
        args = "x={}&y={}&units={}&output=json".format(point.lon,
                                                       point.lat,
                                                       units)
        api_url = url + args
        elev_response = requests.get(api_url)
        usgs = 'USGS_Elevation_Point_Query_Service'
        el_query = 'Elevation_Query'
        elevation = elev_response.json()[usgs][el_query]['Elevation']
        elev_series[i] = elevation
    df2 = df.copy()
    df2['ground_elev'] = elev_series.values()
    return df2


def load_flysight(filename):
    """Read in flysight data, omit 2nd row of dimensional units, reset index"""
    header_cols = ['time', 'lat', 'lon', 'hMSL', 'velN', 'velE', 'velD',
                   'hAcc', 'vAcc', 'sAcc', 'heading', 'cAcc']
    raw = pd.read_csv(filename, parse_dates=['time'],
                      comment='(', usecols=header_cols)
    raw.drop(labels=[0], axis=0, inplace=True)  # Delete row of units
    raw = raw.reset_index(drop=True)
    # OPTIONAL: read in units row only to
    # units_row = pd.read_csv(filename, nrows = 2, usecols=header_cols)
    return raw


def open_file():
    """Explorer Window to locate & open Flysight raw CSV file"""
    root = Tk()
    filename = filedialog.askopenfilename(
                initialdir='C:/Users/mattc/Documents/Flysight',
                title='Select a Flysight CSV file',
                filetypes=(('CSV Files', "*.csv*"), ("all files", "*.*")))
    # Close unnecessary tkinter popup window after retrieving input
    root.destroy()
    del root
    if filename in [None, '']:
        path = 'C:/Users/mattc/Documents/Flysight/21-07-24 Baring/'
        filename = ''.join([path, '16-49-48.CSV'])
    print('Opening {}'.format(filename))
    return filename


if __name__ == '__main__':
    # Open GUI pop-up explorer window to find file
    filename = open_file()
    csvname = filename.split('/')[-1]
    flysight_df = load_flysight(filename)
    # Calculate velocities & add glide ratio
    flysight_df = calc_vel(flysight_df)

    jump_df = find_jump(flysight_df)
    # Calculate and add time_elapsed for Jump
    jump_df = convert_time(jump_df)  # convert_time could become a Class method
    
    # Download ground elevation from API
    # Need to employ multithreading for faster result
    # jump_df = get_elev(jump_df)

# Plot it for checking
    jump_df.plot(x='time_elapsed', y='hMSL',
                 title='{} Jump Data'.format(csvname),
                 color='black',
                 xlabel='Time Elapsed (s)',
                 ylabel='Height-MSL (m)')
    plt2 = plt.twinx()
    plt2.plot(jump_df['time_elapsed'], jump_df['velH'], color='blue')
    plt2.plot(jump_df['time_elapsed'], jump_df['velD'], color='brown')
    plt2.plot(jump_df['time_elapsed'], jump_df['velT'], color='red')
    plt2.ylabel = 'Velocity (m/s)'
    plt2.legend(['Horiz V', 'Vert V', 'Total V'])
    # plt3 = plt2.twinx()
    # plt3.plot(jump_df['time_elapsed'], jump_df['gr'], color='green')

