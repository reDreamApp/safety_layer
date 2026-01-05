import os
import math
from typing import Literal, AsyncGenerator, Tuple, Optional, List
from dataclasses import dataclass, field
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

ProviderType = Literal["groq", "openai", "scaleway"]

@dataclass
class ModelConfig:
    name: str
    provider: ProviderType


@dataclass
class TokenLogprob:
    """Log probability information for a single token."""
    token: str
    logprob: float
    top_logprobs: Optional[List[dict]] = None


@dataclass 
class LogprobsResult:
    """Container for logprobs data from a completion."""
    tokens: List[TokenLogprob] = field(default_factory=list)
    
    @property
    def mean_logprob(self) -> float:
        """Average log probability across all tokens."""
        if not self.tokens:
            return 0.0
        return sum(t.logprob for t in self.tokens) / len(self.tokens)
    
    @property
    def total_logprob(self) -> float:
        """Sum of all log probabilities (log of sequence probability)."""
        return sum(t.logprob for t in self.tokens)
    
    @property
    def confidence(self) -> float:
        """Convert mean logprob to a 0-1 confidence score."""
        return math.exp(self.mean_logprob) if self.tokens else 0.0

# Models that use max_completion_tokens instead of max_tokens
NEW_API_MODELS = ("gpt-5", "o1", "o3")


class Agent:
    def __init__(self, model_config: ModelConfig, system_prompt: str, temperature: float = 0.5):
        self.model = model_config.name
        self.system_prompt = system_prompt
        self.temperature = temperature
        # Check if this model uses the new API parameter names
        self._uses_new_api = any(self.model.startswith(prefix) for prefix in NEW_API_MODELS)
        
        # Initialize the appropriate client
        if model_config.provider == "groq":
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            self.client = AsyncGroq(api_key=api_key)
        elif model_config.provider == "scaleway":
            api_key = os.getenv('SCALEWAY_API_KEY')
            if not api_key:
                raise ValueError("SCALEWAY_API_KEY not found in environment")
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.scaleway.ai/v1"
            )
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self, 
        prompt: str, 
        logprobs: bool = False,
        top_logprobs: Optional[int] = None
    ) -> Tuple[str, dict, Optional[LogprobsResult]]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt to send
            logprobs: Whether to request log probabilities for each token
            top_logprobs: If logprobs=True, how many top alternatives per token (1-20)
            
        Returns:
            Tuple of (response_text, usage_dict, logprobs_result or None)
        """
        try:
            log_prompt(self.system_prompt, prompt, self.model)
            
            request_kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
            }
            
            # Use appropriate token limit parameter based on model
            if self._uses_new_api:
                request_kwargs["max_completion_tokens"] = 1024
            else:
                request_kwargs["max_tokens"] = 1024
            
            if logprobs:
                request_kwargs["logprobs"] = True
                if top_logprobs is not None:
                    request_kwargs["top_logprobs"] = top_logprobs
            
            response = await self.client.chat.completions.create(**request_kwargs)
            
            usage = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
            
            logprobs_result = None
            if logprobs and response.choices[0].logprobs:
                logprobs_result = self._parse_logprobs(response.choices[0].logprobs)
            
            return response.choices[0].message.content, usage, logprobs_result
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _parse_logprobs(self, logprobs_data) -> LogprobsResult:
        """Parse the logprobs from API response into our dataclass."""
        result = LogprobsResult()
        
        if hasattr(logprobs_data, 'content') and logprobs_data.content:
            for token_info in logprobs_data.content:
                top_alternatives = None
                if hasattr(token_info, 'top_logprobs') and token_info.top_logprobs:
                    top_alternatives = [
                        {"token": alt.token, "logprob": alt.logprob}
                        for alt in token_info.top_logprobs
                    ]
                
                result.tokens.append(TokenLogprob(
                    token=token_info.token,
                    logprob=token_info.logprob,
                    top_logprobs=top_alternatives
                ))
        
        return result

    async def generate_stream(self, prompt: str) -> AsyncGenerator[Tuple[str, Optional[dict], Optional[LogprobsResult]], None]:
        """Generate a streaming response. Note: Logprobs not available in streaming mode."""
        try:
            encoder = tiktoken.get_encoding("cl100k_base")
            prompt_tokens = len(encoder.encode(prompt))
            completion_tokens = 0
            
            stream_kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "stream": True,
            }
            
            # Use appropriate token limit parameter based on model
            if self._uses_new_api:
                stream_kwargs["max_completion_tokens"] = 1024
            else:
                stream_kwargs["max_tokens"] = 1024
            
            stream = await self.client.chat.completions.create(**stream_kwargs)
            
            async for chunk in stream:
                if content := chunk.choices[0].delta.content:
                    completion_tokens += len(encoder.encode(content))
                    yield content, None, None
            
            yield "", {
                "input": prompt_tokens,
                "output": completion_tokens,
                "total": prompt_tokens + completion_tokens
            }, None
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
    "GPT4": ModelConfig(name="gpt-4", provider="openai"),
    # GPT-5.2 model for high-quality synthetic data generation
    "GPT5": ModelConfig(name="gpt-5.2", provider="openai"),
    # Scaleway Mistral models
    "MISTRAL_SMALL": ModelConfig(name="mistral-small-3.2-24b-instruct-2506", provider="scaleway"),
    "MISTRAL_NEMO": ModelConfig(name="mistral-nemo-instruct-2407", provider="scaleway"),
}

# Create agent instances (will fail if API keys are not set)
try:
    # Use small Mistral model for routing (fast, lightweight)
    routing_agent = Agent(MODELS["MISTRAL_NEMO"], ROUTING_PROMPT, temperature=0.1)
    # Use larger Mistral model for responses (better quality)
    response_agent = Agent(MODELS["MISTRAL_SMALL"], "your_response_prompt", temperature=0.5)
except ValueError:
    # API keys not set - agents will be None until .env is configured
    routing_agent = None
    response_agent = None
    logger.warning("API keys not found. Agent instances not created. Set SCALEWAY_API_KEY in .env file.")

