"""
Sample Products Data
This data is used to initialize the vector store for testing and demo purposes.
In production, this would come from PartSelect API or a database.
"""

SAMPLE_PRODUCTS = [
    {
        "id": "PS11752778",
        "name": "Ice Maker Assembly",
        "description": "OEM ice maker assembly for Whirlpool refrigerators. Includes motor and valve assembly.",
        "category": "refrigerator",
        "price": "$89.99",
        "image_url": "https://via.placeholder.com/200?text=Ice+Maker",
        "compatible_models": ["WRF989SDAW", "WRF970SMHW", "WRF535SMHW"],
        "in_stock": True,
        "rating": 4.5,
        "reviews_count": 12,
        "installation_guide": "1. Disconnect refrigerator from power\n2. Remove bottom freezer drawer\n3. Remove old ice maker assembly (unscrew 2 bolts)\n4. Disconnect water line\n5. Install new assembly in reverse order\n6. Reconnect water line and power on",
        "keywords": ["ice maker", "whirlpool", "assembly", "motor"]
    },
    {
        "id": "PS12345678",
        "name": "Refrigerator Door Gasket",
        "description": "Replacement door gasket seal for Whirlpool refrigerators. Prevents cold air leakage.",
        "category": "refrigerator",
        "price": "$34.99",
        "image_url": "https://via.placeholder.com/200?text=Door+Gasket",
        "compatible_models": ["WDT780SAEM1", "WRF989SDAW", "WRF535SMHW"],
        "in_stock": True,
        "rating": 4.8,
        "reviews_count": 45,
        "installation_guide": "1. Open refrigerator door fully\n2. Warm gasket with heat gun for easier removal\n3. Remove old gasket from groove\n4. Insert new gasket into groove all around door\n5. Close door and check for proper seal",
        "keywords": ["gasket", "seal", "door", "whirlpool"]
    },
    {
        "id": "PS87654321",
        "name": "Dishwasher Spray Arm",
        "description": "Upper spray arm for Whirlpool dishwashers. Rotates to distribute water during wash cycle.",
        "category": "dishwasher",
        "price": "$49.99",
        "image_url": "https://via.placeholder.com/200?text=Spray+Arm",
        "compatible_models": ["WDT750SAHZ", "WDT760SAEM", "WDT780SAEM1"],
        "in_stock": True,
        "rating": 4.6,
        "reviews_count": 28,
        "installation_guide": "1. Turn off dishwasher and ensure no water is inside\n2. Remove top rack\n3. Remove old spray arm (twist counterclockwise)\n4. Install new spray arm (twist clockwise until tight)\n5. Replace top rack and run test cycle",
        "keywords": ["spray arm", "dishwasher", "water distribution", "whirlpool"]
    },
    {
        "id": "PS11111111",
        "name": "Dishwasher Filter Basket",
        "description": "Replacement filter basket for Whirlpool dishwashers. Removes food particles from wash water.",
        "category": "dishwasher",
        "price": "$24.99",
        "image_url": "https://via.placeholder.com/200?text=Filter+Basket",
        "compatible_models": ["WDT750SAHZ", "WDT760SAEM", "WDT780SAEM1"],
        "in_stock": True,
        "rating": 4.7,
        "reviews_count": 33,
        "installation_guide": "1. Remove bottom rack from dishwasher\n2. Locate filter basket at bottom center\n3. Remove old filter (pull straight up)\n4. Insert new filter and push down until it clicks\n5. Run test cycle with clean water to verify",
        "keywords": ["filter", "basket", "dishwasher", "food particles"]
    },
    {
        "id": "PS22222222",
        "name": "Refrigerator Compressor",
        "description": "Heavy-duty compressor for Whirlpool refrigerators. Factory OEM part. Requires professional installation.",
        "category": "refrigerator",
        "price": "$299.99",
        "image_url": "https://via.placeholder.com/200?text=Compressor",
        "compatible_models": ["WRF989SDAW", "WRF970SMHW", "WRF535SMHW"],
        "in_stock": False,
        "rating": 4.4,
        "reviews_count": 8,
        "installation_guide": "WARNING: This is a complex component. Professional installation is highly recommended. Installation involves evacuating refrigerant and rewiring electrical connections. Call a certified technician.",
        "keywords": ["compressor", "cooling", "refrigerant", "professional"]
    },
    {
        "id": "PS33333333",
        "name": "Evaporator Coil",
        "description": "Replacement evaporator coil for Whirlpool refrigerators. Cools the refrigerant.",
        "category": "refrigerator",
        "price": "$159.99",
        "image_url": "https://via.placeholder.com/200?text=Evaporator+Coil",
        "compatible_models": ["WRF989SDAW", "WRF970SMHW", "WRF535SMHW"],
        "in_stock": True,
        "rating": 4.5,
        "reviews_count": 15,
        "installation_guide": "1. Unplug refrigerator\n2. Remove back panel of fridge compartment\n3. Locate evaporator coil\n4. Disconnect inlet and outlet tubes\n5. Unscrew mounting brackets\n6. Install new coil in reverse order and reconnect tubes",
        "keywords": ["evaporator", "coil", "cooling", "refrigerant"]
    },
    {
        "id": "PS44444444",
        "name": "Dishwasher Pump Assembly",
        "description": "Complete pump assembly for Whirlpool dishwashers. Circulates water during wash cycles.",
        "category": "dishwasher",
        "price": "$124.99",
        "image_url": "https://via.placeholder.com/200?text=Pump+Assembly",
        "compatible_models": ["WDT750SAHZ", "WDT760SAEM", "WDT780SAEM1"],
        "in_stock": True,
        "rating": 4.6,
        "reviews_count": 22,
        "installation_guide": "1. Turn off dishwasher and cut power supply\n2. Remove bottom spray arm and filter\n3. Locate pump assembly at bottom center\n4. Disconnect electrical connector and drain hose\n5. Remove mounting bolts\n6. Install new pump in reverse order",
        "keywords": ["pump", "assembly", "water circulation", "dishwasher"]
    },
    {
        "id": "PS55555555",
        "name": "Refrigerator Shelving Kit",
        "description": "Complete set of adjustable shelves for Whirlpool refrigerators. Includes all mounting hardware.",
        "category": "refrigerator",
        "price": "$79.99",
        "image_url": "https://via.placeholder.com/200?text=Shelving+Kit",
        "compatible_models": ["WRF989SDAW", "WRF970SMHW", "WRF535SMHW"],
        "in_stock": True,
        "rating": 4.9,
        "reviews_count": 56,
        "installation_guide": "1. Remove old shelves\n2. Install shelf support brackets in desired positions\n3. Place new shelves on brackets\n4. Adjust height as needed (shelves are removable)",
        "keywords": ["shelves", "storage", "adjustable", "organization"]
    },
    {
        "id": "PS66666666",
        "name": "Door Bin Assembly",
        "description": "Replacement door bin for refrigerator. Stores bottles and condiments.",
        "category": "refrigerator",
        "price": "$44.99",
        "image_url": "https://via.placeholder.com/200?text=Door+Bin",
        "compatible_models": ["WRF989SDAW", "WRF535SMHW"],
        "in_stock": True,
        "rating": 4.7,
        "reviews_count": 19,
        "installation_guide": "1. Open refrigerator door\n2. Lift and pull out old door bin\n3. Slide new bin into place until it clicks\n4. Test stability and close door",
        "keywords": ["door bin", "storage", "bottles", "easy install"]
    },
    {
        "id": "PS77777777",
        "name": "Heating Element",
        "description": "Replacement heating element for Whirlpool dishwashers. Heats water during wash cycles.",
        "category": "dishwasher",
        "price": "$89.99",
        "image_url": "https://via.placeholder.com/200?text=Heating+Element",
        "compatible_models": ["WDT750SAHZ", "WDT760SAEM", "WDT780SAEM1"],
        "in_stock": True,
        "rating": 4.5,
        "reviews_count": 14,
        "installation_guide": "1. Unplug dishwasher from power\n2. Remove access panel at bottom\n3. Locate heating element\n4. Disconnect electrical connector\n5. Unscrew mounting bracket\n6. Install new element and reconnect",
        "keywords": ["heating", "element", "water temperature", "dishwasher"]
    }
]


def get_sample_products():
    """Get sample products for initialization"""
    return SAMPLE_PRODUCTS


if __name__ == "__main__":
    # Print sample products for verification
    import json
    print(json.dumps(SAMPLE_PRODUCTS, indent=2))