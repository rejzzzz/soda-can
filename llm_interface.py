import asyncio
from google import genai
from google.genai.types import GenerateContentConfig

from config import LLM_MODEL_NAME, GEMINI_API_KEY

# Configure clients
sync_client = genai.Client(api_key=GEMINI_API_KEY)
async_client = genai.Client(api_key=GEMINI_API_KEY)

# Retry wrapper
async def get_llm_response_async(query, relevant_entries, retries=2):
    if not relevant_entries:
        return "No relevant knowledge found for the query."

    cached_text = "\n---\n".join(e.get("text_snippet", "N/A") for e in relevant_entries)
    prompt = f"""
You are a helpful assistant answering questions based strictly on the information below.

-Only use the provided text. Return direct, complete answers. Do not explain your answers or repeat the question.
-Answer in 1 sentence.
---
{cached_text}
---

Question: {query}
Answer:
"""

    for attempt in range(retries + 1):
        try:
            resp = await async_client.aio.models.generate_content(
                model=LLM_MODEL_NAME,
                contents=prompt,
                config=GenerateContentConfig(max_output_tokens=500, temperature=0.2)
            )
            result = resp.text.strip()
            if result:
                return result
        except Exception as e:
            print(f"Attempt {attempt+1} failed for '{query}': {e}")
        await asyncio.sleep(0.8 * (attempt + 1))  # Exponential backoff
    return "No answer found after retries."

# Safe, concurrent fetch with a concurrency limit
async def fetch_responses_in_parallel(queries_and_contexts, max_concurrent=3):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def guarded_call(query, entries):
        async with semaphore:
            return await get_llm_response_async(query, entries)

    tasks = [guarded_call(query, entries) for query, entries in queries_and_contexts]
    return await asyncio.gather(*tasks)

# Optionally sync wrapper
def fetch_parallel_sync(queries_and_contexts):
    return asyncio.run(fetch_responses_in_parallel(queries_and_contexts))
