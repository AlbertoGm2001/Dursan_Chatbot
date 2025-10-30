# prompts.py
import json

def sql_translator_prompt(chat_questions: list,
                          user_answers: list,
                          available_brands: list) -> str:
    
    available_brands_str="\n".join([f"'{brand}'" for brand in available_brands])
    
    prompt=f"""

Your main task is going to be to transform natural language into a simple SQL query that is used in a SQLite database, task for which you are an expert.
You will be provided with a database schema, and you will have to use it to create the SQL query.
You will also be provided with a conversation between a chatbot and a user which will contain the information needed to create the SQL query.

IMPORTANT:You will only respond with the SQL query, nothing else. Do not add any explanations or additional information.

In the conversation, the chatbot will be asking the user for information about what type of car offer they might be interested in, so you need to understand the users needs and create the SQL query accordingly.
The database schema is the following:

id: Optional[int] = Field(default=None, primary_key=True)
url:str
car_brand: str
car_model: str
description: str
offer_price: float
monthly_offer_price: int
car_year: int
car_kms: int
automatic: bool(Options are true, false)
fuel_type: str(Options are 'Gasolina', 'Diésel', 'Eléctrico', 'Híbrido')

The options for the car_brand variable are the following:
{available_brands_str}
If the user gives hints about a brand that is not in the list, you will ignore that information and not include it in the SQL query.
If the user gives a hint that prefers any of the brands in the list, then you will try to filter by not only that brand, but also include in the filter 2 or 3 other brands that you consider similar or relevant.
For example, if the user says they like BMW, you can include in the filter Audi and Mercedes as well.

You will mainly need to filter by the variables offer_price or monthly offer price(depending on what the user asks for), car_year, car_kms, automatic and fuel_type, so you can ignore the rest of the variables.

OBSERVATIONS:

#Try not to include two offers of the same car model in the results, unless there are not enough offers that meet the users needs.
#IMPORTANT: If you cannot extract any useful information from the conversation, you will return a query that retrieves all the information from the database, which is "SELECT * FROM CarAd;"
#VERY IMPORTANT:
You have to understand that your response will be sent to a SQLite database, so you have to use the correct syntax for SQLite.
Correct Syntax examples:
SELECT * FROM CarAd WHERE car_brand = 'Audi';

Incorrect Syntax examples:
```sql
SELECT * FROM CarAd WHERE car_brand = 'Audi';
```


User and chatbot conversation:
"""
    for i in range(len(chat_questions)):
        prompt += f"Chatbot: {chat_questions[i]}\nUser: {user_answers[i]}\n"
    
    return prompt


