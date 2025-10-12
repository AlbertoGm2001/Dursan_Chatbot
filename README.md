# Dursan AI Car Recommendation System

A conversational AI system that helps users find the perfect second-hand car from Dursan's inventory by analyzing their preferences and requirements through a chat interface.

## Project Overview

The project consists of three main components:

1. **Web Scraper**: Collects car listings data from Dursan's website and stores it in a SQLite database.
2. **FastAPI Backend**: Processes user preferences and generates car recommendations using Google's Gemini AI.
3. **React Frontend**: Provides an interactive chat interface for users to specify their car preferences.

## Features

- Interactive chatbot interface
- Real-time car recommendations based on user preferences
- Integration with Google's Gemini AI for natural language processing
- Automated web scraping of car listings
- SQLite database for storing car inventory
- Responsive and modern UI design

## Project Structure

```
/
├── api/                    # FastAPI backend
│   ├── modules/           # Helper modules
│   ├── tests/             # API tests
│   ├── api.py            # Main API endpoints
│   └── prompts.py        # AI prompt templates
├── bbdd/                  # Database
│   ├── car_ads.db        # SQLite database
│   └── BBDD_Connector.py # Database connection handler
├── frontend/             # React frontend
│   ├── src/             # Source files
│   └── public/          # Static assets
└── scrap/               # Web scraper
    └── src/
        ├── models/      # Data models
        ├── modules/     # Scraping modules
        └── scripts/     # Scraping scripts
```

## Prerequisites

- Python 3.13+
- Node.js (latest LTS version)
- Google Cloud API key for Gemini AI

## Installation

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd dursan-ai
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

5. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

1. **Start the FastAPI backend**
   ```bash
   cd api
   uvicorn api:app --reload
   ```

2. **Start the React frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Update car database (optional)**
   ```bash
   cd scrap/src/scripts
   python crawl_main_page.py
   ```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## API Endpoints

- `POST /get_recommendations`
  - Accepts chat questions and user answers
  - Returns personalized car recommendations based on user preferences

## Environment Variables

- `MAIN_URL`: Dursan's main car listing URL
- `BBDD_PATH`: SQLite database path
- `GOOGLE_API_KEY`: Google Cloud API key for Gemini AI

## Technologies Used

- **Backend**:
  - FastAPI
  - SQLModel/SQLAlchemy
  - Google Gemini AI
  - BeautifulSoup4 (for scraping)

- **Frontend**:
  - React
  - TypeScript
  - Tailwind CSS
  - Vite

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.