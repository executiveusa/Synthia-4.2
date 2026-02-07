"""
🤗 HUGGINGFACE MCP SERVER 🤗

Model Context Protocol server for local HuggingFace model deployment
Part of the Aggressive Full Superagent Architecture
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# Try to import transformers
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not installed. HuggingFace models disabled.")


@dataclass
class ModelConfig:
    """Configuration for a HuggingFace model"""
    model_id: str
    display_name: str
    description: str
    max_tokens: int = 2048
    temperature: float = 0.7
    device: str = "auto"  # auto, cpu, cuda
    quantized: bool = False
    loaded: bool = False
    last_used: Optional[str] = None
    use_count: int = 0


class HuggingFaceMCPServer:
    """
    MCP Server for HuggingFace model integration
    Provides local LLM capabilities without API costs
    """
    
    # Recommended models for different tasks
    DEFAULT_MODELS = {
        "code": ModelConfig(
            model_id="microsoft/DialoGPT-medium",
            display_name="Code Assistant",
            description="General purpose code generation and chat",
            max_tokens=2048
        ),
        "chat": ModelConfig(
            model_id="microsoft/DialoGPT-medium",
            display_name="Chat Model",
            description="Conversational AI for general tasks",
            max_tokens=1024
        ),
        "creative": ModelConfig(
            model_id="gpt2",
            display_name="Creative Writer",
            description="Creative writing and story generation",
            max_tokens=1024,
            temperature=0.9
        ),
        "small": ModelConfig(
            model_id="gpt2",
            display_name="Fast Model",
            description="Fast inference for simple tasks",
            max_tokens=512,
            temperature=0.5
        )
    }
    
    def __init__(self, cache_dir: str = "./hf_models"):
        self.cache_dir = cache_dir
        self.models: Dict[str, Any] = {}  # Loaded model instances
        self.tokenizers: Dict[str, Any] = {}  # Loaded tokenizers
        self.configs: Dict[str, ModelConfig] = {}
        self.active_model: Optional[str] = None
        
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize with default models
        for key, config in self.DEFAULT_MODELS.items():
            self.configs[key] = config
        
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Transformers library not available. Install with: pip install transformers torch")
    
    async def load_model(self, model_key: str, force_reload: bool = False) -> bool:
        """Load a HuggingFace model into memory"""
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Cannot load model: transformers not installed")
            return False
        
        if model_key not in self.configs:
            logger.error(f"Unknown model key: {model_key}")
            return False
        
        config = self.configs[model_key]
        
        # Check if already loaded
        if config.loaded and not force_reload and model_key in self.models:
            logger.info(f"Model {model_key} already loaded")
            self.active_model = model_key
            return True
        
        try:
            logger.info(f"Loading model: {config.model_id}")
            
            # Determine device
            device = config.device
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                config.model_id,
                cache_dir=self.cache_dir
            )
            
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                config.model_id,
                cache_dir=self.cache_dir,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None
            )
            
            if device == "cpu":
                model = model.to("cpu")
            
            self.models[model_key] = model
            self.tokenizers[model_key] = tokenizer
            config.loaded = True
            config.last_used = datetime.now().isoformat()
            self.active_model = model_key
            
            logger.info(f"Model {model_key} loaded successfully on {device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_key}: {e}")
            return False
    
    async def unload_model(self, model_key: str) -> bool:
        """Unload a model to free memory"""
        if model_key not in self.models:
            return False
        
        try:
            del self.models[model_key]
            del self.tokenizers[model_key]
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.configs[model_key].loaded = False
            
            if self.active_model == model_key:
                self.active_model = None
            
            logger.info(f"Model {model_key} unloaded")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading model {model_key}: {e}")
            return False
    
    async def generate(self, 
                      prompt: str, 
                      model_key: Optional[str] = None,
                      max_tokens: Optional[int] = None,
                      temperature: Optional[float] = None,
                      stream: bool = False) -> Dict[str, Any]:
        """Generate text using a HuggingFace model"""
        
        if not TRANSFORMERS_AVAILABLE:
            return {
                "error": "Transformers not installed",
                "success": False
            }
        
        # Use specified or active model
        model_key = model_key or self.active_model or "chat"
        
        # Load if not already loaded
        if not self.configs.get(model_key, ModelConfig("", "", "")).loaded:
            success = await self.load_model(model_key)
            if not success:
                return {
                    "error": f"Failed to load model {model_key}",
                    "success": False
                }
        
        config = self.configs[model_key]
        model = self.models[model_key]
        tokenizer = self.tokenizers[model_key]
        
        max_tokens = max_tokens or config.max_tokens
        temperature = temperature or config.temperature
        
        try:
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt")
            
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            config.use_count += 1
            config.last_used = datetime.now().isoformat()
            
            return {
                "success": True,
                "text": generated_text,
                "model": model_key,
                "model_id": config.model_id,
                "tokens_generated": len(outputs[0]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    async def generate_stream(self, 
                             prompt: str,
                             model_key: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Stream generation results"""
        # For streaming, we'd need to implement custom generation loop
        # For now, just yield the full result
        result = await self.generate(prompt, model_key)
        if result["success"]:
            yield result["text"]
        else:
            yield f"Error: {result.get('error', 'Unknown error')}"
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        return [
            {
                "key": key,
                "model_id": config.model_id,
                "display_name": config.display_name,
                "description": config.description,
                "loaded": config.loaded,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "use_count": config.use_count,
                "last_used": config.last_used
            }
            for key, config in self.configs.items()
        ]
    
    def get_model_info(self, model_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a model"""
        if model_key not in self.configs:
            return None
        
        config = self.configs[model_key]
        return {
            "key": model_key,
            "model_id": config.model_id,
            "display_name": config.display_name,
            "description": config.description,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "device": config.device,
            "quantized": config.quantized,
            "loaded": config.loaded,
            "use_count": config.use_count,
            "last_used": config.last_used
        }
    
    async def chat(self, 
                  messages: List[Dict[str, str]], 
                  model_key: Optional[str] = None) -> Dict[str, Any]:
        """Chat completion API compatible with OpenAI format"""
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)
        
        result = await self.generate(prompt, model_key)
        
        if result["success"]:
            return {
                "success": True,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": result["text"]
                    },
                    "finish_reason": "stop"
                }],
                "model": result["model"],
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(result["text"].split()),
                    "total_tokens": len(prompt.split()) + len(result["text"].split())
                }
            }
        else:
            return result
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to prompt string"""
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")
        
        prompt_parts.append("Assistant:")
        return "".join(prompt_parts)
    
    def get_status(self) -> Dict[str, Any]:
        """Get server status"""
        return {
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "cache_dir": self.cache_dir,
            "active_model": self.active_model,
            "loaded_models": sum(1 for c in self.configs.values() if c.loaded),
            "total_models": len(self.configs),
            "cuda_available": torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False,
            "models": self.list_models()
        }
    
    async def add_model(self, 
                       model_key: str, 
                       model_id: str,
                       display_name: str,
                       description: str = "",
                       **kwargs) -> bool:
        """Add a new model configuration"""
        try:
            config = ModelConfig(
                model_id=model_id,
                display_name=display_name,
                description=description,
                **kwargs
            )
            self.configs[model_key] = config
            return True
        except Exception as e:
            logger.error(f"Error adding model: {e}")
            return False


# Singleton instance
_hf_server: Optional[HuggingFaceMCPServer] = None


def get_hf_server() -> HuggingFaceMCPServer:
    """Get singleton HuggingFace MCP server"""
    global _hf_server
    if _hf_server is None:
        _hf_server = HuggingFaceMCPServer()
    return _hf_server