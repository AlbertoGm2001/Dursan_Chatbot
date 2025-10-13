from fastapi import FastAPI,HTTPException
import os
import sys
from loguru import logger
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from bbdd.BBDD_Connector import BBDD_Connector
from api.prompts import sql_translator_prompt, offer_optimizer_prompt
from api.modules.utils import gemini_request
from api.modules.RecommendationParser import RecommendationParser


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

bbdd=BBDD_Connector("bbdd/car_ads_pre.db")
parser=RecommendationParser()

@app.post("/get_recommendations")
def get_recommendations(chat_questions: List[str], user_answers: List[str]) -> Dict[str, Any]:
	try:
		available_brands=bbdd.get_available_brands()		
		
		sql_translator=sql_translator_prompt(chat_questions,user_answers,available_brands)
		logger.info("Translating user answers to SQL query...")
		
		query=gemini_request(sql_translator)
		logger.info(f"Generated SQL Query: {query}")
		
		logger.info("Executing SQL query on the database...")
		car_offers=bbdd.execute_query(query)
		logger.info(f"Retrieved {len(car_offers)} car offers from the database.")
		
		logger.info("Generating recommendations")
		offer_optimizer=offer_optimizer_prompt(chat_questions,user_answers,car_offers,limit_offers=30)
		recommendation_response=gemini_request(offer_optimizer)
		
		logger.info("Parsing recommendations...")
		parsed_recommendations=parser.parse(recommendation_response)["recommendations"]
		
		# Map the parsed recommendations to the original car offers
		recommendations = [
			{**bbdd.search_by_id(recommendation['id'])[0], **{
				"fit_reasoning": recommendation['fit_reasoning']
			}}
			for recommendation in parsed_recommendations
		]

		logger.info("Recomendations generated")
		return {"recommendations": recommendations}
	except Exception as e:
		logger.error(f"Error in /get_recommendations: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))
