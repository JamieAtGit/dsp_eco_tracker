#!/usr/bin/env python3
"""
Enhanced Eco Dataset Generator

Generates a comprehensive dataset of 50,000 products prioritized by commonality:
- Priority 1: 20,000 common everyday items
- Priority 2: 15,000 mid-tier common items  
- Priority 3: 15,000 less common but relevant items

Uses realistic product names, materials, and attributes based on real-world data.
"""

import csv
import json
import random
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

# Set random seed for reproducible results
random.seed(42)

@dataclass
class ProductTemplate:
    """Template for generating realistic products"""
    name_patterns: List[str]
    materials: List[str]
    weight_range: Tuple[float, float]  # kg
    transport_modes: List[str]
    recyclability_options: List[str]
    category: str
    typical_origins: List[str]
    lifespan_range: Tuple[float, float]  # years
    repairability_range: Tuple[int, int]
    size_categories: List[str]
    quality_levels: List[str]
    packaging_types: List[str]
    volume_range: Tuple[float, float]  # liters

class EnhancedDatasetGenerator:
    def __init__(self):
        self.brand_locations = self.load_brand_locations()
        self.co2_intensities = {
            'Plastic': 3.4, 'Metal': 2.8, 'Glass': 1.2, 'Paper': 0.9, 
            'Wood': 0.7, 'Textile': 5.5, 'Ceramic': 1.8, 'Rubber': 2.1,
            'Electronic': 8.2, 'Composite': 4.1, 'Leather': 6.3, 'Cotton': 4.8,
            'Polyester': 5.9, 'Steel': 2.9, 'Aluminum': 8.5, 'Bamboo': 0.4,
            'Cardboard': 0.8, 'Silicon': 12.1, 'Lithium': 15.2
        }
        self.transport_co2 = {'Land': 0.15, 'Ship': 0.03, 'Air': 0.5}
        
        # Initialize product templates
        self.priority1_templates = self._init_priority1_templates()
        self.priority2_templates = self._init_priority2_templates()
        self.priority3_templates = self._init_priority3_templates()
        
    def load_brand_locations(self) -> Dict[str, str]:
        """Load brand location mappings"""
        try:
            with open('/Users/jamie/Documents/University/dsp_eco_tracker/common/data/json/brand_locations.json', 'r') as f:
                data = json.load(f)
                # Remove metadata entry
                if '_metadata' in data:
                    del data['_metadata']
                return data
        except Exception as e:
            print(f"Warning: Could not load brand locations: {e}")
            return self._fallback_brands()
    
    def _fallback_brands(self) -> Dict[str, str]:
        """Fallback brand mappings if file not available"""
        return {
            'Apple': 'China', 'Samsung': 'Vietnam', 'Google': 'China', 'Microsoft': 'China',
            'Amazon': 'China', 'Nike': 'Vietnam', 'Adidas': 'Indonesia', 'IKEA': 'China',
            'Sony': 'Japan', 'LG': 'South Korea', 'Dell': 'China', 'HP': 'China',
            'Lenovo': 'China', 'Asus': 'Taiwan', 'Acer': 'Taiwan', 'MSI': 'Taiwan',
            'Canon': 'Japan', 'Nikon': 'Thailand', 'Panasonic': 'Japan', 'Philips': 'China'
        }
    
    def _init_priority1_templates(self) -> List[ProductTemplate]:
        """Initialize templates for Priority 1: Common everyday items (20,000 products)"""
        return [
            # Electronics (5,000 products)
            ProductTemplate(
                name_patterns=[
                    "iPhone {model} {storage}GB", "Samsung Galaxy S{num}", "Google Pixel {num}",
                    "iPad {model}", "Samsung Galaxy Tab A{num}", "MacBook Air {inch}\"",
                    "Dell XPS {num}", "HP Pavilion {model}", "Lenovo ThinkPad {model}",
                    "AirPods {model}", "Sony WH-{model}", "JBL {model}", "Beats {model}",
                    "Apple Watch Series {num}", "Samsung Galaxy Watch {num}", "Fitbit {model}",
                    "iPhone Charger", "USB-C Cable", "Wireless Charger", "Power Bank {capacity}mAh"
                ],
                materials=['Electronic', 'Plastic', 'Metal', 'Glass'],
                weight_range=(0.05, 2.5),
                transport_modes=['Air', 'Ship'],
                recyclability_options=['Low', 'Medium'],
                category='Electronics',
                typical_origins=['China', 'Vietnam', 'Taiwan', 'Japan', 'South Korea'],
                lifespan_range=(2.0, 8.0),
                repairability_range=(2, 6),
                size_categories=['small', 'medium'],
                quality_levels=['standard', 'premium'],
                packaging_types=['box', 'blister'],
                volume_range=(0.01, 2.0)
            ),
            
            # Clothing (8,000 products)
            ProductTemplate(
                name_patterns=[
                    "Nike Air Max {model}", "Adidas Ultraboost {num}", "Converse Chuck Taylor",
                    "Vans Old Skool", "New Balance {model}", "Puma {model}",
                    "Levi's 501 Jeans", "Wrangler {model} Jeans", "Gap Straight Fit Jeans",
                    "H&M Basic T-Shirt", "Uniqlo {model} Tee", "Gap Essential Tee",
                    "Nike Dri-FIT Shirt", "Adidas {model} Hoodie", "Champion Hoodie",
                    "Calvin Klein {model}", "Hanes {model}", "Fruit of the Loom {model}",
                    "The North Face {model} Jacket", "Patagonia {model}", "Columbia {model}"
                ],
                materials=['Cotton', 'Polyester', 'Textile', 'Leather', 'Synthetic'],
                weight_range=(0.1, 1.5),
                transport_modes=['Ship', 'Air'],
                recyclability_options=['Medium', 'High'],
                category='Clothing',
                typical_origins=['Bangladesh', 'Vietnam', 'China', 'India', 'Turkey'],
                lifespan_range=(1.0, 10.0),
                repairability_range=(3, 8),
                size_categories=['small', 'medium'],
                quality_levels=['budget', 'standard', 'premium'],
                packaging_types=['bag', 'box'],
                volume_range=(0.1, 3.0)
            ),
            
            # Household Items (4,000 products)
            ProductTemplate(
                name_patterns=[
                    "IKEA {model} Knife Set", "Cuisinart {model}", "KitchenAid {model}",
                    "Pyrex Glass Bowls", "Tupperware {model}", "Rubbermaid {model}",
                    "Dawn Dish Soap", "Tide Laundry Detergent", "Bounty Paper Towels",
                    "Charmin Toilet Paper", "Lysol {model}", "Febreze {model}",
                    "Glad Trash Bags", "Ziploc Storage Bags", "Reynolds Wrap",
                    "Brita Water Filter", "Keurig K-Cups", "Ninja Blender"
                ],
                materials=['Plastic', 'Metal', 'Glass', 'Paper', 'Ceramic'],
                weight_range=(0.05, 3.0),
                transport_modes=['Land', 'Ship'],
                recyclability_options=['Medium', 'High'],
                category='Household',
                typical_origins=['China', 'USA', 'Mexico', 'Germany'],
                lifespan_range=(0.5, 15.0),
                repairability_range=(1, 7),
                size_categories=['small', 'medium', 'large'],
                quality_levels=['budget', 'standard'],
                packaging_types=['bottle', 'box', 'bag'],
                volume_range=(0.05, 5.0)
            ),
            
            # Personal Care (3,000 products)
            ProductTemplate(
                name_patterns=[
                    "Head & Shoulders Shampoo", "Pantene {model}", "L'Oreal {model}",
                    "Oral-B Toothbrush", "Colgate {model}", "Crest {model}",
                    "Dove Body Wash", "Irish Spring {model}", "Old Spice {model}",
                    "Gillette {model} Razor", "Schick {model}", "Venus {model}",
                    "Maybelline {model}", "CoverGirl {model}", "Revlon {model}",
                    "Neutrogena {model}", "Cetaphil Daily Cleanser", "Aveeno {model}"
                ],
                materials=['Plastic', 'Metal', 'Glass', 'Paper'],
                weight_range=(0.02, 0.8),
                transport_modes=['Land', 'Ship'],
                recyclability_options=['Medium', 'High'],
                category='Personal Care',
                typical_origins=['USA', 'France', 'Germany', 'China'],
                lifespan_range=(0.1, 3.0),
                repairability_range=(1, 3),
                size_categories=['small', 'medium'],
                quality_levels=['budget', 'standard', 'premium'],
                packaging_types=['bottle', 'tube', 'box'],
                volume_range=(0.01, 1.0)
            )
        ]
    
    def _init_priority2_templates(self) -> List[ProductTemplate]:
        """Initialize templates for Priority 2: Mid-tier common items (15,000 products)"""
        return [
            # Home Appliances (4,000 products)
            ProductTemplate(
                name_patterns=[
                    "Keurig K-Elite Coffee Maker", "Mr. Coffee {model}", "Hamilton Beach {model}",
                    "Ninja Professional Blender", "Vitamix {model}", "Magic Bullet {model}",
                    "Dyson V{num} Vacuum", "Shark Navigator", "Bissell {model}",
                    "Honeywell Air Purifier", "Levoit {model}", "Winix {model}",
                    "Instant Pot {model}", "Crock-Pot {model}", "Ninja Foodi {model}"
                ],
                materials=['Plastic', 'Metal', 'Electronic', 'Glass'],
                weight_range=(1.0, 15.0),
                transport_modes=['Ship', 'Land'],
                recyclability_options=['Low', 'Medium'],
                category='Appliances',
                typical_origins=['China', 'Mexico', 'USA', 'Germany'],
                lifespan_range=(3.0, 12.0),
                repairability_range=(3, 7),
                size_categories=['medium', 'large'],
                quality_levels=['standard', 'premium'],
                packaging_types=['box'],
                volume_range=(2.0, 20.0)
            ),
            
            # Sports & Fitness (4,000 products)
            ProductTemplate(
                name_patterns=[
                    "Manduka Pro Yoga Mat", "Gaiam {model}", "BalanceFrom {model}",
                    "Bowflex SelectTech Dumbbells", "CAP Barbell {model}", "Yes4All {model}",
                    "Nike Air Zoom Pegasus", "Brooks Ghost {num}", "ASICS Gel-Kayano",
                    "Hydro Flask Water Bottle", "YETI Rambler", "Nalgene {model}",
                    "Fitbit Charge {num}", "Garmin Forerunner", "Apple Watch SE"
                ],
                materials=['Rubber', 'Metal', 'Plastic', 'Textile', 'Electronic'],
                weight_range=(0.2, 25.0),
                transport_modes=['Ship', 'Air'],
                recyclability_options=['Medium', 'High'],
                category='Sports',
                typical_origins=['China', 'Taiwan', 'Vietnam', 'USA'],
                lifespan_range=(1.0, 8.0),
                repairability_range=(2, 6),
                size_categories=['small', 'medium', 'large'],
                quality_levels=['standard', 'premium'],
                packaging_types=['box', 'bag'],
                volume_range=(0.1, 10.0)
            ),
            
            # Office Supplies (3,500 products)
            ProductTemplate(
                name_patterns=[
                    "BIC Cristal Pens", "Pilot G2 Gel Pens", "Sharpie Permanent Markers",
                    "Moleskine Classic Notebook", "Rhodia {model}", "Leuchtturm1917 {model}",
                    "Staples {model}", "3M Post-it Notes", "Scotch Tape",
                    "HP OfficeJet Pro Printer", "Canon PIXMA {model}", "Epson EcoTank",
                    "Logitech MX Master Mouse", "Dell Wireless Mouse", "Apple Magic Mouse"
                ],
                materials=['Plastic', 'Paper', 'Metal', 'Electronic', 'Ink'],
                weight_range=(0.01, 8.0),
                transport_modes=['Land', 'Ship'],
                recyclability_options=['Medium', 'High'],
                category='Office',
                typical_origins=['China', 'Japan', 'Germany', 'USA'],
                lifespan_range=(0.5, 8.0),
                repairability_range=(1, 5),
                size_categories=['small', 'medium'],
                quality_levels=['budget', 'standard', 'premium'],
                packaging_types=['box', 'blister', 'bag'],
                volume_range=(0.001, 5.0)
            ),
            
            # Automotive (3,500 products)
            ProductTemplate(
                name_patterns=[
                    "Bosch ICON Wiper Blades", "Rain-X {model}", "Michelin {model}",
                    "Armor All {model}", "Chemical Guys {model}", "Meguiar's {model}",
                    "Craftsman {model} Tool Set", "DEWALT {model}", "Black+Decker {model}",
                    "WeatherTech Floor Mats", "Husky Liners {model}", "Lloyd Mats {model}"
                ],
                materials=['Rubber', 'Metal', 'Plastic', 'Composite'],
                weight_range=(0.1, 5.0),
                transport_modes=['Land', 'Ship'],
                recyclability_options=['Medium', 'Low'],
                category='Automotive',
                typical_origins=['China', 'Mexico', 'USA', 'Germany'],
                lifespan_range=(1.0, 10.0),
                repairability_range=(3, 8),
                size_categories=['small', 'medium', 'large'],
                quality_levels=['budget', 'standard', 'premium'],
                packaging_types=['box', 'bag'],
                volume_range=(0.1, 8.0)
            )
        ]
    
    def _init_priority3_templates(self) -> List[ProductTemplate]:
        """Initialize templates for Priority 3: Less common but relevant items (15,000 products)"""
        return [
            # Specialized Electronics (5,000 products)
            ProductTemplate(
                name_patterns=[
                    "Canon EOS {model} DSLR", "Nikon D{model}", "Sony Alpha {model}",
                    "DJI Mavic {model} Drone", "GoPro HERO{num}", "Insta360 {model}",
                    "Focusrite Scarlett {model}", "Audio-Technica AT{model}", "Shure SM{model}",
                    "ASUS ROG {model} Gaming", "MSI Gaming {model}", "Razer {model}",
                    "Oculus Quest {num}", "HTC Vive {model}", "PlayStation VR"
                ],
                materials=['Electronic', 'Metal', 'Plastic', 'Glass'],
                weight_range=(0.3, 5.0),
                transport_modes=['Air', 'Ship'],
                recyclability_options=['Low', 'Medium'],
                category='Specialized Electronics',
                typical_origins=['Japan', 'Taiwan', 'China', 'Germany'],
                lifespan_range=(3.0, 10.0),
                repairability_range=(2, 7),
                size_categories=['medium', 'large'],
                quality_levels=['premium', 'professional'],
                packaging_types=['box'],
                volume_range=(0.5, 8.0)
            ),
            
            # Niche Clothing & Accessories (3,000 products)
            ProductTemplate(
                name_patterns=[
                    "Patagonia Better Sweater", "Arc'teryx {model}", "Canada Goose {model}",
                    "Rolex Submariner", "Omega Speedmaster", "Seiko {model}",
                    "Ray-Ban Aviator", "Oakley {model}", "Maui Jim {model}",
                    "Hermès {model} Bag", "Louis Vuitton {model}", "Gucci {model}"
                ],
                materials=['Leather', 'Metal', 'Textile', 'Glass', 'Composite'],
                weight_range=(0.05, 2.0),
                transport_modes=['Air', 'Ship'],
                recyclability_options=['Low', 'Medium'],
                category='Luxury Accessories',
                typical_origins=['Switzerland', 'Italy', 'France', 'Japan'],
                lifespan_range=(5.0, 25.0),
                repairability_range=(4, 9),
                size_categories=['small', 'medium'],
                quality_levels=['luxury', 'premium'],
                packaging_types=['box', 'pouch'],
                volume_range=(0.01, 1.0)
            ),
            
            # Hobby & Craft Supplies (3,500 products)
            ProductTemplate(
                name_patterns=[
                    "LEGO Creator {model}", "Playmobil {model}", "Hot Wheels {model}",
                    "Fender Player Stratocaster", "Gibson Les Paul", "Yamaha {model}",
                    "Prismacolor Premier Pencils", "Winsor & Newton {model}", "Sakura {model}",
                    "Brother XM{model} Sewing Machine", "Singer {model}", "Janome {model}"
                ],
                materials=['Plastic', 'Wood', 'Metal', 'Paper', 'Electronic'],
                weight_range=(0.05, 15.0),
                transport_modes=['Ship', 'Land'],
                recyclability_options=['Medium', 'High'],
                category='Hobby',
                typical_origins=['Denmark', 'China', 'Japan', 'Germany'],
                lifespan_range=(2.0, 20.0),
                repairability_range=(2, 8),
                size_categories=['small', 'medium', 'large'],
                quality_levels=['standard', 'premium', 'professional'],
                packaging_types=['box', 'bag'],
                volume_range=(0.1, 12.0)
            ),
            
            # Garden & Outdoor Tools (3,500 products)
            ProductTemplate(
                name_patterns=[
                    "Black+Decker {model} Trimmer", "WORX {model}", "Greenworks {model}",
                    "Fiskars Pruning Shears", "Corona {model}", "Felco {model}",
                    "Weber Genesis {model} Grill", "Traeger {model}", "Big Green Egg {model}",
                    "Coleman {model} Tent", "REI Co-op {model}", "Kelty {model}"
                ],
                materials=['Metal', 'Plastic', 'Wood', 'Textile', 'Composite'],
                weight_range=(0.2, 50.0),
                transport_modes=['Land', 'Ship'],
                recyclability_options=['Medium', 'High'],
                category='Garden & Outdoor',
                typical_origins=['USA', 'China', 'Germany', 'Finland'],
                lifespan_range=(3.0, 15.0),
                repairability_range=(4, 9),
                size_categories=['medium', 'large', 'extra_large'],
                quality_levels=['standard', 'premium', 'professional'],
                packaging_types=['box'],
                volume_range=(1.0, 100.0)
            )
        ]
    
    def calculate_eco_score(self, material: str, transport: str, recyclability: str, 
                           weight: float, distance: float = 8000) -> Tuple[str, float]:
        """Calculate eco score and CO2 emissions based on material, transport, and recyclability"""
        
        # Base material CO2 intensity (kg CO2 per kg product)
        material_co2 = self.co2_intensities.get(material, 3.0)
        
        # Transport CO2 (kg CO2 per kg per km)
        transport_co2 = self.transport_co2.get(transport, 0.1)
        
        # Calculate total CO2 emissions
        material_emissions = weight * material_co2
        transport_emissions = weight * distance * transport_co2
        total_co2 = material_emissions + transport_emissions
        
        # Recyclability modifier
        recyclability_modifier = {'High': 0.8, 'Medium': 1.0, 'Low': 1.3}.get(recyclability, 1.0)
        adjusted_co2 = total_co2 * recyclability_modifier
        
        # Convert to eco score (A-G scale based on CO2 emissions)
        if adjusted_co2 < 0.5:
            eco_score = 'A'
        elif adjusted_co2 < 1.0:
            eco_score = 'B'
        elif adjusted_co2 < 2.0:
            eco_score = 'C'
        elif adjusted_co2 < 4.0:
            eco_score = 'D'
        elif adjusted_co2 < 8.0:
            eco_score = 'E'
        elif adjusted_co2 < 15.0:
            eco_score = 'F'
        else:
            eco_score = 'G'
            
        return eco_score, round(adjusted_co2, 2)
    
    def generate_product_name(self, template: ProductTemplate) -> str:
        """Generate a realistic product name from template patterns"""
        pattern = random.choice(template.name_patterns)
        
        # Replace placeholders with realistic values
        replacements = {
            '{model}': random.choice(['Pro', 'Max', 'Plus', 'Ultra', 'Elite', 'Classic', 'Essential', 
                                    'Premium', 'Standard', 'Basic', 'Advanced', 'Sport', 'Comfort']),
            '{num}': str(random.randint(1, 20)),
            '{storage}': str(random.choice([64, 128, 256, 512, 1024])),
            '{inch}': str(random.choice([13, 14, 15, 16, 17])),
            '{capacity}': str(random.choice([5000, 10000, 15000, 20000, 25000]))
        }
        
        for placeholder, value in replacements.items():
            pattern = pattern.replace(placeholder, value)
            
        return pattern
    
    def get_random_brand_origin(self) -> Tuple[str, str]:
        """Get a random brand and its origin country"""
        brand = random.choice(list(self.brand_locations.keys()))
        origin = self.brand_locations[brand]
        return brand, origin
    
    def generate_product(self, template: ProductTemplate) -> Dict[str, Any]:
        """Generate a single product based on template"""
        
        # Generate product name
        title = self.generate_product_name(template)
        
        # Add brand to title if not already present
        brand, origin = self.get_random_brand_origin()
        if not any(b.lower() in title.lower() for b in self.brand_locations.keys()):
            title = f"{brand} {title}"
        
        # Select attributes
        material = random.choice(template.materials)
        weight = round(random.uniform(*template.weight_range), 2)
        transport = random.choice(template.transport_modes)
        recyclability = random.choice(template.recyclability_options)
        
        # Use template origins or brand origin
        if random.random() < 0.7:  # 70% chance to use template origin
            origin = random.choice(template.typical_origins)
        
        # Calculate eco score and emissions
        eco_score, co2_emissions = self.calculate_eco_score(material, transport, recyclability, weight)
        
        # Generate enhanced features
        secondary_materials = []
        if random.random() < 0.3:  # 30% chance of secondary materials
            available_materials = [m for m in template.materials if m != material]
            if available_materials:
                secondary_materials = [random.choice(available_materials)]
        
        packaging_type = random.choice(template.packaging_types)
        packaging_materials = ['Cardboard', 'Plastic']
        if packaging_type in ['bottle', 'tube']:
            packaging_materials = ['Plastic', 'Glass']
        
        # Generate other attributes
        material_confidence = round(random.uniform(0.6, 0.95), 2)
        packaging_weight_ratio = round(random.uniform(0.05, 0.25), 2)
        origin_confidence = round(random.uniform(0.7, 0.95), 2)
        estimated_lifespan = round(random.uniform(*template.lifespan_range), 1)
        repairability_score = random.randint(*template.repairability_range)
        size_category = random.choice(template.size_categories)
        quality_level = random.choice(template.quality_levels)
        
        # Boolean attributes
        is_eco_labeled = random.random() < 0.15  # 15% chance
        is_amazon_choice = random.random() < 0.08  # 8% chance
        
        pack_size = random.choice([1, 1, 1, 1, 2, 3, 4, 6, 12])  # Weighted towards single items
        estimated_volume = round(random.uniform(*template.volume_range), 2)
        weight_confidence = round(random.uniform(0.5, 0.9), 2)
        
        return {
            'title': title,
            'material': material,
            'weight': weight,
            'transport': transport,
            'recyclability': recyclability,
            'true_eco_score': eco_score,
            'co2_emissions': co2_emissions,
            'origin': origin,
            'material_confidence': material_confidence,
            'secondary_materials': str(secondary_materials),
            'packaging_type': packaging_type,
            'packaging_materials': str(packaging_materials),
            'packaging_weight_ratio': packaging_weight_ratio,
            'inferred_category': template.category.lower().replace(' ', '_'),
            'origin_confidence': origin_confidence,
            'estimated_lifespan_years': estimated_lifespan,
            'repairability_score': repairability_score,
            'size_category': size_category,
            'quality_level': quality_level,
            'is_eco_labeled': is_eco_labeled,
            'is_amazon_choice': is_amazon_choice,
            'pack_size': pack_size,
            'estimated_volume_l': estimated_volume,
            'weight_confidence': weight_confidence
        }
    
    def generate_dataset(self) -> List[Dict[str, Any]]:
        """Generate the complete dataset of 50,000 products"""
        
        products = []
        
        print("Generating Priority 1 products (common everyday items)...")
        # Priority 1: 20,000 products (5,000 per template)
        for template in self.priority1_templates:
            products_per_template = 20000 // len(self.priority1_templates)
            for _ in range(products_per_template):
                products.append(self.generate_product(template))
        
        print("Generating Priority 2 products (mid-tier common items)...")
        # Priority 2: 15,000 products
        for template in self.priority2_templates:
            products_per_template = 15000 // len(self.priority2_templates)
            for _ in range(products_per_template):
                products.append(self.generate_product(template))
        
        print("Generating Priority 3 products (less common items)...")
        # Priority 3: 15,000 products
        for template in self.priority3_templates:
            products_per_template = 15000 // len(self.priority3_templates)
            for _ in range(products_per_template):
                products.append(self.generate_product(template))
        
        # Shuffle to mix priorities
        random.shuffle(products)
        
        return products
    
    def save_dataset(self, products: List[Dict[str, Any]], filename: str = 'enhanced_eco_dataset.csv'):
        """Save the dataset to CSV file"""
        
        # Define column order to match the specified structure
        columns = [
            'title', 'material', 'weight', 'transport', 'recyclability', 'true_eco_score',
            'co2_emissions', 'origin', 'material_confidence', 'secondary_materials',
            'packaging_type', 'packaging_materials', 'packaging_weight_ratio',
            'inferred_category', 'origin_confidence', 'estimated_lifespan_years',
            'repairability_score', 'size_category', 'quality_level', 'is_eco_labeled',
            'is_amazon_choice', 'pack_size', 'estimated_volume_l', 'weight_confidence'
        ]
        
        output_path = Path('/Users/jamie/Documents/University/dsp_eco_tracker/common/data/csv') / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            writer.writerows(products)
        
        print(f"Dataset saved to: {output_path}")
        print(f"Total products generated: {len(products)}")
        
        # Print some statistics
        categories = {}
        eco_scores = {}
        materials = {}
        
        for product in products:
            category = product['inferred_category']
            categories[category] = categories.get(category, 0) + 1
            
            eco_score = product['true_eco_score']
            eco_scores[eco_score] = eco_scores.get(eco_score, 0) + 1
            
            material = product['material']
            materials[material] = materials.get(material, 0) + 1
        
        print("\nDataset Statistics:")
        print(f"Categories: {dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))}")
        print(f"Eco Scores: {dict(sorted(eco_scores.items()))}")
        print(f"Top Materials: {dict(sorted(materials.items(), key=lambda x: x[1], reverse=True)[:10])}")

def main():
    """Main execution function"""
    print("=== Enhanced Eco Dataset Generator ===")
    print("Generating 50,000 realistic products prioritized by commonality...")
    print()
    
    generator = EnhancedDatasetGenerator()
    products = generator.generate_dataset()
    generator.save_dataset(products)
    
    print("\n=== Generation Complete ===")
    print("Dataset ready for ML training and analysis!")

if __name__ == "__main__":
    main()