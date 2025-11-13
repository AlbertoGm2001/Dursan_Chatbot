from sqlmodel import Session, create_engine


import os
import requests
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

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
            
        # Create engine once and reuse it for better performance
        self._engine = create_engine(self.db, echo=False, pool_size=10, max_overflow=20)
            
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

    

    def parse_ad(self,ad):
        try: 
            car_image= ad.css_first('div.vehicle-card__slider')
            if car_image:
                    img_tag=car_image.css_first('img')
                    image_url=img_tag.attributes['src'] if img_tag and 'src' in img_tag.attributes else None
                    image_content=requests.get(image_url).content
                    with open(f'/tmp/{image_url.split("/")[-1]}', 'wb') as handler:
                        handler.write(image_content)
                    self.s3_client.upload_file(f'/tmp/{image_url.split("/")[-1]}', self.s3_bucket_name, f'{self.s3_folder_name}/{image_url.split("/")[-1]}')
            
                    car_image_url=image_url.split("/")[-1]
            else:
                return None

            car_content = ad.css_first('div.vehicle-card__content')
            
            if car_content is None:
                return None
            
            ad_title = car_content.css_first('a.vehicle-card__title')
            ad_url = ad_title.attributes['href'] if ad_title else None

            ad_brand = ad_title.css_first('span.make').text() if ad_title else None
            ad_model = ad_title.css_first('span.model').text() if ad_title else None

            car_especifications = ad.css_first('div.vehicle-card-specs')
            car_especifications = car_especifications.css('li')
            ad_kms = int(clean_text(car_especifications[0].text())) if len(car_especifications) > 0 else None
            ad_year = int(car_especifications[1].text().strip()) if len(car_especifications) > 1 else None
            ad_automatic = True if len(car_especifications) > 2 and 'Automático' in car_especifications[2].text().strip() else False
            ad_fuel_type = car_especifications[3].text().strip() if len(car_especifications) > 3 else None

            car_prices=ad.css_first('div.vehicle-card__price')
            ad_offer_price=int(clean_text(car_prices.css_first('span.inner').text()))
            
            car_quota=ad.css_first('div.vehicle-card__quota')
            ad_monthly_price=int(clean_text(car_quota.css_first('span.value').text()))
            ad_description=ad_title.text().strip().replace(' ','').replace('\n',' ') if ad_title else None
            car_ad = CarAd(
            url=ad_url,
            car_brand=ad_brand,
            car_model=ad_model,
            description=ad_description,
            offer_price=ad_offer_price,  # You need to extract this from the ad if available
            monthly_offer_price=ad_monthly_price,  # You need to extract this from the ad if available
            car_year=ad_year,
            car_kms=ad_kms,
            automatic=ad_automatic,
            fuel_type=ad_fuel_type,
            image_url=car_image_url
            )

        except Exception as e:
            print(f"Error processing ad: {e}")
            return 
        return car_ad

    def get_page_ads(self,html):
        
        tree=HTMLParser(html)

        ads_list=tree.css('div.vehicle-card')

        car_ads_list = [self.parse_ad(ad) for ad in ads_list]    
        
        car_ads_list = [car_ad for car_ad in car_ads_list if car_ad is not None]

        return car_ads_list


    def insert_car_ads(self, car_ads_list):
        """
        Insert car ads using bulk operations for better performance.
        Uses the reusable engine instance with connection pooling.
        """
        if not car_ads_list:
            return
            
        with Session(self._engine) as session:
            # Use bulk_save_objects for better performance with large datasets
            session.bulk_save_objects(car_ads_list)
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
        




