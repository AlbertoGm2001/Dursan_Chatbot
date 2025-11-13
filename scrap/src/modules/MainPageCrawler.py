from sqlmodel import Session, create_engine


import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.models.CarAd import CarAd
import re
import math
import boto3


load_dotenv()
main_url=os.getenv('MAIN_URL')

def clean_text(text:str):
           return text.strip().replace('km','').replace('\n','').replace('.','').replace('\xa0','').replace('€','')

class MainPageCrawler():

    def __init__(self,
                    url: str,
                    db: str = None,
                    s3_client = boto3.client('s3'),
                    s3_bucket_name='dursan-chatbot',
                    s3_folder_name='scrap-images'
                ):
        
        
        self.url = url
        
        if db is None:
            DB_USER = os.getenv("DB_USER")
            DB_PASSWORD = os.getenv("DB_PASSWORD")
            DB_HOST = os.getenv("DB_HOST")
            DB_PORT = os.getenv("DB_PORT")
            DB_NAME = os.getenv("DB_NAME")
            self.db = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        else:
            self.db = db
            
        self.s3_client = s3_client
        self.s3_bucket_name = s3_bucket_name
        self.s3_folder_name = s3_folder_name
    def get_html(self,
                 url=main_url
                 ):
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        return {"error": "Failed to retrieve data"}

    

    def get_page_ads(self,html):
        
        soup=BeautifulSoup(html, 'html.parser')

        ads_list=soup.find_all('div', class_='vehicle-card')
        car_ads_list=[]

        for ad in ads_list:
            
            try: 
                car_image= ad.find('div', class_='vehicle-card__slider')
                if car_image:
                     img_tag=car_image.find('img')
                     image_url=img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
                     image_content=requests.get(image_url).content
                     with open(f'/tmp/{image_url.split("/")[-1]}', 'wb') as handler:
                        handler.write(image_content)
                     self.s3_client.upload_file(f'/tmp/{image_url.split("/")[-1]}', self.s3_bucket_name, f'{self.s3_folder_name}/{image_url.split("/")[-1]}')
                
                car_image_url=image_url.split("/")[-1]
                car_content = ad.find('div', class_='vehicle-card__content')
                
                if car_content is None:
                    continue
                ad_title = car_content.find('a', class_='vehicle-card__title')
                ad_url = ad_title['href'] if ad_title else None

                ad_brand = ad_title.find('span', class_='make').text if ad_title else None
                ad_model = ad_title.find('span', class_='model').text if ad_title else None

                car_especifications = ad.find('div', class_='vehicle-card-specs')
                car_especifications = car_especifications.find_all('li')
                ad_kms = int(clean_text(car_especifications[0].text)) if len(car_especifications) > 0 else None
                ad_year = int(car_especifications[1].text.strip()) if len(car_especifications) > 1 else None
                ad_automatic = True if len(car_especifications) > 2 and 'Automático' in car_especifications[2].text.strip() else False
                ad_fuel_type = car_especifications[3].text.strip() if len(car_especifications) > 3 else None

                car_prices=ad.find('div', class_='vehicle-card__price')
                ad_offer_price=int(clean_text(car_prices.find('span',class_='inner').text))
                
                car_quota=ad.find('div', class_='vehicle-card__quota')
                ad_monthly_price=int(clean_text(car_quota.find('span',class_='value').text))

                car_ad = CarAd(
                url=ad_url,
                car_brand=ad_brand,
                car_model=ad_model,
                description=ad_title.text if ad_title else None,
                offer_price=ad_offer_price,  # You need to extract this from the ad if available
                monthly_offer_price=ad_monthly_price,  # You need to extract this from the ad if available
                car_year=ad_year,
                car_kms=ad_kms,
                automatic=ad_automatic,
                fuel_type=ad_fuel_type,
                image_url=car_image_url
                )

                car_ads_list.append(car_ad)
            except Exception as e:
                print(f"Error processing ad: {e}")
                continue

        return car_ads_list


    def insert_car_ads(self,car_ads_list):
        
        engine = create_engine(self.db, echo=True)
        with Session(engine) as session:
            
            session.add_all(car_ads_list)
            session.commit()

    def get_all_urls(self,html):
         
        soup=BeautifulSoup(html, 'html.parser')
        summary=soup.find('div',class_='vehicle-list-header__summary')
        summary_text=summary.find('span').text
        match = re.search(r'(\d+)', summary_text)
        n_ads = int(match.group(1)) if match else None
        n_pages=math.ceil(n_ads/35)
        url_list=[]
        for page in range(n_pages):
            n_page=page+1
            url_to_crawl=self.url+f'?page={n_page}'
            url_list.append(url_to_crawl)
        return url_list
        




