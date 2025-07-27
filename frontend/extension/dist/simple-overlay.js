// Simple, reliable persistent overlay - no complex messaging
(function() {
  'use strict';
  
  let overlayVisible = false;
  
  // Listen for extension icon clicks
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'TOGGLE_OVERLAY') {
      toggleOverlay();
      sendResponse({ success: true });
    }
  });
  
  function toggleOverlay() {
    if (overlayVisible) {
      hideOverlay();
    } else {
      showOverlay();
    }
  }
  
  function showOverlay() {
    if (document.getElementById('eco-overlay')) {
      return;
    }
    
    overlayVisible = true;
    
    const overlay = document.createElement('div');
    overlay.id = 'eco-overlay';
    overlay.style.cssText = `
      position: fixed !important;
      top: 20px !important;
      right: 20px !important;
      width: 380px !important;
      max-height: calc(100vh - 40px) !important;
      z-index: 999999 !important;
      background: linear-gradient(135deg, rgba(15, 15, 35, 0.95), rgba(26, 26, 46, 0.95)) !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      border-radius: 16px !important;
      color: white !important;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
      font-size: 14px !important;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5) !important;
      overflow: hidden !important;
      display: flex !important;
      flex-direction: column !important;
    `;
    
    overlay.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: rgba(255, 255, 255, 0.05); border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
        <h3 style="margin: 0; font-size: 16px; font-weight: 600; background: linear-gradient(135deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🌱 Eco Calculator</h3>
        <button onclick="this.closest('#eco-overlay').remove(); window.ecoOverlayVisible = false;" style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #ef4444; width: 32px; height: 32px; border-radius: 8px; font-size: 18px; cursor: pointer;">×</button>
      </div>
      
      <div style="flex: 1; overflow-y: auto; padding: 20px; max-height: calc(100vh - 120px);">
        <form id="ecoForm" style="margin-bottom: 20px;">
          <div style="margin-bottom: 16px;">
            <input 
              type="text" 
              id="ecoUrl" 
              value="${window.location.href}"
              placeholder="Amazon product URL" 
              style="width: 100%; padding: 14px 16px; border: 2px solid rgba(255, 255, 255, 0.1); border-radius: 12px; background: rgba(255, 255, 255, 0.05); color: white; font-size: 14px; box-sizing: border-box;"
              required
            />
          </div>
          <div style="margin-bottom: 16px;">
            <input 
              type="text" 
              id="ecoPostcode" 
              placeholder="Enter your postcode (e.g., SW1A 1AA)" 
              style="width: 100%; padding: 14px 16px; border: 2px solid rgba(255, 255, 255, 0.1); border-radius: 12px; background: rgba(255, 255, 255, 0.05); color: white; font-size: 14px; box-sizing: border-box;"
            />
          </div>
          <button type="submit" style="width: 100%; padding: 16px 24px; border: none; border-radius: 12px; font-size: 14px; font-weight: 600; cursor: pointer; background: linear-gradient(135deg, #00d4ff, #7c3aed); color: white; box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);">
            Calculate Emissions
          </button>
        </form>
        
        <div id="ecoResults"></div>
      </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Prevent scroll events from bubbling to the page
    overlay.addEventListener('wheel', (e) => {
      e.stopPropagation();
    });
    
    // Prevent touch scroll events from bubbling to the page
    overlay.addEventListener('touchmove', (e) => {
      e.stopPropagation();
    });
    
    // Form handler
    document.getElementById('ecoForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const url = document.getElementById('ecoUrl').value.trim();
      const postcode = document.getElementById('ecoPostcode').value.trim() || 'SW1A 1AA';
      const results = document.getElementById('ecoResults');
      
      if (!url) return;
      
      results.innerHTML = '<div style="text-align: center; padding: 20px; color: #a1a1aa;">Analyzing product...</div>';
      
      try {
        // Use background script to make API call (avoids CORS)
        const response = await chrome.runtime.sendMessage({
          type: 'FETCH_EMISSIONS',
          url: url,
          postcode: postcode
        });
        
        if (response.success && response.data?.data) {
          displayResults(response.data);
        } else {
          throw new Error(response.error || 'No data received');
        }
        
      } catch (error) {
        console.error('Error:', error);
        results.innerHTML = `
          <div style="text-align: center; padding: 20px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; color: #ef4444;">
            Unable to analyze product. Please check the URL and try again.
          </div>
        `;
      }
    });
  }
  
  function hideOverlay() {
    const overlay = document.getElementById('eco-overlay');
    if (overlay) {
      overlay.remove();
    }
    overlayVisible = false;
  }
  
  function displayResults(response) {
    const data = response.data;
    const attributes = data.attributes || {};
    const productTitle = response.title || data.title || 'Product';
    
    const mlScore = attributes.eco_score_ml || 'N/A';
    const ruleScore = attributes.eco_score_rule_based || 'N/A';
    const carbonKg = attributes.carbon_kg || 'N/A';
    const materialType = attributes.material_type || 'Unknown';
    const transportMode = attributes.transport_mode || 'N/A';
    const origin = attributes.origin || attributes.country_of_origin || 'Unknown';
    const weightKg = attributes.weight_kg || 'N/A';
    const recyclability = attributes.recyclability || 'Assessment pending';
    const mlConfidence = attributes.eco_score_ml_confidence || 0;
    const ruleConfidence = attributes.eco_score_rule_based_confidence || 0;
    const distanceOrigin = attributes.distance_from_origin_km || 0;
    const distanceUK = attributes.distance_from_uk_hub_km || 0;
    
    // Extract materials data
    const materials = attributes.materials || {};
    const primaryMaterial = materials.primary_material || materialType || 'Unknown';
    const allMaterials = materials.all_materials || [];
    const secondaryMaterials = allMaterials.filter(m => m.name !== primaryMaterial);
    
    // If we have detailed materials data, use it; otherwise fall back to simple material_type
    const showDetailedMaterials = primaryMaterial && primaryMaterial !== 'Mixed' && primaryMaterial !== 'Unknown';
    const displayMaterial = showDetailedMaterials ? primaryMaterial : materialType;
    
    // Calculate trees
    const trees = carbonKg !== 'N/A' ? Math.max(1, Math.round(parseFloat(carbonKg) / 21.77)) : 0;
    
    // Get emojis
    const getEmoji = (score) => {
      const emojis = { 'A+': '🌍', 'A': '🌿', 'B': '🍃', 'C': '🌱', 'D': '⚠️', 'E': '❌', 'F': '💀' };
      return emojis[score] || '';
    };
    
    const getTransportEmoji = (mode) => {
      if (!mode) return '';
      const m = mode.toLowerCase();
      if (m === 'air') return '✈️';
      if (m === 'ship') return '🚢';
      if (m === 'truck') return '🚚';
      return '';
    };
    
    document.getElementById('ecoResults').innerHTML = `
      <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; margin-top: 16px;">
        
        <!-- Product Title -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; gap: 12px;">
          <div style="font-size: 14px; font-weight: 600; color: white; line-height: 1.3; flex: 1;">
            📦 ${productTitle}
          </div>
          <button onclick="document.getElementById('ecoUrl').value = '${window.location.href}'; document.getElementById('ecoResults').innerHTML = '';" style="background: linear-gradient(135deg, #7c3aed, #00d4ff); color: white; border: none; border-radius: 8px; padding: 8px 12px; font-size: 12px; cursor: pointer;">
            🔄 New
          </button>
        </div>
        
        <!-- Prediction Methods -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
          <div style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 12px; padding: 16px;">
            <div style="display: flex; align-items: center; margin-bottom: 12px; gap: 12px;">
              <span style="font-size: 20px;">🧠</span>
              <div>
                <div style="font-size: 13px; font-weight: 600; color: white; margin-bottom: 2px;">ML Prediction</div>
                <div style="font-size: 10px; color: #a1a1aa;">Enhanced XGBoost</div>
              </div>
            </div>
            <div style="text-align: center;">
              <div style="font-size: 20px; font-weight: 700; color: #00d4ff; margin-bottom: 4px;">${getEmoji(mlScore)} ${mlScore}</div>
              <div style="font-size: 11px; color: #10b981;">Confidence: ${mlConfidence.toFixed(0)}%</div>
            </div>
          </div>
          
          <div style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 12px; padding: 16px;">
            <div style="display: flex; align-items: center; margin-bottom: 12px; gap: 12px;">
              <span style="font-size: 20px;">📊</span>
              <div>
                <div style="font-size: 13px; font-weight: 600; color: white; margin-bottom: 2px;">Standard Method</div>
                <div style="font-size: 10px; color: #a1a1aa;">Traditional calculation</div>
              </div>
            </div>
            <div style="text-align: center;">
              <div style="font-size: 20px; font-weight: 700; color: #00d4ff; margin-bottom: 4px;">${getEmoji(ruleScore)} ${ruleScore}</div>
              <div style="font-size: 11px; color: #10b981;">Confidence: ${ruleConfidence.toFixed(0)}%</div>
            </div>
          </div>
        </div>
        
        <!-- Specifications -->
        <div style="margin: 20px 0;">
          <h4 style="margin: 0 0 12px 0; font-size: 14px; color: white; border-bottom: 2px solid rgba(0, 212, 255, 0.3); padding-bottom: 6px;">📋 Product Specifications</h4>
          <div style="display: grid; gap: 8px;">
            <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
              <span style="color: #a1a1aa; font-size: 12px;">Weight:</span>
              <span style="color: white; font-size: 12px; font-weight: 600;">${weightKg} kg</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
              <span style="color: #a1a1aa; font-size: 12px;">Origin:</span>
              <span style="color: white; font-size: 12px; font-weight: 600;">${origin}</span>
            </div>
            ${showDetailedMaterials ? `
            <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
              <span style="color: #a1a1aa; font-size: 12px;">Primary Material:</span>
              <span style="color: white; font-size: 12px; font-weight: 600;">${primaryMaterial}</span>
            </div>
            ${secondaryMaterials.length > 0 ? `
            <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
              <span style="color: #a1a1aa; font-size: 12px;">Secondary Materials:</span>
              <span style="color: white; font-size: 12px; font-weight: 600;">${secondaryMaterials.map(m => 
                m.weight ? `${m.name} (${(m.weight * 100).toFixed(0)}%)` : m.name
              ).join(', ')}</span>
            </div>` : ''}` : `
            <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
              <span style="color: #a1a1aa; font-size: 12px;">Material:</span>
              <span style="color: white; font-size: 12px; font-weight: 600;">${displayMaterial}</span>
            </div>`}
            <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
              <span style="color: #a1a1aa; font-size: 12px;">Transport:</span>
              <span style="color: white; font-size: 12px; font-weight: 600;">${transportMode} ${getTransportEmoji(transportMode)}</span>
            </div>
          </div>
        </div>
        
        <!-- Environmental Impact -->
        <div style="margin: 20px 0;">
          <h4 style="margin: 0 0 12px 0; font-size: 14px; color: white; border-bottom: 2px solid rgba(0, 212, 255, 0.3); padding-bottom: 6px;">🌍 Environmental Impact</h4>
          <div style="display: flex; gap: 16px; align-items: flex-start;">
            <div style="text-align: center; background: rgba(0, 212, 255, 0.1); border: 2px solid rgba(0, 212, 255, 0.3); border-radius: 12px; padding: 16px; min-width: 100px;">
              <div style="font-size: 28px; font-weight: 800; color: #00d4ff; margin-bottom: 8px;">${mlScore} ${getEmoji(mlScore)}</div>
              <div style="font-size: 12px; color: white; margin-bottom: 4px;">Eco Score</div>
              <div style="font-size: 10px; color: #10b981;">${mlConfidence.toFixed(1)}% confidence</div>
            </div>
            <div style="flex: 1; display: grid; gap: 8px;">
              <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                <span style="color: #a1a1aa; font-size: 12px;">Carbon Emissions:</span>
                <span style="background: linear-gradient(135deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 13px; font-weight: 700;">${carbonKg} kg CO₂</span>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                <span style="color: #a1a1aa; font-size: 12px;">🌳 Trees to Offset:</span>
                <span style="color: white; font-size: 12px; font-weight: 600;">${trees} tree${trees !== 1 ? 's' : ''}</span>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                <span style="color: #a1a1aa; font-size: 12px;">International Distance:</span>
                <span style="color: white; font-size: 12px; font-weight: 600;">${distanceOrigin.toFixed(1)} km</span>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span style="color: #a1a1aa; font-size: 12px;">UK Hub Distance:</span>
                <span style="color: white; font-size: 12px; font-weight: 600;">${distanceUK.toFixed(1)} km</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- CO2 Equivalence Comparisons -->
        ${getCO2Equivalences(carbonKg)}
      </div>
    `;
  }
  
  function getCO2Equivalences(carbonKg) {
    if (!carbonKg || carbonKg === 'N/A' || isNaN(parseFloat(carbonKg))) {
      return '';
    }
    
    const co2 = parseFloat(carbonKg);
    
    // CO2 equivalence calculations
    // Car: Average car emits 0.12 kg CO2 per km
    const carKm = (co2 / 0.12).toFixed(1);
    
    // Kettle: 1 litre boil = ~0.15 kg CO2 (3kW for 3 mins)
    const kettleBoils = Math.round(co2 / 0.15);
    
    // House lights: LED bulb 10W for 1 hour = ~0.005 kg CO2
    const lightHours = Math.round(co2 / 0.005);
    
    // Electricity cost: UK average 28p per kWh, 1 kWh = ~0.23 kg CO2
    const kWhEquivalent = co2 / 0.23;
    const electricityCost = (kWhEquivalent * 0.28).toFixed(2);
    
    return `
      <div style="margin: 20px 0;">
        <h4 style="margin: 0 0 12px 0; font-size: 14px; color: white; border-bottom: 2px solid rgba(0, 212, 255, 0.3); padding-bottom: 6px;">🔄 CO₂ Equivalences</h4>
        <div style="display: grid; gap: 8px;">
          <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
            <span style="color: #a1a1aa; font-size: 12px;">🚗 Car driving distance:</span>
            <span style="color: white; font-size: 12px; font-weight: 600;">${carKm} km</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
            <span style="color: #a1a1aa; font-size: 12px;">☕ Kettle boiling (1L):</span>
            <span style="color: white; font-size: 12px; font-weight: 600;">${kettleBoils} times</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
            <span style="color: #a1a1aa; font-size: 12px;">💡 House lights (LED):</span>
            <span style="color: white; font-size: 12px; font-weight: 600;">${lightHours} hours</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
            <span style="color: #a1a1aa; font-size: 12px;">⚡ Electricity cost:</span>
            <span style="color: white; font-size: 12px; font-weight: 600;">£${electricityCost}</span>
          </div>
        </div>
      </div>
    `;
  }
  
  // Expose globally for cleanup
  window.ecoOverlayVisible = overlayVisible;
})();