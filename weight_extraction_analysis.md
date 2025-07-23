# Weight Extraction Issue Analysis & Solution

## Problem Summary
For the protein powder URL:
```
https://www.amazon.co.uk/Isolate-Protein-Fast-digesting-hydrolysate-Gourmet/dp/B01H3O2AMG/...
```

**Current Results:**
- Title: "MUTANT ISO Surge | Whey Isolate Protein Powder | 25g Protein, Fast-digesting whey Protein Isolate &"
- Weight: 0.025kg (WRONG - extracts "25g Protein" as container weight)
- Emissions: 0 kg CO₂ (because weight is too low)

**Expected Results:**
- Container weight should be ~2.5kg (typical protein powder container)
- Should calculate meaningful emissions based on actual product weight

## Root Cause Analysis

### 1. Title Truncation Issue
- The title is truncated and ends with "&" 
- Missing the actual container weight information
- Full title likely contains weight like "2.5kg" or "5lb"

### 2. Incorrect Weight Pattern Matching
- Current regex captures "25g Protein" (protein content per serving)
- This is nutritional information, NOT container weight
- Pattern `(\d+(?:\.\d+)?)\s*g\b(?!gram)` matches "25g" incorrectly

### 3. Missing Product Specifications Access
- Current scrapers don't access Amazon's "Technical Details" or "Product Information" sections
- These sections contain the actual container weight
- Weight extraction relies only on title text

### 4. Insufficient Protein Powder Handling
- No category-specific weight estimation
- No fallback for protein powder products when extraction fails

## Current Scraper Flow Analysis

### Enhanced Scraper (`enhanced_scraper_fix.py`)
1. ✅ Uses multiple strategies (direct, search, mobile)
2. ❌ `extract_weight_enhanced()` incorrectly captures "25g" from protein content
3. ❌ Only looks at title, not product specifications
4. ❌ No category-specific fallbacks

### Requests Scraper (`requests_scraper.py`)
1. ✅ Has protein powder detection logic
2. ✅ Uses fallback weight of 2.5kg for protein powder
3. ❌ Still has same regex issue capturing "25g Protein"
4. ⚠️ Enhanced patterns exist but getting overridden

### Main App (`app.py`)
1. ✅ Uses enhanced scraper first, then fallback
2. ✅ Has `extract_weight_from_title()` function with good patterns
3. ❌ Gets wrong data from scraper before enhancement
4. ❌ Enhancement only runs if weight <= 0.1kg (25g = 0.025kg triggers this)

## The 0.03kg Mystery
Looking at the user's report of 0.03kg, this suggests:
- Enhanced scraper returns 0.025kg (25g)
- App enhancement adds some default/minimum value
- Result: 0.03kg (close to 0.025kg + small buffer)

## Solution Implementation

### Fix 1: Improve Weight Pattern Matching
```python
def extract_weight_from_title_fixed(title: str) -> float:
    """Enhanced weight extraction that ignores nutritional content"""
    if not title:
        return 0.0
    
    title_lower = title.lower()
    
    # EXCLUDE nutritional content patterns first
    nutritional_exclusions = [
        r'\d+\s*g\s*protein',
        r'\d+\s*g\s*carb',
        r'\d+\s*g\s*fat',
        r'\d+\s*mg\s*sodium',
        r'\d+\s*cal',
        r'\d+\s*kcal',
    ]
    
    # Remove nutritional info to avoid false matches
    cleaned_title = title_lower
    for exclusion in nutritional_exclusions:
        cleaned_title = re.sub(exclusion, '', cleaned_title)
    
    # Look for container weight patterns
    container_weight_patterns = [
        r'(\d+(?:\.\d+)?)\s*kg\b',          # 2.5kg
        r'(\d+(?:\.\d+)?)\s*lb[s]?\b',      # 5lb, 5lbs  
        r'(\d+(?:\.\d+)?)\s*pound[s]?\b',   # 5 pounds
        # Only capture grams for reasonable container sizes
        r'(\d+(?:\.\d+)?)\s*g\b(?=.*(?:container|tub|jar|bottle))', # 1000g container
        r'(\d{3,4})\s*g\b',  # 500g, 1000g, 2500g (3-4 digit grams likely container)
    ]
    
    for pattern in container_weight_patterns:
        matches = re.findall(pattern, cleaned_title)
        if matches:
            try:
                weight_val = float(matches[0])
                
                if 'kg' in pattern:
                    weight_kg = weight_val
                elif 'lb' in pattern or 'pound' in pattern:
                    weight_kg = weight_val * 0.453592
                elif 'g' in pattern:
                    # Only convert if reasonable container size
                    if weight_val >= 200:  # At least 200g
                        weight_kg = weight_val / 1000
                    else:
                        continue
                
                # Sanity check
                if 0.1 <= weight_kg <= 50:
                    return weight_kg
            except ValueError:
                continue
    
    return 0.0
```

### Fix 2: Category-Specific Weight Estimation
```python
def get_category_fallback_weight(title: str, brand: str) -> float:
    """Category-specific weight estimation when extraction fails"""
    title_lower = title.lower()
    
    # Protein powder category
    if any(keyword in title_lower for keyword in ['protein', 'whey', 'casein', 'mass gainer']):
        # Estimate based on common protein powder sizes
        if any(size in title_lower for size in ['small', 'trial', 'sample']):
            return 0.9  # ~900g
        elif any(size in title_lower for size in ['large', 'bulk', '10lb', '5kg']):
            return 4.5  # ~4.5kg
        else:
            return 2.3  # ~2.3kg (typical 5lb container)
    
    # Electronics
    elif any(keyword in title_lower for keyword in ['phone', 'tablet', 'laptop']):
        return 0.8
    
    # Books
    elif 'book' in title_lower:
        return 0.4
    
    # Default
    return 1.0
```

### Fix 3: Access Product Specifications
The scrapers need to access Amazon's technical details section:

```python
def extract_weight_from_tech_specs(soup) -> float:
    """Extract weight from Amazon's technical details/specifications"""
    
    # Look for technical details table
    tech_sections = [
        '.a-section table tr',
        '.prodDetTable tr', 
        '#productDetails_techSpec_section_1 tr',
        '#productDetails_detailBullets_sections1 tr'
    ]
    
    for section_selector in tech_sections:
        rows = soup.select(section_selector)
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                label = cells[0].get_text().strip().lower()
                value = cells[1].get_text().strip().lower()
                
                if any(weight_term in label for weight_term in ['weight', 'item weight', 'package weight']):
                    # Extract weight from value
                    weight = extract_weight_from_text(value)
                    if weight > 0:
                        return weight
    
    return 0.0
```

## Immediate Fix Implementation

The quickest fix is to modify the weight extraction logic in the main app to:

1. **Detect and skip nutritional content**: Don't extract "25g Protein" as weight
2. **Use category fallback**: For protein powder, use 2.3kg when extraction fails  
3. **Enhanced pattern matching**: Look for container-specific weight patterns

## Testing the Fix

Test with the failing URL should show:
- Title: Full title (fix truncation)
- Weight: ~2.3kg (fallback) or actual container weight if found
- Emissions: Meaningful CO₂ calculation based on proper weight

## Files to Modify

1. `enhanced_scraper_fix.py` - Fix weight extraction patterns
2. `app.py` - Improve `extract_weight_from_title()` function  
3. `requests_scraper.py` - Ensure protein powder fallback works
4. Add product specifications parsing to all scrapers