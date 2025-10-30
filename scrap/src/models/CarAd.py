
from sqlmodel import SQLModel, Field
from typing import Optional
from sqlmodel import create_engine
from dotenv import load_dotenv
import os
load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_URI=f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

class CarAd(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	url:str
	car_brand: str
	car_model: str
	description: str
	offer_price: float
	monthly_offer_price: int
	car_year: int
	car_kms: int
	automatic: bool
	fuel_type: str
	image_url: str
	
def create_db():
		engine = create_engine(DB_URI, echo=True)
		SQLModel.metadata.create_all(engine)

def remove_db():
		engine = create_engine(DB_URI, echo=True)
		SQLModel.metadata.drop_all(engine)

if __name__ == "__main__":
	remove_db()
	create_db()
