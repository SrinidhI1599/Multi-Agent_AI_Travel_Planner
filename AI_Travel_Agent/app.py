from datetime import date, timedelta

import streamlit as st

from agents.planner import PlannerAgent
from tools.travel_tool import MODES
from utils.pdf_generator import generate_pdf


# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

MODE_OPTIONS = {
    "all": "Compare All (Train, Flight, Bus, Car)",
    "train": "🚆 Train",
    "flight": "✈️ Flight",
    "bus": "🚌 Bus",
    "car": "🚗 Car",
}

CLASS_OPTIONS = {
    "SL": "Sleeper (SL)",
    "3A": "AC 3-Tier (3A)",
    "2A": "AC 2-Tier (2A)",
    "1A": "AC First Class (1A)",
}


# -----------------------------------
# FORM DEFAULTS + RESET
# -----------------------------------

def default_form():
    return {
        "origin": "",
        "city": "",
        "days": 3,
        "total_budget": 25000,
        "travel_date": date.today() + timedelta(days=7),
        "travellers": 1,
        "travel_mode": "all",
        "travel_class": "3A",
    }


def view_key(mode, travel_class):
    """
    Identifies one 'travel view'. The train class only matters when
    trains are part of the search.
    """
    return (mode, travel_class if mode in ("train", "all") else None)


def reset_form():
    """
    Runs as the PDF download button's on_click callback.
    Streamlit runs callbacks BEFORE the rerun, so the download
    still happens and the page comes back with a blank form.
    """
    for key, value in default_form().items():
        st.session_state[key] = value

    st.session_state["result"] = None
    st.session_state["plan_cache"] = {}


# Keep "travel_class" alive while its selectbox is hidden. Streamlit
# deletes the value of a widget that is not drawn in a run; copying
# it to itself first turns it into a normal session value.
if "travel_class" in st.session_state:
    st.session_state["travel_class"] = st.session_state["travel_class"]

# first load only: seed the widget values
for key, value in default_form().items():
    st.session_state.setdefault(key, value)

st.session_state.setdefault("result", None)
st.session_state.setdefault("plan_cache", {})


# -----------------------------------
# HEADER
# -----------------------------------

st.title("✈️ Multi-Agent AI Travel Planner")

st.markdown(
    """
Plan trips using Weather, Hotel, Travel (Train / Flight / Bus / Car), Budget,
Attraction, Image and Itinerary Agents.
"""
)


# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.header("Trip Details")

origin = st.sidebar.text_input(
    "Travelling From (optional, for train / flight / bus / car)",
    placeholder="e.g. Hyderabad",
    key="origin"
)

city = st.sidebar.text_input(
    "Destination",
    placeholder="e.g. Goa",
    key="city"
)

travel_date = st.sidebar.date_input(
    "Travel Date",
    min_value=date.today(),
    key="travel_date"
)

days = st.sidebar.number_input(
    "Number of Days",
    min_value=1,
    max_value=30,
    key="days"
)

travellers = st.sidebar.number_input(
    "Travellers",
    min_value=1,
    max_value=6,
    key="travellers"
)

travel_mode = st.sidebar.selectbox(
    "Travel Mode",
    options=list(MODE_OPTIONS.keys()),
    format_func=lambda m: MODE_OPTIONS[m],
    key="travel_mode"
)

# Train class is only relevant when Train is the selected mode
if travel_mode == "train":
    travel_class = st.sidebar.selectbox(
        "Train Class",
        options=list(CLASS_OPTIONS.keys()),
        format_func=lambda c: CLASS_OPTIONS[c],
        key="travel_class"
    )
else:
    travel_class = st.session_state.get("travel_class", "3A")

total_budget = st.sidebar.number_input(
    "Total Trip Budget (₹)",
    min_value=5000,
    max_value=1000000,
    step=1000,
    key="total_budget"
)

generate_btn = st.sidebar.button(
    "Generate Travel Plan"
)


# -----------------------------------
# GENERATE PLAN  (result saved in session_state)
# -----------------------------------

