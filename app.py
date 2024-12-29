import streamlit as st
from herbie import Herbie
from datetime import datetime
import metpy.interpolate
import xarray as xr

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
    # Convert date_time to datetime object
    dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")

    # Initialize Herbie for URMA
    h = Herbie(dt, model="urma")

    # Download the URMA dataset and open it with xarray
    ds = h.xarray("APCP_surface")

    # Extract U and V components of wind
    u = ds["UGRD"]  # U-component of wind (m/s)
    v = ds["VGRD"]  # V-component of wind (m/s)

    # Combine U and V into wind speed
    wind_speed = (u**2 + v**2)**0.5

    # Interpolate to the desired lat/lon
    point_wind_speed = metpy.interpolate.interpolate_to_points(
        (wind_speed.latitude.values, wind_speed.longitude.values),
        wind_speed.values,
        [(lat, lon)]
    )

    return point_wind_speed[0]

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
