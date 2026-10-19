# ✈️ Multi-Agent AI Travel Planner

An AI-powered travel planning application that helps users create a personalized, day-wise travel plan based on their destination, trip duration, travel date, number of travellers, preferred travel mode, and total budget.

The application combines specialized travel-planning agents with a Streamlit interface and Google Gemini to generate an itinerary, suggest hotels and attractions, show weather information, compare transport options, estimate expenses, and create a downloadable PDF travel guide.

> **Important:** This is a planning assistant, not a booking platform. Hotel suggestions, fares, schedules, attraction lists, and budget figures may be AI-generated, sample, or estimated rather than live/verified data. Confirm all details with official providers before making travel decisions.

## ✨ Features

- **Personalized trip inputs:** origin, destination, travel date, number of days, travellers, transport mode, train class, and total budget.
- **Multi-agent workflow:** separate agents handle weather, hotels, attractions, transport, budget, destination imagery, and itinerary generation.
- **Transport comparison:** supports train, flight, bus, and car options, including a “Compare All” mode.
- **Budget estimation:** calculates estimated costs for transport, accommodation, food, local transport, sightseeing, and miscellaneous expenses.
- **AI-generated itinerary:** produces a day-wise plan with hotel recommendations, food suggestions, local transportation tips, and travel advice.
- **Weather information:** retrieves current weather information through wttr.in when available.
- **Destination image:** searches Unsplash for a destination image when an API key is configured.
- **PDF travel guide:** generates a downloadable PDF of the travel plan.
- **Session caching:** keeps generated results in the Streamlit session and reuses cached travel-mode views where possible.

## 🧰 Tech Stack

- **Language:** Python
- **UI:** Streamlit
- **LLM:** Google Gemini via `langchain-google-genai`
- **LLM orchestration / agent framework:** LangChain and LangGraph dependencies
- **HTTP requests:** Requests
- **Configuration:** `python-dotenv`
- **PDF generation:** ReportLab
- **Other libraries:** Pydantic, Pandas, SQLAlchemy

The current planner coordinates the agents directly through `PlannerAgent`. A `StateGraph` scaffold is present in `graph/travel_graph.py`, but the main application flow does not currently use that graph for orchestration.

## 🏗️ Project Structure

```text
AI_Travel_Agent/
├── agents/
│   ├── attraction.py       # Attraction agent
│   ├── budget.py           # Trip budget estimation
│   ├── hotels.py           # Hotel suggestions
│   ├── image.py            # Destination image lookup
│   ├── itinerary.py        # LLM-generated day-wise itinerary
│   ├── planner.py          # Coordinates the agents
│   ├── travel.py           # Transport search and cost comparison
│   └── weather.py          # Weather agent
├── database/
│   ├── db.py               # Database utilities
│   └── trips.db            # Local database file (if used)
├── graph/
│   └── travel_graph.py     # LangGraph scaffold
├── models/
│   └── state.py            # Travel state schema
├── prompts/
│   └── system_prompt.py    # Travel-planner prompt
├── tools/
│   ├── attraction_tool.py
│   ├── budget_tool.py
│   ├── hotel_tool.py
│   ├── image_tool.py
│   ├── maps_tool.py
│   ├── travel_tool.py
│   └── weather_tool.py
├── utils/
│   ├── llm.py               # Gemini LLM configuration
│   └── pdf_generator.py     # PDF creation
├── app.py                   # Streamlit entry point
├── requirements.txt
└── README.md
```

## ⚙️ Setup and Installation

### 1. Prerequisites

- Python 3.10 or newer recommended
- A Google Gemini API key
- An Unsplash Access Key if destination images are required

### 2. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repository>.git
cd AI_Travel_Agent
```

Replace the repository URL with your own GitHub repository URL.

### 3. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a local `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
```

Never commit `.env` or expose API keys in screenshots, logs, or public repositories. Add `.env` to `.gitignore`. If a key was previously committed, revoke/rotate it.

### 6. Run the application

```bash
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) to open in your browser.

## 🧭 How It Works

1. Enter the origin (optional), destination, travel date, trip duration, number of travellers, travel mode, and budget.
2. The planner retrieves weather information, suggests hotels and attractions, and optionally searches transport options when an origin is provided.
3. The budget agent estimates major trip expenses and checks the estimated total against the selected budget.
4. The itinerary agent sends the trip details and retrieved suggestions to Google Gemini to create a day-wise travel plan.
5. The application displays the generated plan and provides a PDF travel guide.
6. When the user changes the travel mode, the application recalculates travel-dependent costs and the itinerary while reusing other results when available.

## 🔐 API Keys and Data Notes

- `GOOGLE_API_KEY` is used by the Google Gemini integration.
- `UNSPLASH_ACCESS_KEY` is used for destination image search.
- Weather data is requested from `wttr.in`.
- Some attraction entries are currently static examples, and hotel/transport suggestions may be generated by the LLM. Treat these as recommendations to verify, not guaranteed live inventory or booking availability.
- Do not upload API credentials, private trip data, local databases containing personal information, or generated caches to GitHub.

## 🧪 Troubleshooting

- **Missing API key:** Check that `.env` is in the project root and the variable names match exactly.
- **Dependency/import errors:** Activate the intended virtual environment and run `pip install -r requirements.txt`.
- **Gemini errors:** Check API key validity, model access, quotas, and network connectivity.
- **Weather/image data unavailable:** Check connectivity and the relevant service/API key. The app may return unavailable data if the request fails.
- **Unexpected hotel/transport details:** Validate recommendations and fares against official providers; LLM-generated outputs are not a substitute for live booking APIs.

## 🚀 Future Improvements

- Integrate verified, live travel and hotel APIs.
- Replace static attraction examples with a trusted attractions API.
- Add data validation and structured output schemas for LLM responses.
- Add automated tests, logging, retries, and clearer error handling.
- Use LangGraph for explicit workflow orchestration and state transitions.
- Add user authentication and persistent trip history if needed.
- Add currency, accessibility, dietary, and traveller-preference options.
- Add a `.gitignore`, sanitized sample environment file, and CI checks.

## 👩‍💻 Author

**Srinidhi**  
AI / Machine Learning / Generative AI Project

Update this section with your preferred name, LinkedIn profile, and portfolio links before publishing.


