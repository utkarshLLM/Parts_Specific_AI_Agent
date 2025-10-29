"""
Product Service Module
Handles product data retrieval, filtering, and formatting
"""

from typing import List, Dict, Optional, Tuple
from vector_store import get_vector_store


class ProductService:
    """Service for product queries and operations"""
    
    # Product categories
    CATEGORIES = {
        'refrigerator': ['ice maker parts', 'compressor parts', 'evaporator coils', 'gaskets', 'shelves', 'drawers'],
        'dishwasher': ['spray arms', 'filters', 'pumps', 'racks', 'heating elements', 'door seals']
    }
    
    def __init__(self):
        """Initialize product service"""
        self.vector_store = get_vector_store()
    
    def search_products(self, query: str, category: Optional[str] = None, top_k: int = 5) -> List[Dict]:
        """
        Search for products using vector similarity
        
        Args:
            query: Search query string
            category: Optional category filter ('refrigerator' or 'dishwasher')
            top_k: Number of results to return
        
        Returns:
            List of product dictionaries sorted by relevance
        """
        if not self.vector_store.initialized:
            return []
        
        # Search in vector store
        results = self.vector_store.search(query, top_k=top_k * 2)  # Get more to filter
        
        # Filter by category if specified
        if category:
            category = category.lower()
            results = [p for p in results if p.get('category', '').lower() == category]
        
        # Return top_k results
        return results[:top_k]
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get a specific product by ID"""
        return self.vector_store.get_by_id(product_id)
    
    def search_by_part_number(self, part_number: str) -> Optional[Dict]:
        """Search for a product by part number"""
        part_number = part_number.upper()
        for product in self.vector_store.metadata:
            if product.get('id', '').upper() == part_number or product.get('part_number', '').upper() == part_number:
                return product
        return None
    
    def check_compatibility(self, part_id: str, model_number: str) -> Tuple[bool, str]:
        """
        Check if a part is compatible with a specific model
        
        Returns:
            Tuple of (is_compatible, reason_message)
        """
        part = self.search_by_part_number(part_id)
        if not part:
            return False, f"Part {part_id} not found in catalog"
        
        compatible_models = part.get('compatible_models', [])
        if isinstance(compatible_models, str):
            compatible_models = [compatible_models]
        
        model_number = model_number.upper()
        for compat_model in compatible_models:
            if model_number in str(compat_model).upper():
                return True, f"Part {part_id} is compatible with {model_number}"
        
        return False, f"Part {part_id} is not compatible with {model_number}. Compatible models: {', '.join(compatible_models[:3])}"
    
    def search_by_model(self, model_number: str) -> List[Dict]:
        """Find all parts compatible with a model"""
        results = self.vector_store.search_by_model(model_number)
        return results
    
    def get_installation_guide(self, part_id: str) -> Optional[str]:
        """Get installation guide for a part"""
        part = self.search_by_part_number(part_id)
        if part:
            return part.get('installation_guide', 'Installation guide not available')
        return None
    
    def get_troubleshooting_guide(self, issue: str, appliance_type: str = None) -> List[Dict]:
        """Get troubleshooting guides for common issues"""
        query = f"troubleshoot {issue}"
        if appliance_type:
            query += f" {appliance_type}"
        
        results = self.search_products(query, top_k=3)
        return results
    
    def format_product_for_chat(self, product: Dict) -> Dict:
        """
        Format product data for chat display
        
        Returns:
            Dictionary with frontend-friendly fields
        """
        if not product:
            return {}
        
        return {
            'id': product.get('id'),
            'name': product.get('name'),
            'description': product.get('description', ''),
            'price': product.get('price', 'N/A'),
            'image_url': product.get('image_url', ''),
            'category': product.get('category', ''),
            'part_number': product.get('id'),  # Part number is the ID
            'compatible_models': product.get('compatible_models', []),
            'in_stock': product.get('in_stock', True),
            'rating': product.get('rating', 0),
            'reviews_count': product.get('reviews_count', 0),
            'link': f"https://www.partselect.com/products/{product.get('id', '')}",
            'relevance_score': product.get('score', 0)
        }
    
    def format_products_for_chat(self, products: List[Dict]) -> List[Dict]:
        """Format multiple products for chat display"""
        return [self.format_product_for_chat(p) for p in products]
    
    def build_context_string(self, products: List[Dict]) -> str:
        """
        Build a context string from products for passing to LLM
        
        Args:
            products: List of product dictionaries
        
        Returns:
            Formatted context string for LLM
        """
        if not products:
            return "No products found."
        
        context_lines = ["Here are relevant products from our catalog:"]
        
        for i, product in enumerate(products, 1):
            context_lines.append(f"\n{i}. {product.get('name', 'Unknown')}")
            context_lines.append(f"   Part Number: {product.get('id')}")
            context_lines.append(f"   Category: {product.get('category')}")
            
            if product.get('compatible_models'):
                models = product.get('compatible_models')
                if isinstance(models, list):
                    models = ', '.join(models[:3])
                context_lines.append(f"   Compatible with: {models}")
            
            if product.get('price'):
                context_lines.append(f"   Price: {product.get('price')}")
            
            if product.get('description'):
                desc = product.get('description')[:150] + "..." if len(product.get('description', '')) > 150 else product.get('description')
                context_lines.append(f"   Description: {desc}")
            
            if product.get('in_stock') == False:
                context_lines.append(f"   Status: OUT OF STOCK")
        
        return "\n".join(context_lines)


def create_product_service() -> ProductService:
    """Factory function to create product service"""
    return ProductService()