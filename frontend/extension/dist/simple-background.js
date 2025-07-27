// Simple background script - handles API calls to avoid CORS
chrome.action.onClicked.addListener((tab) => {
  // Only work on Amazon pages
  if (tab.url && (tab.url.includes('amazon.co.uk') || tab.url.includes('amazon.com'))) {
    // Send simple message to toggle overlay
    chrome.tabs.sendMessage(tab.id, { type: 'TOGGLE_OVERLAY' }).catch(() => {
      // If content script not loaded, inject it
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['simple-overlay.js']
      });
    });
  } else {
    // Show notification for non-Amazon pages
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: 'Eco Tracker',
      message: 'Please visit an Amazon product page to use the Eco Tracker.'
    });
  }
});

// Handle API requests from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'FETCH_EMISSIONS') {
    // Make API call from background script to avoid CORS
    fetch('https://web-production-a62d7.up.railway.app/estimate_emissions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amazon_url: request.url,
        postcode: request.postcode,
        include_packaging: true
      })
    })
    .then(response => response.json())
    .then(data => {
      sendResponse({ success: true, data: data });
    })
    .catch(error => {
      console.error('API Error:', error);
      sendResponse({ success: false, error: error.message });
    });
    
    return true; // Keep message channel open for async response
  }
});