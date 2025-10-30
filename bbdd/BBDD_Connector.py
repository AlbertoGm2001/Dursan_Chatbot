from sqlalchemy import create_engine,text

class BBDD_Connector:
    def __init__(self, db_name: str):
        self.db_name = db_name
    
    def create_engine(self):
        return create_engine(self.db_name)

    def execute_query(self, query: str):
        engine = self.create_engine()
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
        
    def search_by_id(self, id: int):
        query = f"SELECT * FROM CarAd WHERE id = {id};"
        return self.execute_query(query)
    def get_available_brands(self):
        query = "SELECT DISTINCT car_brand FROM CarAd;"
        results = self.execute_query(query)
        return [row['car_brand'] for row in results if row['car_brand'] is not None]