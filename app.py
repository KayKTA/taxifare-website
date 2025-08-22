import streamlit as st
import datetime
import numpy as np
import pandas as pd
import requests
import folium
import math
from streamlit_folium import st_folium

url = 'https://taxifare-314678532696.europe-west1.run.app'

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = (math.sin(dlat/2)**2
         + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2)
    return R * (2*math.atan2(math.sqrt(a), math.sqrt(1-a)))

def build_map(pickup, dropoff):
    if pickup and dropoff:
        center = ((pickup[0]+dropoff[0])/2, (pickup[1]+dropoff[1])/2)
        zoom = 12
    elif pickup:
        center, zoom = (pickup[0], pickup[1]), 13
    elif dropoff:
        center, zoom = (dropoff[0], dropoff[1]), 13
    else:
        center, zoom = (40.7128, -74.0060), 18

    m = folium.Map(location=center, zoom_start=zoom, control_scale=True, tiles="cartodbpositron")

    if pickup:
        folium.Marker(pickup, icon=folium.Icon(color="green", icon="play", prefix="fa"), tooltip="Start").add_to(m)
    if dropoff:
        folium.Marker(dropoff, icon=folium.Icon(color="red", icon="flag", prefix="fa"), tooltip="End").add_to(m)
    if pickup and dropoff:
        folium.PolyLine([pickup, dropoff], weight=4, opacity=0.7).add_to(m)

    return m

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
    if response.ok :
        return True, response.json()
    else :
        return False, f"{response.status_code}: {response.json()} "


st.set_page_config(page_title="TaxiFare", page_icon="🚕", layout="wide")
st.title("🚕 TaxiFare")
st.caption("Planifie ton trajet")

st.sidebar.header("Paramètres du trajet")

st.sidebar.divider()

passenger_count = st.number_input("Passagers", min_value=1, max_value=8, value=1, step=1)
col_date, col_time = st.sidebar.columns(2)
with col_date:
    pickup_date = st.date_input( "Date", datetime.date(2013, 7, 6))
with col_time:
    pickup_time = st.time_input( "Heure", datetime.time(8, 0, 0))

st.sidebar.subheader("Départ")
col_lat1, col_lon1 = st.sidebar.columns(2)
with col_lat1:
    pickup_latitude = st.number_input("Latitude Départ", value=-73.950655, format="%.6f")
with col_lon1:
    pickup_longitude = st.number_input("Longitude Départ", value=40.783282, format="%.6f")

st.sidebar.subheader("Arrivée")
col_lat2, col_lon2 = st.sidebar.columns(2)
with col_lat2:
    dropoff_latitude = st.number_input("Latitude Arrivée", value=-73.984365, format="%.6f")
with col_lon2:
    dropoff_longitude = st.number_input("Longitude Arrivée", value=40.769802, format="%.6f")

st.sidebar.divider()


m = build_map([pickup_longitude, pickup_latitude], [dropoff_longitude, dropoff_latitude])

map_data = st_folium(m, width=None, height=400, key="map")

# Infos trajets
st.divider()
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    st.metric("Départ", f"{(pickup_latitude, pickup_longitude)}" if (pickup_latitude, pickup_longitude) else "—")
with c2:
    st.metric("Arrivée", f"{(dropoff_latitude, dropoff_longitude)}" if (dropoff_latitude, dropoff_longitude) else "—")
with c3:
    if (pickup_latitude, pickup_longitude) and (dropoff_latitude, dropoff_longitude):
        d = haversine(*(pickup_latitude, pickup_longitude), *(dropoff_latitude, dropoff_longitude))
        st.metric("Distance", f"{d:.2f} km")
    else:
        st.metric("Distance", "—")



disabled = not (pickup_longitude and pickup_latitude and dropoff_longitude and dropoff_latitude  )
st.sidebar.header("Calculer le Prix")
if st.sidebar.button("Estimer le prix de la course", type="secondary", disabled=disabled, use_container_width=True):
        ok, resp = predict_price()
        if ok:
            fare = resp.get("fare")
            st.success(f"Prix Estimé : **{fare:.2f} $**")
        else:
            st.error(resp)
