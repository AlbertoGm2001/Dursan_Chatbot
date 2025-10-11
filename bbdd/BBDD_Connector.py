from sqlalchemy import create_engine,text

class BBDD_Connector:
    def __init__(self, db_name: str):
        self.db_name = db_name
    
    def create_engine(self):
        return create_engine(f"sqlite:///{self.db_name}")

    def execute_query(self, query: str):
        engine = self.create_engine()
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]