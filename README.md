# Dursan AI Car Recommendation System

A conversational AI system that helps users find the perfect second-hand car from Dursan's inventory by analyzing their preferences and requirements through a chat interface. The system uses advanced AI technology to provide personalized car recommendations based on natural language conversations.

## Architecture Overview

The application is composed of **4 main services** working together to provide a seamless car recommendation experience:

### 1. **Frontend Application** 🌐
- **Deployment**: Vercel
- **URL**: [dursanchatbotagm.vercel.app](https://dursanchatbotagm.vercel.app)
- **Description**: Interactive React-based chat interface where users can specify their car preferences through natural conversation
- **Technology Stack**: React 19, TypeScript, Tailwind CSS 4, Vite 7

### 2. **PostgreSQL Database** 🗄️
- **Hosting**: Neon Database
- **Host**: Configured via environment variables (DB_HOST)
- **Description**: Stores all scraped car listings with detailed information including specifications, pricing, and metadata
- **Features**: Full-text search capabilities, optimized queries for recommendation matching

### 3. **API Service** 🚀
- **Deployment**: Render
- **URL**: [https://dursan-chatbot.onrender.com](https://dursan-chatbot.onrender.com)
- **Main Endpoint**: `POST /get_recommendations`
- **Description**: Processes user conversations and generates personalized car recommendations using Google's Gemini 2.5 Flash AI model
- **Functionality**: 
  - Translates natural language preferences into SQL queries
  - Retrieves matching cars from the database
  - Uses AI to rank and explain why each car fits the user's needs
  - Returns structured recommendations with reasoning

### 4. **Web Scraping Service** 🕷️
- **Deployment**: AWS Lambda Function
- **Target**: Dursan website (automotordursan.com)
- **Technology**: Selectolax for high-performance HTML parsing
- **Description**: Automated scraping service that extracts car listings data
- **Features**: 
  - Serverless architecture for cost efficiency
  - High-performance parsing with Selectolax
  - Image processing and storage in AWS S3
  - Periodic execution to keep database updated

### **Image Storage** 📸
- **Service**: AWS S3
- **Purpose**: Stores all car images scraped from listings
- **Integration**: Linked with car records in PostgreSQL database

## Key Features

- 🤖 **AI-Powered Recommendations**: Uses Google Gemini 2.5 Flash for natural language understanding
- 💬 **Conversational Interface**: Chat-based interaction for intuitive user experience  
- 🔍 **Smart Filtering**: AI translates user preferences into precise database queries
- 🚗 **Real-time Data**: Up-to-date car inventory through automated scraping
- 📱 **Responsive Design**: Works seamlessly across all devices
- ⚡ **High Performance**: Optimized scraping with Selectolax library
- ☁️ **Cloud Architecture**: Fully distributed across modern cloud platforms

## Project Structure

```
Dursan_Chatbot/
├── 📁 api/                          # FastAPI Backend Service
│   ├── 📁 modules/                  # Core business logic modules
│   │   ├── RecommendationParser.py  # AI response parsing
│   │   └── utils.py                 # Gemini API integration
│   ├── 📁 tests/                   # API testing suite
│   │   ├── available_brands_in_bbdd.py
│   │   ├── gemini_requests.py
│   │   └── query_result_format.py
│   ├── api.py                      # Main FastAPI application & endpoints
│   └── prompts.py                  # AI prompt engineering templates
│
├── 📁 bbdd/                        # Database Layer
│   └── BBDD_Connector.py          # PostgreSQL connection handler
│
├── 📁 frontend/                    # React Frontend Application
│   ├── 📁 src/                    # Source code
│   │   ├── App.tsx                # Main React component
│   │   ├── App.css               # Styling
│   │   ├── main.tsx              # Application entry point
│   │   └── index.css             # Global styles
│   ├── 📁 images/                 # Static assets
│   │   ├── car_images/           # Car placeholder images
│   │   └── logo/                 # Brand assets
│   ├── package.json              # Dependencies & scripts
│   ├── vite.config.ts            # Vite configuration
│   └── tsconfig.json             # TypeScript configuration
│
├── 📁 scrap/                      # Web Scraping Service
│   └── 📁 src/
│       ├── 📁 models/             # Data models
│       │   ├── CarAd.py          # Car advertisement model
│       │   └── Enums.py          # Type definitions
│       ├── 📁 modules/            # Scraping logic
│       │   └── MainPageCrawler.py # Main scraping engine
│       └── 📁 scripts/            # Executable scripts
│           └── crawl_main_page.py # Scraping entry point
│
├── 📄 lambda_scrap.py             # AWS Lambda handler
├── 📄 pyproject.toml              # Python dependencies & config
├── 📄 requirements.txt            # Python requirements (legacy)
├── 📄 Dockerfile                 # Container configuration
└── 📄 README.md                  # Project documentation
```

## Live Application

🌐 **Access the live application**: [dursanchatbotagm.vercel.app](https://dursanchatbotagm.vercel.app)

## Local Development Setup

### Prerequisites
- **Python 3.13+** - Latest Python version
- **Node.js 18+** - Latest LTS version recommended  
- **UV Package Manager** - Fast Python package management
- **Google Cloud API Key** - For Gemini AI integration

### Environment Configuration

1. **Clone the repository**
   ```bash
   git clone https://github.com/AlbertoGm2001/Dursan_Chatbot.git
   cd Dursan_Chatbot
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Configure your `.env` file with:
   ```bash
   # Scraping Configuration
   MAIN_URL=https://automotordursan.com/coches-segunda-mano
   
   # Database Configuration (Neon PostgreSQL)
   DB_HOST=your-neon-host
   DB_PORT=5432
   DB_NAME=your-database-name
   DB_USER=your-username
   DB_PASSWORD=your-password
   
   # AI Configuration
   GOOGLE_API_KEY=your-gemini-api-key
   ```

### Backend Setup

1. **Install Python dependencies with UV**
   ```bash
   uv sync
   ```

2. **Activate virtual environment**
   ```bash
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Start FastAPI development server**
   ```bash
   cd api
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

### Local Development URLs
- 🎨 **Frontend**: http://localhost:5173
- 🚀 **API**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs

## API Documentation

### Main Endpoint
**`POST /get_recommendations`**

**Purpose**: Processes user conversation and returns AI-generated car recommendations

**Request Body**:
```json
{
  "chat_questions": ["What's your budget?", "What type of car do you prefer?"],
  "user_answers": ["Around 15000 euros", "I need a family SUV"]
}
```

**Response**:
```json
{
  "recommendations": [
    {
      "id": 123,
      "car_brand": "Toyota",
      "car_model": "RAV4",
      "offer_price": 14500,
      "fit_reasoning": "Perfect family SUV within your budget...",
      // ... other car details
    }
  ]
}
```

**Process Flow**:
1. 🧠 AI translates user preferences into SQL queries
2. 🔍 Database retrieval of matching vehicles
3. 🤖 Gemini AI ranks and explains recommendations
4. 📋 Structured response with reasoning



## Technologies Used

### **Backend & API** 🛠️
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** + **SQLModel** - Database ORM and models
- **PostgreSQL** - Primary database (hosted on Neon)
- **Google Gemini 2.5 Flash** - AI model for natural language processing
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server for FastAPI
- **Loguru** - Advanced logging capabilities
- **Psycopg2** - PostgreSQL adapter for Python

### **Frontend & UI** 🎨
- **React 19** - Modern UI library with latest features
- **TypeScript 5.9** - Type-safe JavaScript development
- **Tailwind CSS 4** - Utility-first CSS framework
- **Vite 7** - Next-generation build tool and dev server
- **Lucide React** - Beautiful icon library
- **ESLint** - Code linting and formatting

### **Web Scraping & Data Processing** 🕷️
- **Selectolax** - High-performance HTML/XML parser (faster than BeautifulSoup)
- **Requests** - HTTP library for web scraping
- **Pandas** - Data manipulation and analysis
- **Boto3** - AWS SDK for S3 image storage
- **Python-dotenv** - Environment variable management

### **Cloud Infrastructure** ☁️
- **AWS Lambda** - Serverless scraping execution
- **AWS S3** - Image storage and CDN
- **Render** - API hosting and deployment
- **Vercel** - Frontend hosting with global CDN
- **Neon Database** - Serverless PostgreSQL hosting

### **Development & DevOps** 🔧
- **Docker** - Containerization support
- **Git** - Version control
- **Python 3.13+** - Latest Python features
- **UV** - Fast Python package manager (pyproject.toml)
- **Environment Variables** - Secure configuration management

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.