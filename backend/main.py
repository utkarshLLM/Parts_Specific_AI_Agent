"""
Main API Server
FastAPI/Flask application providing REST endpoints for the chat frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from chat_handler import create_chat_handler, ChatHandler
from vector_store import initialize_vector_store
from sample_products import get_sample_products
import os
from typing import Optional

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Global chat handler instance
chat_handler: Optional[ChatHandler] = None


def initialize_backend():
    """Initialize all backend services"""
    global chat_handler
    
    print("Initializing Instalily AI Chat Backend...")
    
    # Initialize vector store with sample products
    print("Loading product catalog...")
    products = get_sample_products()
    initialize_vector_store(products)
    print(f"✓ Loaded {len(products)} products")
    
    # Initialize chat handler
    print("Initializing chat handler...")
    try:
        chat_handler = create_chat_handler()
        print("✓ Chat handler ready")
    except ValueError as e:
        print(f"⚠ Warning: {e}")
        print("  Set DEEPSEEK_API_KEY environment variable to enable LLM features")
        chat_handler = create_chat_handler(api_key="test-key")
    
    print("✓ Backend initialization complete\n")


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "Instalily AI Chat Backend",
        "version": "1.0.0"
    }), 200


@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information"""
    return jsonify({
        "name": "Instalily AI Chat API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/api/info",
            "/api/chat",
            "/api/products/search",
            "/api/products/:id",
            "/api/compatibility",
            "/api/session/info"
        ],
        "models": ["refrigerator", "dishwasher"],
        "deepseek_available": chat_handler is not None
    }), 200


# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    
    Request body:
    {
        "message": "How can I install part number PS11752778?",
        "session_id": "user-123" (optional, defaults to "default")
    }
    
    Response:
    {
        "response_text": "...",
        "products": [...],
        "suggestions": [...],
        "intent": "installation",
        "metadata": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        session_id = data.get('session_id', 'default')
        
        # Process message with chat handler
        result = chat_handler.process_message(user_message, session_id)
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error in /api/chat: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@app.route('/api/products/search', methods=['GET'])
def search_products():
    """
    Search for products
    
    Query parameters:
    - q: Search query (required)
    - category: Filter by category ('refrigerator' or 'dishwasher')
    - limit: Max results (default 5)
    
    Response:
    {
        "products": [...],
        "count": 5
    }
    """
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({"error": "Search query required"}), 400
        
        category = request.args.get('category')
        limit = int(request.args.get('limit', 5))
        
        # Search products
        results = chat_handler.products.search_products(query, category=category, top_k=limit)
        formatted = chat_handler.products.format_products_for_chat(results)
        
        return jsonify({
            "products": formatted,
            "count": len(formatted),
            "query": query
        }), 200
    
    except Exception as e:
        print(f"Error in /api/products/search: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get a specific product by ID
    
    Response:
    {
        "product": {...},
        "found": true/false
    }
    """
    try:
        product = chat_handler.products.get_product_by_id(product_id)
        
        if not product:
            return jsonify({
                "product": None,
                "found": False,
                "message": f"Product {product_id} not found"
            }), 404
        
        formatted = chat_handler.products.format_product_for_chat(product)
        
        return jsonify({
            "product": formatted,
            "found": True
        }), 200
    
    except Exception as e:
        print(f"Error in /api/products/<id>: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ============================================================================
# COMPATIBILITY ENDPOINTS
# ============================================================================

@app.route('/api/compatibility', methods=['POST'])
def check_compatibility():
    """
    Check if a part is compatible with a model
    
    Request body:
    {
        "part_id": "PS11752778",
        "model_number": "WDT780SAEM1"
    }
    
    Response:
    {
        "compatible": true/false,
        "message": "...",
        "part": {...},
        "model_number": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'part_id' not in data or 'model_number' not in data:
            return jsonify({"error": "part_id and model_number are required"}), 400
        
        part_id = data['part_id'].upper()
        model_number = data['model_number'].upper()
        
        # Check compatibility
        is_compatible, message = chat_handler.products.check_compatibility(part_id, model_number)
        product = chat_handler.products.search_by_part_number(part_id)
        
        response = {
            "compatible": is_compatible,
            "message": message,
            "part": chat_handler.products.format_product_for_chat(product) if product else None,
            "model_number": model_number
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error in /api/compatibility: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ============================================================================
# SESSION ENDPOINTS
# ============================================================================

@app.route('/api/session/info', methods=['GET'])
def get_session_info():
    """
    Get information about a session
    
    Query parameters:
    - session_id: Session ID (optional, defaults to 'default')
    
    Response:
    {
        "session_id": "...",
        "message_count": 5,
        "user_model": "...",
        "last_intent": "..."
    }
    """
    try:
        session_id = request.args.get('session_id', 'default')
        info = chat_handler.get_session_info(session_id)
        
        if not info:
            return jsonify({
                "session_id": session_id,
                "exists": False,
                "message": "Session does not exist"
            }), 404
        
        return jsonify({
            **info,
            "exists": True
        }), 200
    
    except Exception as e:
        print(f"Error in /api/session/info: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    """
    Clear a session
    
    Request body:
    {
        "session_id": "user-123" (optional, defaults to 'default')
    }
    
    Response:
    {
        "cleared": true,
        "session_id": "..."
    }
    """
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id', 'default')
        
        chat_handler.clear_session(session_id)
        
        return jsonify({
            "cleared": True,
            "session_id": session_id,
            "message": f"Session {session_id} cleared"
        }), 200
    
    except Exception as e:
        print(f"Error in /api/session/clear: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


@app.before_request
def before_request():
    """Before request handler - validate requests"""
    if request.method == 'POST':
        if request.content_type and 'application/json' not in request.content_type:
            return jsonify({"error": "Content-Type must be application/json"}), 400


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def main():
    """Start the application"""
    # Initialize backend services
    initialize_backend()
    
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"Starting Instalily AI Chat Server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Frontend should call: http://localhost:{port}/api/chat\n")
    
    # Run the app
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()