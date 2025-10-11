from fastapi import FastAPI, Request, HTTPException, Body
import ollama
from sqlmodel import Session, select
from typing import Any, Dict, List, Optional
import os
import sys
from pydantic import BaseModel

# Import CarAd model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scrap', 'src', 'models')))
from CarAd import CarAd
from sqlmodel import create_engine
from fastapi.middleware.cors import CORSMiddleware

# Import the prompt template
from prompts import carad_gpt_prompt

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],  # allow Content-Type, Authorization, etc.
)

# Build absolute path to the db file in the bbdd folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, "bbdd", "car_ads.db")
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo=True)

@app.post("/carads")
async def get_carads(filters: Optional[Dict[str, Any]] = Body(default={})):
	with Session(engine) as session:
		query = select(CarAd)
		for key, value in filters.items():
			query = query.where(getattr(CarAd, key) == value)
		results: List[CarAd] = session.exec(query).all()
		return results

# Define request body model
class ChatRequest(BaseModel):
    messages: list[str]

@app.post("/chat")
async def chat(request: ChatRequest):
	messages = request.messages
	if not messages or not isinstance(messages, list):
		raise HTTPException(status_code=400, detail="Field 'messages' (list) is required in the body")
	# Here you would implement the logic to handle the chat messages
	
	return {"message": "Chat request received", "messages": messages}


# Request model for GPT endpoint
class GPTRequest(BaseModel):
	message: str

# Endpoint to call gpt-oss-20b model with Ollama
@app.post("/gpt-carad")
def gpt_carad():
	prompt = carad_gpt_prompt()
	try:
		response = ollama.generate(
		model="openai/gpt-oss-20b",
		prompt=prompt
			)
		return {"response": response["message"]["content"],"status_code":200}
	except Exception as e:
		return {"error": str(e),"status_code":500}