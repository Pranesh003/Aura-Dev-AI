import os
import time
import random
from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Using correctly formatted GenAI models for LiteLLM
VISION_MODELS = [
    "openrouter/qwen/qwen3.5-35b-a3b",
    "models/gemini-flash-latest",
    "models/gemini-2.0-flash",
    "models/gemini-pro-latest"
]

TEXT_MODELS = [
    "openrouter/qwen/qwen3.5-35b-a3b",
    "models/gemini-flash-latest",
    "models/gemini-2.0-flash",
    "models/gemini-pro-latest"
]

class StreamWrapper:
    """Wraps a stream to ignore specific Windows-related errors on flush/write."""
    def __init__(self, original_stream):
        self._original = original_stream

    def write(self, data):
        try:
            self._original.write(data)
        except OSError as e:
            if e.errno != 22: raise

    def flush(self):
        try:
            self._original.flush()
        except OSError as e:
            if e.errno != 22: raise

    def __getattr__(self, name):
        return getattr(self._original, name)

import sys
sys.stdout = StreamWrapper(sys.stdout)
sys.stderr = StreamWrapper(sys.stderr)

def gemini_shield():
    """Nuclear patch to strip additionalProperties from ALL Gemini API requests."""
    # Disabled in 7-agent version as the new google-genai library no longer uses this syntax.
    # The patch causes a TypeError: Models.generate_content() takes 1 positional argument.
    print("DEBUG: Gemini Shield disabled for modern google-genai compatibility.")

# Apply patches immediately
gemini_shield()

MODEL_MAPPING = {} # No longer needed for masking but keeping for compatibility

