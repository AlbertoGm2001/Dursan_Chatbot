from bbdd.BBDD_Connector import BBDD_Connector
from api.prompts import sql_translator_prompt

bbdd=BBDD_Connector("bbdd/car_ads_pre.db")
available_brands=bbdd.get_available_brands()

sql_translator_prompt=sql_translator_prompt(chat_questions=["Quieres comprar el coche al contado, o prefieres financiarlo?","Que presupuesto tienes para comprar el coche?","Que tipo de combustible prefieres?","Que kilometraje maximo te gustaria que tuviera el coche?","Que antiguedad maxima te gustaria que tuviera el coche?","Prefieres un coche automatico o no te importa?"],user_answers=["Prefiero financiarlo","Tengo un presupuesto de 20000 euros","Prefiero gasolina","Maximo 50000 km","Maximo 5 años","No me importa"],available_brands=available_brands)  
breakpoint()