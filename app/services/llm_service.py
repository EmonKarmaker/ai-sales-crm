import httpx
import asyncio
from typing import Optional
from app.config import settings


class LLMService:
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_retries: int = 5
    ) -> str:
        """Generate a response from the LLM with retry logic."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.base_url,
                        headers=headers,
                        json=payload
                    )
                    
                    # Handle rate limiting
                    if response.status_code == 429:
                        wait_time = (2 ** attempt) + 1  # Exponential backoff: 2, 3, 5, 9, 17 seconds
                        print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1
                    print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(wait_time)
                    continue
                print(f"HTTP error: {e.response.status_code} - {e.response.text}")
                return ""
            except Exception as e:
                print(f"LLM error: {e}")
                return ""
        
        print("Max retries exceeded")
        return ""
    
    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a JSON response from the LLM."""
        json_system = (system_prompt or "") + "\n\nRespond ONLY with valid JSON. No explanations or markdown."
        return await self.generate(prompt, json_system)


# Singleton instance
llm_service = LLMService()