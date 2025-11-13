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
from dotenv import load_dotenv



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





@app.post("/get_recommendations")

async def get_recommendations(chat_questions: List[str], user_answers: List[str]) -> Dict[str, Any]:
	
	DB_USER = os.getenv("DB_USER")
	DB_PASSWORD = os.getenv("DB_PASSWORD")
	DB_HOST = os.getenv("DB_HOST")
	DB_PORT = os.getenv("DB_PORT")
	DB_NAME = os.getenv("DB_NAME")
	DB_URI=f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
	
	bbdd=BBDD_Connector(DB_URI)
	parser=RecommendationParser()
	
	query_flag=0 ##Bool that controls if the query has been properly generated
	n_sql_tries=0
	N_AI_TRIES=3
	recommendation_flag=0#Bool that controls if the generation of the recommendation has been successful
	n_recommendation_tries=0
	#Query generation flow off from the user answers
	available_brands=bbdd.get_available_brands()		
	
	while query_flag==0 & n_sql_tries<N_AI_TRIES:
		try:
			sql_translator=sql_translator_prompt(chat_questions,user_answers,available_brands)
			logger.info("Translating user answers to SQL query...")
			
			query=gemini_request(sql_translator)
			logger.info(f"Generated SQL Query: {query}")
			
			logger.info("Executing SQL query on the database...")
			car_offers=bbdd.execute_query(query)
			query_flag=1
			if len(car_offers)==0:
				raise HTTPException(status_code=404, detail="No car offers found matching the criteria")
		
		except HTTPException as he:
			raise he
		except Exception as e:
			logger.error(f"Error executing SQL query: {str(e)}")
			n_sql_tries+=1
			if n_sql_tries>=3:
				raise HTTPException(status_code=500, detail="Error executing SQL query")
		

	logger.info(f"Retrieved {len(car_offers)} car offers from the database.")
	#SE ordena para mostrar al prompt los coches de mayor valor, ya que se asume que si el cliente no fija límites de presupuesto, es porque busca el mejor coche posible
	car_offers=sorted(car_offers,key=lambda x:x["offer_price"],reverse=True)

	#Recommendation generation flow based on the retrieved car offers
	while recommendation_flag==0 | n_recommendation_tries<N_AI_TRIES:
		try:
			logger.info("Generating recommendations")
			offer_optimizer=offer_optimizer_prompt(chat_questions,user_answers,car_offers,limit_offers=80)
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
			if not recommendations or len(recommendations)==0:
				raise HTTPException(status_code=500, detail="No recommendations generated")
			recommendation_flag=1
		except Exception as e:
			logger.error(f"Error generating recommendations: {str(e)}")
			n_recommendation_tries+=1
			if n_recommendation_tries>=N_AI_TRIES:
				raise HTTPException(status_code=500, detail="Error generating recommendations")
			
	logger.info("Recomendations generated")
	return {"recommendations": recommendations}
