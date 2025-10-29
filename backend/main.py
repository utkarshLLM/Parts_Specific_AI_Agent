"""
Main API Server
FastAPI/Flask application providing REST endpoints for the chat frontend
"""

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from chat_handler import create_chat_handler, ChatHandler
from vector_store import initialize_vector_store
from sample_products import get_sample_products
import os
from typing import Optional

load_dotenv()  # ← This line is probably missing

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
        chat_handler = create_chat_handler()
    
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
    Returns format that frontend expects
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": {"message": "Message is required"}
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                "success": False,
                "error": {"message": "Message cannot be empty"}
            }), 400
        
        session_id = data.get('sessionId', 'default')
        
        # Process message with chat handler
        result = chat_handler.process_message(user_message, session_id)
        
        # Transform backend response to frontend format
        response_data = {
            "success": True,
            "sessionId": session_id,
            "response": {
                "type": "text",
                "content": result['response_text'],
                "data": {
                    "products": result['products'],
                    "suggestions": result['suggestions'],
                    "intent": result['intent']
                }
            }
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        print(f"Error in /api/chat: {str(e)}")
        return jsonify({
            "success": False,
            "error": {"message": f"Server error: {str(e)}"}
        }), 500


# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@app.route('/api/products/search', methods=['GET'])
def search_products():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                "success": False,
                "error": {"message": "Search query required"}
            }), 400
        
        category = request.args.get('category')
        limit = int(request.args.get('limit', 5))
        
        results = chat_handler.products.search_products(query, category=category, top_k=limit)
        formatted = chat_handler.products.format_products_for_chat(results)
        
        return jsonify({
            "success": True,
            "response": {
                "type": "product_results",
                "content": f"Found {len(formatted)} products",
                "data": {
                    "products": formatted,
                    "query": query
                }
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"message": f"Server error: {str(e)}"}
        }), 500


@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = chat_handler.products.get_product_by_id(product_id)
        
        if not product:
            return jsonify({
                "success": False,
                "error": {"message": f"Product {product_id} not found"}
            }), 404
        
        formatted = chat_handler.products.format_product_for_chat(product)
        
        return jsonify({
            "success": True,
            "response": {
                "type": "product_results",
                "content": f"Product details for {product_id}",
                "data": {
                    "products": [formatted]
                }
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"message": f"Server error: {str(e)}"}
        }), 500


# ============================================================================
# COMPATIBILITY ENDPOINTS
# ============================================================================

@app.route('/api/compatibility', methods=['POST'])
def check_compatibility():
    try:
        data = request.get_json()
        
        if not data or 'part_id' not in data or 'model_number' not in data:
            return jsonify({
                "success": False,
                "error": {"message": "part_id and model_number are required"}
            }), 400
        
        part_id = data['part_id'].upper()
        model_number = data['model_number'].upper()
        
        is_compatible, message = chat_handler.products.check_compatibility(part_id, model_number)
        product = chat_handler.products.search_by_part_number(part_id)
        
        return jsonify({
            "success": True,
            "response": {
                "type": "text",
                "content": message,
                "data": {
                    "compatible": is_compatible,
                    "part": chat_handler.products.format_product_for_chat(product) if product else None,
                    "model_number": model_number
                }
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"message": f"Server error: {str(e)}"}
        }), 500


# ============================================================================
# SESSION ENDPOINTS
# ============================================================================

@app.route('/api/session/info', methods=['GET'])
def get_session_info():
    try:
        session_id = request.args.get('session_id', 'default')
        info = chat_handler.get_session_info(session_id)
        
        if not info:
            return jsonify({
                "success": False,
                "error": {"message": "Session does not exist"}
            }), 404
        
        return jsonify({
            "success": True,
            "response": {
                "type": "text",
                "content": f"Session {session_id} info",
                "data": info
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"message": f"Server error: {str(e)}"}
        }), 500


@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id', 'default')
        
        chat_handler.clear_session(session_id)
        
        return jsonify({
            "success": True,
            "response": {
                "type": "text",
                "content": f"Session {session_id} cleared",
                "data": {"session_id": session_id}
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"message": f"Server error: {str(e)}"}
        }), 500


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