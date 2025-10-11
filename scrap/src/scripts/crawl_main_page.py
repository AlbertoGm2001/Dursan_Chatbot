import sys 
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import time
from modules.MainPageCrawler import MainPageCrawler
from dotenv import load_dotenv  
from src.models.CarAd import create_db, remove_db


load_dotenv()
main_url = os.getenv("MAIN_URL")
remove_db()
create_db()

crawler=MainPageCrawler(main_url)
html = crawler.get_html()
page_url_list=crawler.get_all_urls(html)

car_ads_list=[]
start_time = time.time()

for i,page in enumerate(page_url_list):
    try:
        print(f'Extrayendo página {str(page)}',)
        html = crawler.get_html(page)
        car_ads_list.extend(crawler.get_page_ads(html))
    except Exception as e:
        print(f'Error en la página {i+1}:',e)

crawler.insert_car_ads(car_ads_list)

end_time = time.time()
print(f"Execution time: {end_time - start_time:.2f} seconds")