def offer_optimizer_prompt(chat_questions: list, 
                           user_answers: list,
                           car_offers: list,
                           limit_offers: int=None,
                           ) -> str:
    
    #Image_url is not included in the prompt to reduce token usage
    fields_to_include_in_prompt=['id', 'url', 'car_brand', 'car_model', 'description', 'offer_price', 'monthly_offer_price', 'car_year', 'car_kms', 'automatic', 'fuel_type']
    car_offers=[{key: offer[key] for key in fields_to_include_in_prompt} for offer in car_offers]
    
    if limit_offers:
        car_offers = car_offers[:limit_offers]
    car_offers=json.dumps(car_offers, indent=4, ensure_ascii=False)

   
    prompt=f"""
You are an expert car sales assistant and data analyst.

Your task is to analyze a conversation between a chatbot and a user, where the chatbot gathers the users car preferences (budget, brand, model, transmission, fuel type, mileage, year, etc.). You will also receive a list of car offers in JSON format, each containing detailed information about available cars.
You must carefully reason through the information and return the top 3 offers that best match the users expressed preferences.

---

### Input Structure

You will receive the following data:

1. Conversation:
   A transcript between the chatbot and the user. The conversation includes the users stated preferences, needs, and priorities (e.g., price range, brand, year, mileage, transmission type, etc.).

2. Car offers (JSON list):
   Each offer will follow this structure:
   {{
     'id': 1,
     'url': 'https://example.com/car/1',
     'car_brand': 'Volkswagen',
     'car_model': 'Golf',
     'description': 'Electric hatchback with high efficiency',
     'offer_price': 22900.0,
     'monthly_offer_price': 350,
     'car_year': 2020,
     'car_kms': 35000,
     'automatic': true,
     'fuel_type': 'Electric'
   }}

---

### Task

1. Extract the users preferences from the conversation (budget, brand, fuel type, etc.).
2. Compare each car offer against those preferences.
3. Rank all offers based on how well they match the users needs.
4. Return the top 3 offers in JSON format, including a reasoning summary and an estimated match score. Reasoning summary must be in Spanish!!!

---

### Output Format

{{
  'top_3_offers': [
    {{
      'id': 12,
      'fit_reasoning': 'Matches users preference for an electric car under 25,000€, automatic transmission, and low mileage.',
      'match_score': 0.92
    }},
    {{
      'id': 7,
      'fit_reasoning': 'Slightly above budget but matches desired brand and recent model year.',
      'match_score': 0.85
    }},
    {{
      'id': 3,
      'fit_reasoning': 'Good balance of mileage and price; user was flexible with fuel type.',
      'match_score': 0.81
    }}
  ]
}}

---

### Evaluation Criteria

Prioritize offers based on:
- Price alignment with the users budget
- Preferred brand/model
- Fuel type (electric, hybrid, gasoline, diesel)
- Transmission (automatic/manual)
- Car year (prefer newer)
- Mileage (prefer lower)
- Any explicit or inferred preferences from the conversation

If some preferences are not mentioned, infer reasonable assumptions based on the users context or tone.

Conversation:
"""

    for i in range(len(chat_questions)):
        prompt += f"Chatbot: {chat_questions[i]}\nUser: {user_answers[i]}\n"

    prompt += f"\nCar offers:\n{car_offers}\n"

    return prompt


template_response="""

As an expert car sales assistant and data analyst, I have carefully extracted the user's preferences from the conversation and evaluated all available car offers.

**User Preferences:**
*   **Payment:** Prefers financing (not a direct filter for car specs, but noted).
*   **Budget:** Maximum 20,000 euros.
*   **Fuel Type:** Gasoline.
*   **Maximum Mileage:** 50,000 km.
*   **Maximum Age:** 5 years (meaning `car_year` must be 2019 or newer, assuming current year is 2024).
*   **Transmission:** Doesn't matter (automatic or manual is acceptable).

**Evaluation Criteria and Scoring Logic:**
All cars must first meet the strict criteria: price <= 20,000€, fuel type is 'Gasolina', mileage <= 50,000 km, and year >= 2019. Any car that is a "Van" type (like the Ford Transit Courier) is excluded as the user specifically asked for "coche" (car), implying a passenger vehicle.

For ranking the qualified offers, a weighted scoring system was used, prioritizing attributes as follows:
*   **Price Alignment:** How much lower the price is compared to the budget maximum (weighted 40%).
*   **Mileage:** How much lower the mileage is compared to the maximum (weighted 30%).
*   **Car Year:** How new the car is within the allowed age range (weighted 20%).
*   **Automatic Transmission:** A slight bonus if the car is automatic, as the user didn't mind (weighted 10%).

The raw scores were then rescaled to be within a [0.85, 0.95] range for a clearer "match_score" presentation, where 0.95 indicates the best match among the filtered options.

---

**Top 3 Car Offers:**

```json
{
  "top_3_offers": [
    {
      "id": 190,
      "fit_reasoning": "This Opel Corsa is an excellent match, offering a very recent model year (2023) and exceptionally low mileage (16,361 km) at a competitive price well within your 20,000 euro budget. It perfectly meets your fuel type preference and transmission flexibility.",
      "match_score": 0.95
    },
    {
      "id": 230,
      "fit_reasoning": "The Peugeot 208 is another strong contender with a very new model year (2023) and low mileage (25,598 km). Its price is very attractive and well under budget, aligning perfectly with all your preferences including fuel type and transmission.",
      "match_score": 0.93
    },
    {
      "id": 381,
      "fit_reasoning": "The Dacia Sandero offers outstanding value, being the lowest priced option among the top recommendations (11,800€) with remarkably low mileage (15,024 km). While a 2020 model, it's comfortably within your maximum age limit and meets all other preferences.",
      "match_score": 0.90
    }
  ]
}
```


"""