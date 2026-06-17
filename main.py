import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from fpdf import FPDF

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

OPENWEATHER_API_KEY = "98a7a8f78622c1c4738e4a1984a20c70"

# ==================================================
# SESSION STATE
# ==================================================

if "trip_generated" not in st.session_state:
    st.session_state.trip_generated = False

if "itinerary" not in st.session_state:
    st.session_state.itinerary = ""

# ==================================================
# CSS
# ==================================================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.hero {
    text-align:center;
    padding:20px;
}

.hero h1 {
    color:#00d4ff;
    font-size:50px;
}

.stButton>button {
    width:100%;
    border-radius:12px;
    height:3em;
    font-weight:bold;
}

.card {
    background:#1e293b;
    padding:20px;
    border-radius:15px;
    margin:10px 0px;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

st.markdown("""
<div class='hero'>
<h1>🌍 AI Travel Planner</h1>
<p>Smart Travel Planning Powered by Data</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("Trip Details")

destination = st.sidebar.text_input(
    "Destination"
)

days = st.sidebar.slider(
    "Days",
    1,
    15,
    5
)

budget = st.sidebar.number_input(
    "Budget (₹)",
    1000,
    500000,
    50000
)

travel_style = st.sidebar.selectbox(
    "Travel Style",
    [
        "Budget",
        "Luxury",
        "Adventure",
        "Family",
        "Solo"
    ]
)

interests = st.sidebar.multiselect(
    "Interests",
    [
        "Nature",
        "Food",
        "Shopping",
        "Photography",
        "History",
        "Beaches"
    ]
)

generate = st.sidebar.button(
    "Generate Plan"
)

# ==================================================
# WEATHER
# ==================================================

def get_weather(city):

    try:

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        if response.status_code != 200:
            return None

        return data

    except:
        return None

# ==================================================
# MAP
# ==================================================

def create_map(place):

    try:

        geo_url = f"https://nominatim.openstreetmap.org/search?q={place}&format=json"

        response = requests.get(
            geo_url,
            headers={"User-Agent":"TravelPlanner"},
            timeout=10
        )

        data = response.json()

        if len(data) == 0:
            return None

        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])

        m = folium.Map(
            location=[lat, lon],
            zoom_start=11
        )

        folium.Marker(
            [lat, lon],
            popup=place
        ).add_to(m)

        return m

    except:
        return None

# ==================================================
# SMART ITINERARY
# ==================================================

def create_itinerary():

    itinerary = f"""
# ✈️ Travel Plan for {destination}

## Day 1
- Arrive at destination
- Explore local market
- Try local cuisine

## Day 2
- Visit famous attractions
- Photography session
- Evening sightseeing

## Day 3
- Cultural exploration
- Shopping
- Local food experience

## Day 4
- Adventure activities
- Nature exploration

## Day 5
- Relax and departure

### Travel Style
{travel_style}

### Budget
₹{budget:,}

### Interests
{', '.join(interests)}
"""

    return itinerary

# ==================================================
# PDF
# ==================================================

def generate_pdf(content):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=12
    )

    pdf.multi_cell(
        0,
        8,
        content.encode(
            "latin-1",
            "replace"
        ).decode(
            "latin-1"
        )
    )

    filename = "travel_plan.pdf"

    pdf.output(filename)

    return filename

# ==================================================
# GENERATE
# ==================================================

if generate:

    if destination:

        st.session_state.itinerary = create_itinerary()

        st.session_state.trip_generated = True

# ==================================================
# DISPLAY
# ==================================================

if st.session_state.trip_generated:

    weather = get_weather(
        destination
    )

    if weather:

        st.subheader(
            "🌤 Weather Dashboard"
        )

        c1,c2,c3,c4 = st.columns(4)

        c1.metric(
            "Temperature",
            f"{weather['main']['temp']} °C"
        )

        c2.metric(
            "Humidity",
            f"{weather['main']['humidity']}%"
        )

        c3.metric(
            "Wind",
            f"{weather['wind']['speed']} m/s"
        )

        c4.metric(
            "Condition",
            weather['weather'][0]['description']
        )

    st.subheader(
        "🧠 Smart Travel Plan"
    )

    st.markdown(
        st.session_state.itinerary
    )

    pdf_file = generate_pdf(
        st.session_state.itinerary
    )

    with open(
        pdf_file,
        "rb"
    ) as file:

        st.download_button(
            "📄 Download PDF",
            file,
            file_name="travel_plan.pdf"
        )

    # Budget Chart

    st.subheader(
        "💰 Budget Analysis"
    )

    df = pd.DataFrame({

        "Category":[
            "Hotel",
            "Food",
            "Transport",
            "Activities",
            "Shopping"
        ],

        "Cost":[
            budget*0.4,
            budget*0.2,
            budget*0.15,
            budget*0.15,
            budget*0.1
        ]
    })

    fig = px.pie(
        df,
        names="Category",
        values="Cost",
        title="Budget Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Map

    st.subheader(
        "🗺 Destination Map"
    )

    m = create_map(
        destination
    )

    if m:

        st_folium(
            m,
            width=1000,
            height=500
        )

    # Packing Checklist

    st.subheader(
        "🎒 Packing Checklist"
    )

    items = [
        "Passport / ID",
        "Phone Charger",
        "Power Bank",
        "Water Bottle",
        "Medicines",
        "Comfortable Shoes",
        "Cash / Cards"
    ]

    for item in items:
        st.checkbox(item)

    # Travel Tips

    st.subheader(
        "💡 Travel Tips"
    )

    tips = [
        "Check weather before leaving.",
        "Carry a power bank.",
        "Keep emergency contacts.",
        "Book hotels early.",
        "Stay hydrated."
    ]

    for tip in tips:
        st.success(tip)

else:

    st.info(
        "Enter trip details and click Generate Plan."
    )

# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.markdown(
    """
    <center>
    <h4>✈️ AI Travel Planner</h4>
    <p>Built with Streamlit + OpenWeather API</p>
    </center>
    """,
    unsafe_allow_html=True
)
