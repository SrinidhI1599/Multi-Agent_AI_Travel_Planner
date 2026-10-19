import json

from utils.llm import llm

# -----------------------------------
# PER-MODE CONFIGURATION
# -----------------------------------

MODES = {
    "train": {
        "label": "Train",
        "icon": "🚆",
        "provider_hint": "real Indian Railways trains",
        "number_hint": "5-digit train number",
        "name_hint": "train name",
        "classes": ["SL", "3A", "2A", "1A"],
        "booking_url": "https://www.irctc.co.in/nget/train-search",
        "booking_label": "IRCTC",
        "compare_url": "https://www.ixigo.com/trains",
        "compare_label": "ixigo",
    },
    "flight": {
        "label": "Flight",
        "icon": "✈️",
        "provider_hint": "real flights operated by Indian airlines",
        "number_hint": "flight number, e.g. 6E-123",
        "name_hint": "airline name",
        "classes": ["Economy", "Business"],
        "booking_url": "https://www.makemytrip.com/flights/",
        "booking_label": "MakeMyTrip",
        "compare_url": "https://www.google.com/travel/flights",
        "compare_label": "Google Flights",
    },
    "bus": {
        "label": "Bus",
        "icon": "🚌",
        "provider_hint": "real intercity bus services (APSRTC, TSRTC, KSRTC, "
                         "VRL, Orange Travels, etc.)",
        "number_hint": "service number or leave empty",
        "name_hint": "operator name",
        "classes": ["Seater", "Sleeper", "AC Sleeper"],
        "booking_url": "https://www.redbus.in/",
        "booking_label": "redBus",
        "compare_url": "https://www.abhibus.com/",
        "compare_label": "AbhiBus",
    },
    "car": {
        "label": "Car",
        "icon": "🚗",
        "provider_hint": "realistic outstation car options (outstation cab "
                         "or self-drive using your own car, including fuel "
                         "and toll estimates)",
        "number_hint": "leave empty",
        "name_hint": "e.g. Outstation Cab or Own Car (Fuel + Tolls)",
        "classes": ["Hatchback", "Sedan", "SUV"],
        "booking_url": "https://www.savaari.com/",
        "booking_label": "Savaari",
        "compare_url": "https://www.zoomcar.com/",
        "compare_label": "Zoomcar",
        # fares are for the WHOLE vehicle, not per person
        "per_vehicle": True,
        "seats": 4,
    },
}


def _clean_json(text):
    text = text.strip()
    text = text.replace("```json", "").replace("```", "")
    return text.strip()


def _normalise(option, mode, preferred_class):
    """Give every option (train / flight / bus) the same set of keys."""

    fares = {}
    for item in option.get("classes", []):
        try:
            fares[str(item["class"])] = int(item["fare"])
        except (KeyError, ValueError, TypeError):
            continue

    # Train: use the class the user picked. Flight / bus: cheapest fare.
    positive = [f for f in fares.values() if f > 0]

    if mode == "train":
        fare = fares.get(preferred_class, 0)
    else:
        fare = min(positive) if positive else 0

    return {
        "mode": mode,
        "number": str(option.get("number", "")),
        "name": option.get("name", MODES[mode]["label"]),
        "from_station": option.get("from_station", ""),
        "to_station": option.get("to_station", ""),
        "departure": option.get("departure", "--:--"),
        "arrival": option.get("arrival", "--:--"),
        "duration": option.get("duration", ""),
        "runs_on": option.get("runs_on", ""),
        "distance_km": option.get("distance_km", ""),
        "fares": fares,
        "fare": fare,
        "per_vehicle": MODES[mode].get("per_vehicle", False),
        "seats": MODES[mode].get("seats", 1),
    }


def search_travel(origin, destination, travel_date, mode, preferred_class="3A"):
    """
    Suggest 3 options for ONE travel mode ("train", "flight", "bus" or "car").

    NOTE: there is no free public API for all of these, so timings and
    fares are AI-generated estimates. The UI sends the user to the
    real booking sites to verify and book.
    """

    cfg = MODES[mode]

    class_rows = ",\n            ".join(
        '{"class": "%s", "fare": 0}' % c for c in cfg["classes"]
    )

    prompt = (
        f"Suggest exactly 3 {cfg['provider_hint']} for travel from "
        f"{origin} to {destination} on {travel_date}.\n\n"
        "Return ONLY valid JSON. Use 24-hour HH:MM times.\n"
        + (
            "Fares are approximate one-way fares for the WHOLE VEHICLE "
            "(not per person) in INR, including fuel and tolls.\n\n"
            if cfg.get("per_vehicle")
            else "Fares are approximate per-person one-way fares in INR.\n\n"
        )
        +
        "Format:\n\n"
        "[\n"
        "    {\n"
        f'        "number": "{cfg["number_hint"]}",\n'
        f'        "name": "{cfg["name_hint"]}",\n'
        '        "from_station": "",\n'
        '        "to_station": "",\n'
        '        "departure": "HH:MM",\n'
        '        "arrival": "HH:MM",\n'
        '        "duration": "e.g. 8h 30m",\n'
        '        "runs_on": "e.g. Daily",\n'
        '        "distance_km": "road distance in km for car, else empty",\n'
        '        "classes": [\n'
        f"            {class_rows}\n"
        "        ]\n"
        "    }\n"
        "]\n"
    )

    try:
        response = llm.invoke(prompt)
        data = json.loads(_clean_json(response.content))  # type: ignore
        options = [
            _normalise(o, mode, preferred_class) for o in data
        ][:3]

        if not options:
            raise ValueError("No options returned")

    except Exception as e:
        print(f"{cfg['label']} search error: {e}")
        options = []

    for option in options:
        option["booking_url"] = cfg["booking_url"]
        option["booking_label"] = cfg["booking_label"]
        option["compare_url"] = cfg["compare_url"]
        option["compare_label"] = cfg["compare_label"]
        option["travel_date"] = str(travel_date)

    return options