if generate_btn:

    if not city:
        st.warning("Please enter a destination.")
        st.stop()

    with st.spinner("Generating itinerary..."):

        try:

            planner = PlannerAgent()

            result = planner.run(
                city=city,
                days=days,
                total_budget=total_budget,
                origin=origin,
                travel_date=travel_date,
                travel_mode=travel_mode,
                travel_class=travel_class,
                travellers=travellers
            )

            # remember what the plan was generated for
            result["inputs"] = {
                "origin": origin,
                "city": city,
                "days": days,
                "travel_date": travel_date,
                "travel_mode": travel_mode,
                "travel_class": travel_class,
                "travellers": travellers,
            }

            st.session_state["result"] = result

            # a new plan starts a fresh cache of travel views
            st.session_state["plan_cache"] = {
                view_key(travel_mode, travel_class): result
            }

        except Exception as e:

            st.session_state["result"] = None
            st.error(f"Error generating trip plan: {str(e)}")


result = st.session_state["result"]


# -----------------------------------
# AUTO-UPDATE WHEN THE TRAVEL MODE (OR TRAIN CLASS) CHANGES
# No need to press "Generate Travel Plan" again: only the travel,
# budget and itinerary parts are redone, and each view is cached
# so switching back to a mode already viewed is instant.
# -----------------------------------

if result is not None and result["inputs"]["origin"]:

    inp = result["inputs"]

    wanted = view_key(travel_mode, travel_class)
    shown = view_key(inp["travel_mode"], inp["travel_class"])

    if wanted != shown:

        cache = st.session_state["plan_cache"]

        if wanted in cache:

            result = cache[wanted]

        else:

            with st.spinner(
                f"Updating plan for {MODE_OPTIONS[travel_mode]}..."
            ):

                try:

                    result = PlannerAgent().update_travel(
                        result,
                        travel_mode,
                        travel_class
                    )

                    cache[wanted] = result

                except Exception as e:

                    st.error(f"Error updating travel mode: {str(e)}")

        st.session_state["result"] = result


# -----------------------------------
# SHOW RESULT (only after a plan is generated)
# -----------------------------------

