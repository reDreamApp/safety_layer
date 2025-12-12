import os
from typing import Literal, AsyncGenerator, Tuple, Optional
from dataclasses import dataclass
from openai import AsyncOpenAI
from groq import AsyncGroq
import logging
from .prompts import ROUTING_PROMPT
import tiktoken
# Create a specific logger for prompts
prompt_logger = logging.getLogger("prompts")
logger = logging.getLogger(__name__)

# Add a method to log prompts
def log_prompt(system_prompt: str, user_prompt: str, model: str):
    prompt_logger.info(
        "\n=== API REQUEST ===\n"
        f"Model: {model}\n"
        f"System Prompt: {system_prompt}\n"
        f"User Prompt: {user_prompt}\n"
        "=================="
    )

ProviderType = Literal["groq", "openai"]

@dataclass
class ModelConfig:
    name: str
    provider: ProviderType

class Agent:
    def __init__(self, model_config: ModelConfig, system_prompt: str, temperature: float = 0.5):
        self.model = model_config.name
        self.system_prompt = system_prompt
        self.temperature = temperature
        
        # Initialize the appropriate client
        if model_config.provider == "groq":
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            self.client = AsyncGroq(api_key=api_key)
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt: str) -> Tuple[str, dict]:
        try:
            log_prompt(self.system_prompt, prompt, self.model)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=1024
            )
            return response.choices[0].message.content, {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def generate_stream(self, prompt: str) -> AsyncGenerator[Tuple[str, Optional[dict]], None]:
        try:
            encoder = tiktoken.get_encoding("cl100k_base")
            prompt_tokens = len(encoder.encode(prompt))
            completion_tokens = 0
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=1024,
                stream=True
            )
            
            async for chunk in stream:
                if content := chunk.choices[0].delta.content:
                    completion_tokens += len(encoder.encode(content))
                    yield content, None
            
            yield "", {
                "input": prompt_tokens,
                "output": completion_tokens,
                "total": prompt_tokens + completion_tokens
            }
        except Exception as e:
            logger.error(f"Error in stream generation: {str(e)}")
            raise

# Model configurations
MODELS = {
    "GROQ_70B": ModelConfig(name="llama-3.3-70b-versatile", provider="groq"),
    # Use a smaller Groq model for lightweight tasks like language detection.
    # If your account doesn't have this specific model, it will still work since
    # language_detector only needs a valid Groq config; you can swap the name later.
    "GROQ_8B": ModelConfig(name="llama-3.1-8b-instant", provider="groq"),
    "GPT4": ModelConfig(name="gpt-4", provider="openai")
}

# Create agent instances (will fail if API keys are not set)
try:
    routing_agent = Agent(MODELS["GROQ_70B"], ROUTING_PROMPT, temperature=0.1)
    response_agent = Agent(MODELS["GROQ_70B"], "your_response_prompt", temperature=0.5)
except ValueError:
    # API keys not set - agents will be None until .env is configured
    routing_agent = None
    response_agent = None
    logger.warning("API keys not found. Agent instances not created. Set GROQ_API_KEY or OPENAI_API_KEY in .env file.")

