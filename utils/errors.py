import json

class LLMCatchError(Exception):
    """
    Definitive signal for unrecoverable LLM failures (e.g., rate limits, 
    unresponsive models, hallucinated fields, or JSON extraction failures).
    
    This error is designed to be caught by the LangGraph runner to cleanly 
    checkpoint the state and propagate a detailed payload to the frontend.
    """
    def __init__(self, message: str, raw_output: str = None, error_details: str = None, section_id: str = None):
        self.message = message
        self.raw_output = raw_output or ""
        self.error_details = error_details or ""
        self.section_id = section_id or ""
        
        full_msg = message
        if error_details:
            full_msg += f" | Details: {error_details}"
            
        super().__init__(full_msg)

    def to_dict(self):
        return {
            "message": self.message,
            "raw_output": self.raw_output,
            "error_details": self.error_details,
            "section_id": self.section_id
        }
