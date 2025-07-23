# 🌍 Dual Origin System Implementation

## Overview

The DSP Eco Tracker now features a **dual origin system** that separates geographic location (for distance calculations) from detailed manufacturing information (for transparency).

## System Components

### 1. **Country of Origin** 🗺️
- **Purpose**: Accurate distance calculations via pgeocode
- **Validation**: Strict - only real country names accepted
- **Sources**: 
  - Brand database mapping (most reliable)
  - Text extraction with country validation
- **Examples**: `"UK"`, `"South Africa"`, `"Germany"`

### 2. **Facility Origin** 🏭
- **Purpose**: Detailed manufacturing transparency
- **Validation**: Permissive - captures facility details
- **Sources**: 
  - Text extraction from product descriptions
  - Manufacturing facility mentions
- **Examples**: `"A Facility"`, `"GMP Certified Facility"`, `"Birmingham Plant"`

## Implementation Details

### Backend Changes

#### Enhanced Scraper (`enhanced_scraper_fix.py`)
```python
def extract_dual_origin_enhanced(self, soup):
    """Returns (country_of_origin, facility_origin)"""
    
    # Strategy 1: Brand-based country mapping
    brand_origins = {
        'sci-mx': 'UK',
        'usn': 'South Africa',
        'optimum nutrition': 'USA',
        # ... more brands
    }
    
    # Strategy 2: Text extraction with different validation levels
    country_patterns = [  # Strict validation
        r'country\s+of\s+origin[:\s]*([A-Z][a-zA-Z\s]{2,25}?)',
        r'(?:made|manufactured)\s+in\s+([A-Z][a-zA-Z\s]{2,25}?)'
    ]
    
    facility_patterns = [  # Permissive validation  
        r'(?:facility|factory|plant)[:\s]*([A-Z][a-zA-Z\s\-]{2,40}?)',
        r'origin[:\s]*([A-Z][a-zA-Z\s\-]{2,40}?)'
    ]
```

#### API Response (`backend/api/app.py`)
```python
"attributes": {
    "origin": origin_country,              # Legacy compatibility
    "country_of_origin": origin_country,   # For distance calculation
    "facility_origin": facility_origin,    # For detailed transparency
    "distance_from_origin_km": 118.8,      # Based on country_of_origin
    # ... other attributes
}
```

### Frontend Changes

#### ProductImpactCard Display
```jsx
<div className="p-3 glass-card rounded-lg">
  <div className="flex justify-between items-center mb-2">
    <span className="text-slate-400">Country of Origin:</span>
    <ModernBadge variant="default" size="sm">
      {attr.country_of_origin || attr.origin}
    </ModernBadge>
  </div>
  {attr.facility_origin && attr.facility_origin !== "Unknown" && (
    <div className="pt-2 border-t border-slate-700">
      <div className="flex justify-between items-center">
        <span className="text-xs text-slate-500">Manufacturing Facility:</span>
        <span className="text-xs text-slate-300 font-medium">
          {attr.facility_origin}
        </span>
      </div>
    </div>
  )}
</div>
```

## Problem Solved

### Before: Single Origin Issues
- ❌ "A Facility" used for distance calculation → 3.2km fallback
- ❌ Loss of manufacturing transparency  
- ❌ Inaccurate carbon footprint calculations

### After: Dual Origin Benefits
- ✅ **UK** used for distance → 118.8km accurate calculation
- ✅ **A Facility** preserved for manufacturing transparency
- ✅ Accurate carbon footprint based on real geography
- ✅ Better user information with detailed origin data

## Use Cases

### 1. **SCI-MX Product Example**
```
Country of Origin: UK                    → Distance calculation: 118.8km
Manufacturing Facility: A Facility      → User transparency
Transport Mode: Truck                    → Based on UK distance
Carbon Emissions: 0.03 kg CO₂          → Low domestic footprint
```

### 2. **USN Product Example**  
```
Country of Origin: South Africa          → Distance calculation: 9,069km
Manufacturing Facility: [None detected] → No specific facility info
Transport Mode: Air                      → Based on SA distance  
Carbon Emissions: 2.27 kg CO₂          → High international footprint
```

### 3. **Future Enhanced Example**
```
Country of Origin: Germany               → Distance calculation: 1,200km
Manufacturing Facility: Munich GMP Lab  → Detailed facility info
Transport Mode: Ship                     → Based on European distance
Carbon Emissions: 0.85 kg CO₂          → Moderate European footprint
```

## Technical Benefits

### 1. **Accuracy** 🎯
- **Distance calculations** use validated country names only
- **pgeocode integration** works with proper geographic data
- **Transport mode selection** based on real distances

### 2. **Transparency** 🔍  
- **Manufacturing details** preserved for user information
- **Facility information** shown when available
- **Supply chain visibility** enhanced

### 3. **Flexibility** 🔧
- **Backward compatibility** maintained (`origin` field still works)
- **Progressive enhancement** - shows facility when detected
- **Scalable system** - easy to add more origin types

## Testing Results

### API Response Structure
```json
{
  "data": {
    "attributes": {
      "origin": "England",
      "country_of_origin": "England", 
      "facility_origin": "A Facility",
      "distance_from_origin_km": 118.8,
      "transport_mode": "Truck",
      "carbon_kg": 0.03
    }
  }
}
```

### Frontend Display
```
Product Specifications
┌─────────────────────────────────┐
│ Country of Origin: [UK]         │
│ ─────────────────────────────── │
│ Manufacturing Facility:         │ 
│ A Facility                      │
└─────────────────────────────────┘
```

## Impact on Eco Score

The dual origin system significantly improves the accuracy of environmental impact assessments:

- **Domestic products** (UK): Low emissions, better eco scores
- **European products**: Moderate emissions, realistic scores  
- **International products**: High emissions, appropriate penalties
- **Facility transparency**: Users can make informed choices

This implementation represents a major improvement in both **accuracy** and **transparency** for the DSP Eco Tracker system!