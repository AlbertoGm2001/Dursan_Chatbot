
from sqlmodel import SQLModel, Field
from typing import Optional
from sqlmodel import create_engine
from dotenv import load_dotenv
import os
load_dotenv()
bbdd_path=os.getenv('BBDD_PATH')


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
def create_db():
		engine = create_engine(bbdd_path, echo=True)
		SQLModel.metadata.create_all(engine)

def remove_db():
		engine = create_engine(bbdd_path, echo=True)
		SQLModel.metadata.drop_all(engine)

if __name__ == "__main__":
	remove_db()
	create_db()
