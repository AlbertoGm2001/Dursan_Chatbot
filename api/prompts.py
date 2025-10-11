# prompts.py

def carad_gpt_prompt(user_message: str) -> str:
    """
    Template for generating a prompt to send to the gpt-oss-20b model via Ollama.
    """
    return f"""
You are an expert car sales assistant. Answer the following user question in a helpful, concise, and friendly way, using your knowledge of cars and the data available in the database.

User question: {user_message}

Response:
"""
