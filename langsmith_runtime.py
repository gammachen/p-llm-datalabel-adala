import os
import logging
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from adala.runtimes import OpenAIChatRuntime

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Try to import LangSmith, but don't fail if not available
try:
    from langsmith import Client
    from langsmith.run_helpers import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    logger.warning("LangSmith not available. Install with: pip install langsmith")


class LangSmithOpenAIChatRuntime(OpenAIChatRuntime):
    """
    OpenAIChatRuntime with LangSmith tracing support.
    
    This runtime extends the base OpenAIChatRuntime to add detailed tracing
    of all LLM calls, inputs, outputs, and metadata for better observability.
    """
    
    def __init__(self, **kwargs):
        # Call parent constructor first
        super().__init__(**kwargs)
        
        # Initialize LangSmith if available
        self._setup_langsmith()
    
    def _setup_langsmith(self):
        """Setup LangSmith client and configuration."""
        try:
            # Initialize LangSmith attributes
            self._tracing_enabled = False
            self._langsmith_client = None
            self._project_name = "adala-agent"
            
            if not LANGSMITH_AVAILABLE:
                logger.warning("LangSmith not available. Tracing will be disabled.")
                return
            
            api_key = os.getenv("LANGSMITH_API_KEY")
            if not api_key:
                logger.warning("LANGSMITH_API_KEY not found. Tracing will be disabled.")
                return
            
            self._langsmith_client = Client(
                api_url=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"),
                api_key=api_key
            )
            
            self._project_name = os.getenv("LANGSMITH_PROJECT", "adala-agent")
            self._tracing_enabled = True
            
            logger.info(f"✅ LangSmith tracing enabled for project: {self._project_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup LangSmith: {e}")
            self._tracing_enabled = False
    
    @property
    def tracing_enabled(self) -> bool:
        """Get tracing enabled status."""
        return getattr(self, '_tracing_enabled', False)
    
    @property
    def project_name(self) -> str:
        """Get project name."""
        return getattr(self, '_project_name', 'adala-agent')
    
    def init_runtime(self) -> "Runtime":
        """
        Initialize runtime with LangSmith support.
        Override to avoid model availability check during initialization.
        """
        # Skip model availability check for Ollama compatibility
        if hasattr(self, '_client') and self._client is None:
            try:
                # Only try to initialize client if we have the necessary imports
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.openai_api_key,
                    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
                )
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")
        
        return self
    
    def execute(self, messages: List[Dict[str, Any]]) -> str:
        """
        Execute OpenAI request with LangSmith tracing.
        """
        if not self.tracing_enabled:
            return OpenAIChatRuntime.execute(self, messages)
        
        # Extract input text for tracing
        input_text = self._extract_input_text(messages)
        
        # Create run name for tracing
        timestamp = int(time.time())
        run_name = f"adala-{self.openai_model}-{timestamp}"
        
        try:
            # Use LangSmith traceable decorator
            @traceable(
                name=run_name,
                project_name=self.project_name,
                tags=["adala", "sentiment-analysis", "ollama", "llama3", "execute"],
                metadata={
                    "model": self.openai_model,
                    "runtime_type": "OpenAIChatRuntime",
                    "framework": "adala",
                    "input_length": len(input_text),
                    "message_count": len(messages),
                    "timestamp": timestamp
                }
            )
            def traced_execute():
                # Call the parent class method directly
                return OpenAIChatRuntime.execute(self, messages)
            
            # Execute with tracing
            start_time = time.time()
            completion_text = traced_execute()
            execution_time = time.time() - start_time
            
            # Log the execution
            logger.info(f"✅ LangSmith traced execution completed: {run_name} (took {execution_time:.2f}s)")
            
            return completion_text
            
        except Exception as e:
            logger.error(f"❌ Error in traced execution: {e}")
            # Fallback to non-traced execution
            return OpenAIChatRuntime.execute(self, messages)
    
    def record_to_record(
        self,
        record: Dict[str, str],
        input_template: str,
        instructions_template: str,
        output_template: str,
        extra_fields: Optional[Dict[str, str]] = None,
        field_schema: Optional[Dict] = None,
        instructions_first: bool = False,
    ) -> Dict[str, str]:
        """
        Execute OpenAI request with LangSmith tracing for record-to-record operations.
        """
        if not self.tracing_enabled:
            return super().record_to_record(
                record, input_template, instructions_template, output_template,
                extra_fields, field_schema, instructions_first
            )
        
        # Create run name for tracing
        timestamp = int(time.time())
        record_hash = hash(str(record)) % 10000
        run_name = f"adala-record-{record_hash}-{timestamp}"
        
        try:
            @traceable(
                name=run_name,
                project_name=self.project_name,
                tags=["adala", "record-to-record", "sentiment-analysis"],
                metadata={
                    "model": self.openai_model,
                    "runtime_type": "OpenAIChatRuntime",
                    "framework": "adala",
                    "input_template": input_template,
                    "instructions_template": instructions_template,
                    "output_template": output_template,
                    "record_keys": list(record.keys()),
                    "extra_fields": extra_fields,
                    "field_schema": field_schema,
                    "instructions_first": instructions_first,
                    "timestamp": timestamp
                }
            )
            def traced_record_to_record():
                # Call the parent class method directly
                return OpenAIChatRuntime.record_to_record(
                    self, record, input_template, instructions_template, output_template,
                    extra_fields, field_schema, instructions_first
                )
            
            # Execute with tracing
            start_time = time.time()
            result = traced_record_to_record()
            execution_time = time.time() - start_time
            
            # Log the execution
            logger.info(f"✅ LangSmith traced record-to-record completed: {run_name} (took {execution_time:.2f}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in traced record-to-record execution: {e}")
            # Fallback to non-traced execution
            return OpenAIChatRuntime.record_to_record(
                self, record, input_template, instructions_template, output_template,
                extra_fields, field_schema, instructions_first
            )
    
    def _extract_input_text(self, messages: List[Dict[str, Any]]) -> str:
        """
        Extract input text from messages for tracing purposes.
        """
        if not messages:
            return ""
        
        # Combine all message content
        text_parts = []
        for message in messages:
            if isinstance(message.get("content"), str):
                text_parts.append(message["content"])
            elif isinstance(message.get("content"), list):
                # Handle multimodal content
                for content_item in message["content"]:
                    if isinstance(content_item, dict) and content_item.get("type") == "text":
                        text_parts.append(content_item.get("text", ""))
        
        return " ".join(text_parts)
    
    def get_trace_url(self, run_id: str) -> str:
        """
        Get the URL for viewing a specific trace in LangSmith.
        """
        if not self.tracing_enabled:
            return "Tracing not enabled"
        
        base_url = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        if base_url.startswith("https://api.smith.langchain.com"):
            return f"https://smith.langchain.com/runs/{run_id}"
        else:
            return f"{base_url}/runs/{run_id}"
    
    def get_tracing_status(self) -> Dict[str, Any]:
        """
        Get the current tracing status and configuration.
        """
        return {
            "tracing_enabled": self.tracing_enabled,
            "langsmith_available": LANGSMITH_AVAILABLE,
            "project_name": self.project_name,
            "model": self.openai_model,
            "api_key_configured": bool(os.getenv("LANGSMITH_API_KEY"))
        } 