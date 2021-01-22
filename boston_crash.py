import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATE_TIME = "date/time"
DATA_URL = (
    "boston_crash.csv"
)
st.title("Motor Vehicle Collisions in Boston Metro Area")
st.markdown("This application is a Streamlit dashboard that can be used "
            "to analyze motor vehicle collisions in Boston ☘️💥🚗")


@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.dropna(subset=['lat', 'long'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data.rename(columns={"dispatch_ts": "date/time"}, inplace=True)
    data.rename(columns={"lat": "latitude"}, inplace=True)
    data.rename(columns={"long": "longitude"}, inplace=True)
    return data

data = load_data(20000)
data[['latitude','longitude']].to_csv('lat_long.csv', index=False)

data['date/time'] = pd.to_datetime(data['date/time'], errors='coerce')

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
original_data = data

st.header("What is the most dangerous hour to travel in Boston for each class?")
original_data.rename(columns={'mode_type': "Mode"}, inplace=True)
g2 = original_data.groupby(data['Mode']).size().reset_index(name='Total of Collisions')
original_data.rename(columns={'xstreet1': "Street"}, inplace=True)
g3 = data.groupby(original_data['Street']).size().reset_index(name='Total of Collisions')


data = data[data[DATE_TIME].dt.hour == hour]
st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})

fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ],
))


st.header("Total Collisions by Class between %i:00 and %i:00" % (hour, (hour + 1) % 24))


data.rename(columns={'mode_type': "Mode"}, inplace=True)
g1 = data.groupby(data['Mode']).size().reset_index(name='Total of Collisions')
st.write(g1)

st.header("Total Collisions by Mode")
st.write(g2)

st.header("Collisions by Street Name")
st.write(g3)

select = st.selectbox('Affected class', ['Pedestrians', 'Bicyclists', 'Motorists'])
st.header("Collisions by Hour")

if select == 'Pedestrians':
    df = original_data.query("Mode == 'Pedestrians'")
    dfmode = df.groupby(df['date/time'].dt.hour).size().reset_index(name='Total of Collisions')
    dfmode.rename(columns={"date/time": "Time"}, inplace=True)
    popstreet = df.groupby(df['Street']).size().reset_index(name='Total of Collisions')
    st.write(dfmode)
    st.header("Most dangerous time for Pedestrians")
    st.write(dfmode[dfmode['Total of Collisions']==max(dfmode['Total of Collisions'])])

    st.header("Collisions by Street")
    st.write(popstreet)

    st.header("Most dangerous street for Pedestrians")
    st.write(popstreet[popstreet['Total of Collisions']==max(popstreet['Total of Collisions'])])

elif select == 'Bicyclists':
        df = original_data.query("Mode == 'Bicyclists'")
        dfmode = df.groupby(df['date/time'].dt.hour).size().reset_index(name='Total of Collisions')
        dfmode.rename(columns={"date/time": "Time"}, inplace=True)
        popstreet = df.groupby(df['Street']).size().reset_index(name='Total of Collisions')
        st.write(dfmode)
        st.header("Most dangerous time for Bicyclists")
        st.write(dfmode[dfmode['Total of Collisions']==max(dfmode['Total of Collisions'])])

        st.header("Collisions by Street")
        st.write(popstreet)

        st.header("Most dangerous street for Bicyclists")
        st.write(popstreet[popstreet['Total of Collisions']==max(popstreet['Total of Collisions'])])

else:
        df = original_data.query("Mode == 'Motorists'")
        dfmode = df.groupby(df['date/time'].dt.hour).size().reset_index(name='Total of Collisions')
        dfmode.rename(columns={"date/time": "Time"}, inplace=True)
        popstreet = df.groupby(df['Street']).size().reset_index(name='Total of Collisions')
        st.write(dfmode)
        st.header("Most dangerous time for Motorists")
        st.write(dfmode[dfmode['Total of Collisions']==max(dfmode['Total of Collisions'])])

        st.header("Collisions by Street")
        st.write(popstreet)

        st.header("Most dangerous street for Motorists")
        st.write(popstreet[popstreet['Total of Collisions']==max(popstreet['Total of Collisions'])])


if st.checkbox("Show raw data", False):
    st.subheader("Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
    st.write(data)
