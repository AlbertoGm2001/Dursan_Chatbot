from scrap.src.scripts.crawl_main_page import crawl_main_page
import requests
import json
import time 
from dotenv import load_dotenv
import os 

def handler(event,context):
    try:
        crawl_main_page()

        return {
        "statusCode": 200,
        "body": json.dumps({"message": "Ejecución completada con éxito"})
    }
    except Exception as e:
        print(f"Error: {e}")
        return {"body": json.dumps({"message": "Ejecución errónea"}), "statusCode": 500}
    
if __name__ == "__main__":
    handler(None,None)