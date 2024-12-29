import streamlit as st
from herbie import Herbie
from datetime import datetime
import metpy.interpolate
import xarray as xr
import numpy as np

def get_urma_wind_speed(lat, lon, date_time):
    """
    Fetch URMA wind speed for a given latitude, longitude, and time.

    Parameters:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        date_time (str): Time in the format 'YYYY-MM-DD HH:MM'.

    Returns:
        float: Wind speed at the given location and time in m/s.
    """
    dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")

    try:
        # Initialize Herbie for the given date and model
        h = Herbie(dt, model="urma", save_dir="/root/data", overwrite=True, verbose=True)

        # Load U and V wind components separately
        u = h.xarray("UGRD")  # U-component of wind (m/s)
        v = h.xarray("VGRD")  # V-component of wind (m/s)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Herbie could not find or fetch the URMA file: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while accessing URMA data: {e}")

    # Calculate the difference between input coordinates and the grid
    lat_diff = np.abs(u.latitude - lat)
    lon_diff = np.abs(u.longitude - lon)

    # Combine the differences to find the nearest grid point
    total_diff = lat_diff + lon_diff
    nearest_idx = np.unravel_index(np.argmin(total_diff.values), total_diff.shape)

    # Extract U and V wind components at the nearest grid point
    u_value = u.isel(y=nearest_idx[0], x=nearest_idx[1]).values
    v_value = v.isel(y=nearest_idx[0], x=nearest_idx[1]).values

    # Compute wind speed
    wind_speed = np.sqrt(u_value**2 + v_value**2)

    return wind_speed

# Streamlit App
st.title("URMA Wind Speed Fetcher")

st.write("Enter a location and time to fetch the URMA wind speed.")

# Input fields
latitude = st.number_input("Latitude", value=40.7128, format="%.4f")
longitude = st.number_input("Longitude", value=-74.0060, format="%.4f")
date_time = st.text_input("Date and Time (YYYY-MM-DD HH:MM)", value="2024-12-28 12:00")

if st.button("Fetch Wind Speed"):
    try:
        # Fetch wind speed
        wind_speed = get_urma_wind_speed(latitude, longitude, date_time)
        st.success(f"Wind speed at ({latitude}, {longitude}) on {date_time}: {wind_speed:.2f} m/s")
    except Exception as e:
        st.error(f"Error fetching wind speed: {e}")
