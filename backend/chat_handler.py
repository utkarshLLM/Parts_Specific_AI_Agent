"""
Chat Handler Module
Orchestrates the chat flow, maintains conversation history, and coordinates services
"""

from typing import Dict, List, Optional, Tuple
from deepseek_client import create_deepseek_client, DeepseekClient
from product_service import create_product_service, ProductService


class ChatSession:
    """Manages a single chat session with history and context"""
    
    def __init__(self, session_id: str):
        """Initialize a chat session"""
        self.session_id = session_id
        self.messages: List[Dict] = []  # Conversation history
        self.context_products: List[Dict] = []  # Products mentioned in this session
        self.user_model: Optional[str] = None  # User's appliance model if provided
        self.last_intent: Optional[str] = None  # Last detected intent
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to history"""
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def get_history(self, last_n: int = 6) -> List[Dict]:
        """Get last N messages for context (excluding system messages)"""
        return [m for m in self.messages[-last_n:] if m.get("role") in ["user", "assistant"]]
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.messages = []
        self.context_products = []


class ChatHandler:
    """Main chat handler coordinating services"""
    
    def __init__(self, deepseek_client: Optional[DeepseekClient] = None, product_service: Optional[ProductService] = None):
        """
        Initialize chat handler
        
        Args:
            deepseek_client: Deepseek client instance (created if not provided)
            product_service: Product service instance (created if not provided)
        """
        self.llm = deepseek_client or create_deepseek_client()
        self.products = product_service or create_product_service()
        self.sessions: Dict[str, ChatSession] = {}
    
    def get_or_create_session(self, session_id: str) -> ChatSession:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatSession(session_id)
        return self.sessions[session_id]
    
    def process_message(self, user_message: str, session_id: str = "default") -> Dict:
        """
        Process a user message and generate response
        
        Args:
            user_message: The user's message
            session_id: Session ID for multi-turn conversations
        
        Returns:
            Dictionary with:
            - response_text: LLM response
            - products: Relevant products to display
            - suggestions: Next suggested actions
            - intent: Detected user intent
            - metadata: Additional metadata
        """
        session = self.get_or_create_session(session_id)
        
        # Add user message to history
        session.add_message("user", user_message)
        
        # Extract entities
        part_number = self.llm.extract_part_number(user_message)
        model_number = self.llm.extract_model_number(user_message)
        
        # Update session context
        if model_number:
            session.user_model = model_number
        
        # Analyze intent
        intent_analysis = self.llm.analyze_intent(user_message)
        intent = intent_analysis.get("intent", "product_info")
        session.last_intent = intent
        
        # Get relevant products based on intent
        products = self._get_products_for_intent(user_message, intent, part_number, model_number)
        session.context_products = products
        
        # Build context for LLM
        context = self._build_context(user_message, products, intent, model_number)
        
        # Get LLM response
        response_text = self.llm.get_response(
            user_message=user_message,
            context=context,
            conversation_history=session.get_history()
        )
        
        # Add assistant response to history
        session.add_message("assistant", response_text)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(intent, products)
        
        # Format products for frontend
        formatted_products = self.products.format_products_for_chat(products[:3])
        
        return {
            "response_text": response_text,
            "products": formatted_products,
            "suggestions": suggestions,
            "intent": intent,
            "extracted_part_number": part_number,
            "extracted_model_number": model_number,
            "metadata": {
                "session_id": session_id,
                "message_count": len(session.messages),
                "user_model": session.user_model
            }
        }
    
    def _get_products_for_intent(self, message: str, intent: str, part_number: Optional[str], model_number: Optional[str]) -> List[Dict]:
        """Get relevant products based on intent and extracted entities"""
        
        if intent == "product_info" and part_number:
            # Search by part number
            product = self.products.search_by_part_number(part_number)
            return [product] if product else []
        
        elif intent == "compatibility":
            if part_number and model_number:
                # Check compatibility
                product = self.products.search_by_part_number(part_number)
                return [product] if product else []
            elif model_number:
                # Find parts for model
                return self.products.search_by_model(model_number)
            else:
                return self.products.search_products(message)
        
        elif intent == "installation" and part_number:
            # Get installation guide
            product = self.products.search_by_part_number(part_number)
            return [product] if product else []
        
        elif intent == "troubleshooting":
            # Get troubleshooting guides
            return self.products.get_troubleshooting_guide(message)
        
        elif intent == "order":
            # Generic product search
            return self.products.search_products(message)
        
        else:
            # Default: general search
            return self.products.search_products(message)
    
    def _build_context(self, message: str, products: List[Dict], intent: str, model_number: Optional[str]) -> str:
        """Build context string for LLM"""
        context_parts = []
        
        # Add product information
        if products:
            context_parts.append(self.products.build_context_string(products))
        
        # Add intent-specific context
        if intent == "installation" and products:
            guide = self.products.get_installation_guide(products[0].get('id'))
            if guide:
                context_parts.append(f"\nInstallation Guide:\n{guide}")
        
        elif intent == "compatibility" and model_number:
            context_parts.append(f"\nUser's appliance model: {model_number}")
        
        # Add user model if known
        if model_number:
            context_parts.append(f"\nNote: User has model {model_number}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _generate_suggestions(self, intent: str, products: List[Dict]) -> List[str]:
        """Generate next suggested actions based on intent and products"""
        suggestions = []
        
        if intent == "product_info" and products:
            suggestions.append("Check compatibility with my model")
            suggestions.append("View installation guide")
            suggestions.append("Add to cart")
        
        elif intent == "compatibility":
            if products:
                suggestions.append("Show me installation steps")
                suggestions.append("View other compatible parts")
            suggestions.append("Find parts for another model")
        
        elif intent == "installation":
            suggestions.append("I need troubleshooting help")
            suggestions.append("Find compatible alternatives")
        
        elif intent == "troubleshooting":
            suggestions.append("Show me available parts to fix this")
            suggestions.append("How do I install the replacement part?")
        
        elif intent == "out_of_scope":
            suggestions.append("Tell me about refrigerator parts")
            suggestions.append("Tell me about dishwasher parts")
        
        else:
            suggestions.append("Show me more products")
            suggestions.append("Help me find a part")
        
        return suggestions
    
    def clear_session(self, session_id: str) -> None:
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get information about a session"""
        session = self.sessions.get(session_id)
        if not session:
            return {}
        
        return {
            "session_id": session_id,
            "message_count": len(session.messages),
            "user_model": session.user_model,
            "last_intent": session.last_intent,
            "products_mentioned": len(session.context_products)
        }


def create_chat_handler(deepseek_api_key: Optional[str] = None) -> ChatHandler:
    """Factory function to create chat handler with all dependencies"""
    llm = create_deepseek_client(api_key=deepseek_api_key)
    products = create_product_service()
    return ChatHandler(deepseek_client=llm, product_service=products)