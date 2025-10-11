from google import genai
from dotenv import load_dotenv
import sys 
import os
sys.path.append("C:/Users/BETOBETACO/Desktop/BETEX/DURSAN")
from bbdd.BBDD_Connector import BBDD_Connector
from api.prompts import sql_translator_prompt,offer_optimizer_prompt
import time

load_dotenv()

client = genai.Client()

chat_questions=["Quieres comprar el coche al contado, o prefieres financiarlo?","Que presupuesto tienes para comprar el coche?","Que tipo de combustible prefieres?","Que kilometraje maximo te gustaria que tuviera el coche?","Que antiguedad maxima te gustaria que tuviera el coche?","Prefieres un coche automatico o no te importa?"]

start_time=time.time()

user_answers=["Prefiero financiarlo","Tengo un presupuesto de 20000 euros","Prefiero gasolina","Maximo 50000 km","Maximo 5 años","No me importa"]
sql_translator_prompt=sql_translator_prompt(chat_questions,user_answers)

# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents=sql_translator_prompt
# )
# query=response.text.strip()
query="SELECT * FROM CarAd WHERE offer_price <= 20000 AND fuel_type = 'Gasolina' AND car_kms <= 50000 AND car_year >= (strftime('%Y', 'now') - 5)"

bbdd=BBDD_Connector("bbdd/car_ads.db")
limit_responses=100
query+=f" LIMIT {limit_responses};"

car_offers = bbdd.execute_query(query)

offer_optimizer=offer_optimizer_prompt(chat_questions,user_answers,car_offers,limit_offers=30)

# response= client.models.generate_content(
#     model="gemini-2.5-flash",   
#     contents=offer_optimizer
# )

end_time=time.time()
elapsed_time=end_time-start_time
print(f"Elapsed time: {elapsed_time} seconds")