if result is not None:

    inp = result["inputs"]
    plan_city = inp["city"]

    # -----------------------------------
    # DESTINATION IMAGE
    # -----------------------------------

    if result.get("background_image"):
        st.image(
            result["background_image"],
            use_container_width=True,
            caption=f"📸 {plan_city.title()} Destination View"
        )

    st.success("Trip Plan Generated!")

    st.subheader("📍 Destination")
    st.write(plan_city.title())

    st.subheader("🗓 Duration")
    st.write(f"{inp['days']} Days")

    # -----------------------------------
    # BUDGET ANALYSIS
    # -----------------------------------

    budget = result["budget"]

    st.subheader("💰 Budget Analysis")

    st.write(f"User Budget: ₹{budget['user_budget']:,}")

    if budget.get("travel_cost"):
        best = result.get("best_travel")
        mode_name = best["mode"].title() if best else "Travel"
        st.write(
            f"{mode_name} Cost (best-value option, round trip, "
            f"{inp['travellers']} traveller(s)): "
            f"₹{budget['travel_cost']:,}"
        )

    st.write(f"Estimated Trip Cost: ₹{budget['estimated_total']:,}")

    if budget["exceeded"]:

        exceeded_amount = (
            budget["estimated_total"] - budget["user_budget"]
        )

        st.markdown(
            f"""
            <div style="background-color:#ffebee;padding:15px;
                        border-radius:10px;color:red;font-weight:bold;">
            ❌ Budget Exceeded<br><br>
            Exceeded Amount: ₹{exceeded_amount:,}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div style="background-color:#e8f5e9;padding:15px;
                        border-radius:10px;color:green;font-weight:bold;">
            ✅ Trip Within Budget<br><br>
            Remaining Budget: ₹{budget['remaining']:,}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # -----------------------------------
    # TRAVEL (train / flight / bus / car)
    # -----------------------------------

    travel = result.get("travel", {})

    if inp["origin"]:

        st.subheader(
            f"🧭 Travel: {inp['origin'].title()} → {plan_city.title()}"
        )

        st.caption(
            "Timings and fares are AI-generated estimates. "
            "Confirm availability and book on the official sites."
        )

        tab_modes = list(travel.keys())

        tabs = st.tabs(
            [
                f"{MODES[m]['icon']} {MODES[m]['label']}"
                for m in tab_modes
            ]
        )

        for tab, m in zip(tabs, tab_modes):

            with tab:

                options = travel[m]

                if options:

                    cols = st.columns(len(options))

                    for idx, opt in enumerate(options):

                        with cols[idx]:

                            st.markdown(
                                f"### {opt['number']} {opt['name']}".strip()
                            )

                            st.write(
                                f"🕒 {opt['departure']} → {opt['arrival']}"
                            )

                            if opt["duration"]:
                                st.write(f"⏱ {opt['duration']}")

                            if opt.get("distance_km"):
                                st.write(f"🛣 {opt['distance_km']} km")

                            if opt["runs_on"]:
                                st.write(f"📅 Runs: {opt['runs_on']}")

                            if opt["fares"]:
                                st.write(
                                    "💰 Approx. fare per vehicle (one way)"
                                    if opt.get("per_vehicle")
                                    else "💰 Approx. fare per person"
                                )
                                for cls, fare in opt["fares"].items():
                                    st.write(f"• {cls}: ₹{fare:,}")

                            st.markdown(
                                f"[🎟 Book on {opt['booking_label']}]"
                                f"({opt['booking_url']})  \n"
                                f"[🔎 Compare on {opt['compare_label']}]"
                                f"({opt['compare_url']})"
                            )

                else:
                    st.warning(
                        f"Couldn't fetch {MODES[m]['label'].lower()} "
                        f"options right now."
                    )
                    st.markdown(
                        f"[Open {MODES[m]['booking_label']}]"
                        f"({MODES[m]['booking_url']})"
                    )

        st.divider()

    # -----------------------------------
    # HOTELS
    # -----------------------------------

    hotels = result.get("hotels", [])

    if hotels:

        best_hotel = hotels[0]

        st.subheader("🏨 Top Hotel Recommendations")

        cols = st.columns(min(3, len(hotels)))

        for idx, hotel in enumerate(hotels[:3]):

            with cols[idx]:

                st.markdown(f"### {hotel['name']}")

                st.write(f"💰 ₹{hotel['price_per_night']:,}/night")

                st.write("✨ Highlights")

                for feature in hotel["highlights"]:
                    st.write(f"✓ {feature}")

                booking_url = hotel.get(
                    "booking_url",
                    f"https://www.booking.com/searchresults.html?ss={plan_city}"
                )

                st.link_button("🏨 Book Now", booking_url)

    else:

        best_hotel = {
            "name": "No Hotel Available",
            "price_per_night": 0,
            "highlights": [],
            "booking_url": "https://www.booking.com"
        }

        st.warning("No hotel recommendations found.")

    st.divider()

    # -----------------------------------
    # ITINERARY
    # -----------------------------------

    st.subheader("🧾 Travel Summary")

    st.markdown(result["itinerary"])

    st.divider()

    # -----------------------------------
    # PDF DOWNLOAD  ->  resets the form
    # -----------------------------------

    pdf_bytes = generate_pdf(
        destination=plan_city,
        days=inp["days"],
        budget=budget,
        best_hotel=best_hotel,
        itinerary=result["itinerary"],
        travel=travel,
        origin=inp["origin"],
        travel_date=inp["travel_date"]
    )

    st.download_button(
        label="📄 Download Travel Guide PDF",
        data=pdf_bytes,
        file_name=f"{plan_city.lower()}_travel_guide.pdf",
        mime="application/pdf",
        on_click=reset_form
    )

    st.caption(
        "The form clears automatically after you download "
        "the PDF, ready for your next trip."
    )