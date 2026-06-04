from groq import Groq
from core.utils import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

# Simple cache to avoid repeated identical calls (optional)
_cache = {}

def call_groq(prompt, system="You are a helpful AI learning assistant.", model="llama3-8b-8192", temperature=0.7):
    key = (prompt, system, model, temperature)
    if key in _cache:
        return _cache[key]
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    answer = response.choices[0].message.content
    _cache[key] = answer
    return answer