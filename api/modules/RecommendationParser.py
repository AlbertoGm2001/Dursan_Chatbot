import json
class RecommendationParser:
    
    def parse(self,response:str)->dict:
        try:
            response_splitted=response.strip().split('"top_3_offers": [')[1]
            response_splitted_2=response_splitted.split("]")[0]
            response_splitted_3='['+response_splitted_2+']'
            

            recommendations=json.loads(response_splitted_3)
            return {"recommendations": recommendations}
        except Exception as e:
            print(f"Error parsing recommendations: {e}")
            return {"error": "Failed to parse recommendations"}