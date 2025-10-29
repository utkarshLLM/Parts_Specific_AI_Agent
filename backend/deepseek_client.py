"""
Deepseek LLM Client Module
Handles all interactions with the Deepseek language model API
"""

import requests
import json
from typing import Dict, List, Optional


class DeepseekClient:
    """Client for interacting with Deepseek API"""
    
    # System prompt enforces scope and behavior
    SYSTEM_PROMPT = """You are an expert customer support assistant for PartSelect, specializing in refrigerator and dishwasher parts. 

Your responsibilities:
1. Help customers find compatible parts for their appliances
2. Provide installation guidance for parts
3. Troubleshoot common refrigerator and dishwasher issues
4. Answer questions about part compatibility
5. Assist with ordering and product information

IMPORTANT RULES:
- ONLY answer questions related to refrigerator and dishwasher parts
- If a question is outside this scope, politely decline and redirect: "I can only help with refrigerator and dishwasher parts. Is there anything I can help you with regarding these?"
- Be concise and practical in your responses
- When providing installation steps, prioritize safety
- Always mention part numbers when relevant
- If you don't have specific information, be honest about it
- Suggest related products or services when appropriate

Current date: You are helpful and knowledgeable."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com/v1"):
        """
        Initialize Deepseek client
        
        Args:
            api_key: Deepseek API key (can be set via environment variable DEEPSEEK_API_KEY)
            base_url: Base URL for Deepseek API
        """
        import os
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.model = "deepseek-chat"
        
        if not self.api_key:
            raise ValueError("Deepseek API key not provided. Set DEEPSEEK_API_KEY environment variable.")
    
    def get_response(self, user_message: str, context: str = "", conversation_history: List[Dict] = None) -> str:
        """
        Get response from Deepseek API
        
        Args:
            user_message: The user's current message
            context: Additional context (e.g., product information)
            conversation_history: Previous messages in format [{"role": "user"/"assistant", "content": "..."}]
        
        Returns:
            Response text from the model
        """
        # Build messages list
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add system prompt with context
        system_msg = self.SYSTEM_PROMPT
        if context:
            system_msg += f"\n\nContext Information:\n{context}"
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "system", "content": system_msg}] + messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.95
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract response text
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "I encountered an issue processing your request. Please try again."
        
        except requests.exceptions.ConnectionError:
            return "Connection error: Unable to reach the Deepseek API. Please check your internet connection."
        except requests.exceptions.Timeout:
            return "Request timeout: The API took too long to respond. Please try again."
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return "Authentication error: Invalid Deepseek API key."
            elif e.response.status_code == 429:
                return "Rate limit exceeded: Too many requests. Please wait a moment and try again."
            else:
                return f"API error: {e.response.status_code}. Please try again."
        except json.JSONDecodeError:
            return "Error parsing API response. Please try again."
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def analyze_intent(self, user_message: str) -> Dict[str, any]:
        """
        Analyze user message to determine intent
        
        Returns dict with:
        - intent: 'product_info', 'compatibility', 'installation', 'troubleshooting', 'order', 'out_of_scope'
        - entities: extracted entities (part numbers, model numbers, etc.)
        - confidence: confidence score 0-1
        """
        intent_prompt = f"""Analyze this customer message and determine their intent. Respond in JSON format only.

Message: "{user_message}"

Respond with exactly this JSON structure:
{{"intent": "product_info|compatibility|installation|troubleshooting|order|out_of_scope", "entities": {{}}, "confidence": 0.0}}

Examples of intents:
- product_info: "What is this part?", "Tell me about PS123456"
- compatibility: "Is this compatible with my WDT780SAEM1?", "Will this work?"
- installation: "How do I install this?", "Installation steps"
- troubleshooting: "My ice maker isn't working", "How do I fix..."
- order: "How do I buy this?", "Add to cart"
- out_of_scope: anything not related to fridge/dishwasher parts"""
        
        response = self.get_response(intent_prompt, context="")
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^{}]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback to keyword matching
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['how', 'install', 'step', 'guide']):
            intent = 'installation'
        elif any(word in message_lower for word in ['compatible', 'work', 'fit', 'model']):
            intent = 'compatibility'
        elif any(word in message_lower for word in ['problem', 'broken', 'issue', 'fix', 'help', 'not working']):
            intent = 'troubleshooting'
        elif any(word in message_lower for word in ['buy', 'order', 'cart', 'price', 'cost']):
            intent = 'order'
        elif any(word in message_lower for word in ['ps', 'part', 'number', 'what', 'tell me']):
            intent = 'product_info'
        else:
            intent = 'out_of_scope'
        
        return {
            "intent": intent,
            "entities": {},
            "confidence": 0.7
        }
    
    def extract_part_number(self, text: str) -> Optional[str]:
        """Extract part number from text (format: PSxxxxxxxx)"""
        import re
        match = re.search(r'PS\d{8}', text)
        return match.group(0) if match else None
    
    def extract_model_number(self, text: str) -> Optional[str]:
        """Extract model number from text (format: WDT/WRF followed by numbers)"""
        import re
        # Common patterns for Whirlpool, LG, Samsung models
        match = re.search(r'(?:PS|WDT|WRF|WMTF|LEC|LSC|RS|RFG|RF)\d{6,10}', text)
        return match.group(0) if match else None


def create_deepseek_client(api_key: Optional[str] = None) -> DeepseekClient:
    """Factory function to create Deepseek client"""
    return DeepseekClient(api_key=api_key)