class ResilientLLM(BaseChatModel):
    """
    Nuclear-Tier Resilient LLM for CrewAI.
    Rotates through 8 Google API keys and falls back across models.
    """
    model_name: str = "openrouter/qwen/qwen3.5-35b-a3b"
    current_key_idx: int = 0
    google_keys: List[str] = []
    stop: Optional[List[str]] = None
    
    def __init__(self, model_name: str = "openrouter/qwen/qwen3.5-35b-a3b", **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.google_keys = [
            os.getenv(f"GOOGLE_API_KEY_{i}") if i > 1 else os.getenv("GOOGLE_API_KEY")
            for i in range(1, 9)
        ]
        self.google_keys = [k for k in self.google_keys if k]
        self.current_key_idx = 0

    def call(self, messages: List[Any], callbacks: Optional[List[Any]] = None, **kwargs) -> str:
        """Compatibility layer for CrewAI's custom LLM interface."""
        res = self.invoke(messages, **kwargs)
        return res.content

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        
        attempts = 0
        current_model = self.model_name
        
        # Check for image in messages
        image_path = None
        for m in messages:
            if isinstance(m, HumanMessage) and "temp_sketch.png" in str(m.content):
                image_path = os.path.abspath("temp_sketch.png")
                print(f"DEBUG: Found image path in messages, normalized to: {image_path}")
                if not os.path.exists(image_path):
                    print(f"DEBUG: WARNING - image_path does not exist: {image_path}")
                break

        # Sanitize tools for Gemini compatibility
        if kwargs.get("tools"):
            kwargs["tools"] = self._sanitize_tools(kwargs["tools"])
        else:
            kwargs.pop("tools", None)  # Ensure None/empty list doesn't crash OpenAI providers

        # Strip CrewAI injected metadata that causes Pydantic validation errors
        for key in ["available_functions", "from_task", "from_agent", "response_model", "callbacks"]:
            kwargs.pop(key, None)

        while attempts < 12:
            is_openai = "gpt" in current_model.lower()
            is_openrouter = "openrouter" in current_model.lower() or "qwen" in current_model.lower()
            
            if is_openrouter:
                raw_model = current_model.replace("openrouter/", "") if current_model.startswith("openrouter/") else current_model
                try:
                    print(f"DEBUG: [ATTEMPT] OpenRouter Model={raw_model}")
                    llm = ChatOpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        model=raw_model,
                        openai_api_key=os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
                        temperature=kwargs.get("temperature", 0.7)
                    )
                    res = llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                    print("DEBUG: _generate returned successfully via OpenRouter.")
                    self.current_key_idx = 0
                    return res
                except Exception as e:
                    import sys
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print(f"DEBUG: [OpenRouter ERROR] {str(e)}")
                    if "quota" not in str(e).lower() and "429" not in str(e).lower() and "insufficient" not in str(e).lower():
                        raise e
            elif not is_openai:
                keys_to_try = self.google_keys[self.current_key_idx:] + self.google_keys[:self.current_key_idx]
                for key in keys_to_try:
                    k_idx = self.google_keys.index(key) + 1
                    try:
                        print(f"DEBUG: [ATTEMPT] Model={current_model} | Key={k_idx}/8")
                        # Extract raw model name for the native SDK
                        raw_model = current_model
                        if current_model.startswith("gemini/"):
                             raw_model = current_model.replace("gemini/", "models/")
                        elif not current_model.startswith("models/"):
                             raw_model = f"models/{current_model}"
                        
                        llm = ChatGoogleGenerativeAI(
                            model=raw_model,
                            google_api_key=key,
                            temperature=kwargs.get("temperature", 0.7),
                            convert_system_message_to_human=True,
                        )
                        
                        # Handle vision for Gemini
                        if image_path and current_model in VISION_MODELS:
                             pass
                        
                        print(f"DEBUG: Calling underlying _generate...")
                        res = llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                        print(f"DEBUG: _generate returned successfully.")
                        self.current_key_idx = self.google_keys.index(key)
                        return res
                    except Exception as e:
                        import sys
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        print(f"DEBUG: [ERROR] Type={exc_type.__name__} | Msg={str(e)} | Line={exc_tb.tb_lineno}")
                        
                        err_msg = str(e).lower()
                        if any(x in err_msg for x in ["404", "not found", "not supported", "not exist"]):
                            break # Skip keys for this model
                        if any(x in err_msg for x in ["429", "resource_exhausted", "quota", "rate limit reached"]):
                            continue # Try next key
                        # Handle transient 500s/503s
                        if any(x in err_msg for x in ["500", "503", "service unavailable", "internal error"]):
                            time.sleep(5)
                            continue
                        raise e
            else:
                try:
                    llm = ChatOpenAI(
                        model=current_model,
                        openai_api_key=os.getenv("OPENAI_API_KEY"),
                        temperature=kwargs.get("temperature", 0.7)
                    )
                    return llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                except Exception as e:
                    if "quota" not in str(e).lower():
                        raise e

            # Fallback logic
            current_model = self._get_fallback_model(current_model)
            self.current_key_idx = 0
            attempts += 1
            time.sleep(3)

        raise RuntimeError("CRITICAL FAILURE: Complete resource exhaustion after exhaustive rotation.")

    def _get_fallback_model(self, failed_model: str) -> str:
        rotation = TEXT_MODELS
        try:
            current_idx = rotation.index(failed_model)
            return rotation[(current_idx + 1) % len(rotation)]
        except ValueError:
            return rotation[0]

    def _sanitize_tools(self, tools: List[Any]) -> List[Any]:
        """
        Recursively removes 'additionalProperties' from tool schemas.
        Gemini's Tool implementation doesn't support this common JSON Schema field.
        """
        sanitized = []
        for tool in tools:
            # Handle different tool types (LangChain tools, dictionaries, etc.)
            if hasattr(tool, "args_schema") and tool.args_schema:
                schema = tool.args_schema.schema()
                schema = self._recursive_remove_additional_props(schema)
                # Note: We can't easily re-assign the schema to a Pydantic model at runtime,
                # but many LLM wrappers accept the raw dictionary or we can wrap it.
                # CrewAI/LangChain handles tool conversion; if we modify the dict passed to the LLM, 
                # that's usually where the error happens.
            
            # If it's already a dict (common in the final call to the API)
            if isinstance(tool, dict):
                tool = self._recursive_remove_additional_props(tool)
            
            sanitized.append(tool)
        return sanitized

    def _recursive_remove_additional_props(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            # Remove the problematic key
            obj.pop("additionalProperties", None)
            # Recursively handle nested dictionaries and lists
            return {k: self._recursive_remove_additional_props(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._recursive_remove_additional_props(i) for i in obj]
        return obj

    @property
    def _llm_type(self) -> str:
        return "resilient_llm"

def get_resilient_llm(model_name="openrouter/qwen/qwen3.5-35b-a3b"):
    return ResilientLLM(model_name=model_name)
