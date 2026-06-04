import logging
from groq import Groq
from core.utils import GROQ_API_KEY

logger = logging.getLogger(__name__)
client = Groq(api_key=GROQ_API_KEY)

_cache = {}

def call_groq(prompt, system="You are a helpful AI learning assistant.", model="llama-3.1-8b-instant", temperature=0.7):
    key = (prompt, system, model, temperature)
    if key in _cache:
        logger.debug(f"Cache hit for prompt: {prompt[:50]}...")
        return _cache[key]
    
    logger.info(f"Calling Groq API (model={model}, temp={temperature})")
    logger.debug(f"System: {system[:100]}...")
    logger.debug(f"Prompt length: {len(prompt)} chars")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    answer = response.choices[0].message.content
    logger.info(f"Groq response received, answer length: {len(answer)}")
    logger.debug(f"Response preview: {answer[:200]}...")
    
    _cache[key] = answer
    logger.debug("Response cached")
    return answer