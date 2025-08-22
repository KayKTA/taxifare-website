import streamlit as st
import datetime
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

'''
# TaxiFareModel front
'''

url = 'https://taxifare-314678532696.europe-west1.run.app'

def predict_price():

    data = {
        'pickup_datetime' : datetime.datetime.combine(pickup_date, pickup_time).strftime("%d-%m-%Y %H:%M:%S"),
        'pickup_longitude' : pickup_longitude,
        'pickup_latitude' : pickup_latitude,
        'dropoff_longitude' : dropoff_longitude,
        'dropoff_latitude' : dropoff_latitude,
        'passenger_count' : passenger_count
    }

    # query = f"?pickup_datetime={data['pickup_datetime']}&\
    #         pickup_longitude={data['pickup_longitude']}&\
    #         pickup_latitude={data['pickup_latitude']}&\
    #         dropoff_longitude={data['dropoff_longitude']}&\
    #         dropoff_latitude={data['dropoff_latitude']}&\
    #         passenger_count={data['passenger_count']}"

    response = requests.get(f"{url}/predict", params=data)
    print(response.json())


# col1, col2 = st.columns(2)
# with col1:
subcol1, subcol2 = st.columns(2)


with subcol1:
    pickup_date = st.date_input( "Enter pickup date", datetime.date(2013, 7, 6))
    pickup_longitude = st.number_input('Enter pickup longitude', -73.950655)
    pickup_latitude = st.number_input('Enter pickup latitude', 40.783282)
    passenger_count = st.number_input('Enter the number of passenger', 1, 8, step=1)

with subcol2:
    pickup_time = st.time_input( "Enter pickup time", datetime.time(8, 0, 0))
    dropoff_longitude = st.number_input('Enter dropoff longitude', -73.984365)
    dropoff_latitude = st.number_input('Enter dropoff latitude', 40.769802)
    if st.button('predict'):
        predict_price()

m = folium.Map(location=[pickup_longitude, pickup_latitude], zoom_start=16)
folium.Marker(
    [pickup_longitude, pickup_latitude], popup="Liberty Bell", tooltip="Liberty Bell"
).add_to(m)

# call to render Folium map in Streamlit
st_data = st_folium(m, width=725)
