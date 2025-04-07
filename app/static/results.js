document.addEventListener('DOMContentLoaded', function() {
    // Get data from localStorage
    const analysisResults = JSON.parse(localStorage.getItem('analysisResults') || '[]');
    const selectedRegion = localStorage.getItem('selectedRegion') || 'Selected Region';
    
    // Update the page title
    document.getElementById('results-title').textContent = `Market Analysis Results for the ${selectedRegion}`;
    
    const resultsContainer = document.getElementById('results-container');
    
    // If no results, display a message
    if (!analysisResults.length) {
        resultsContainer.innerHTML = '<div class="no-results"><h2>No results found</h2><p>Please try different search criteria.</p></div>';
        return;
    }
    
    // Create a card for each result
    analysisResults.forEach(result => {
        const card = document.createElement('div');
        card.className = 'card';
        
        // Add special classes based on market attributes
        if (result.best_market) {
            card.classList.add('best-market');
            card.classList.add('best-market-reasons');
        }

        if (result.talent_hub) {
            card.classList.add('talent-hub');
        }

        if (result.economic_growth) { 
            card.classList.add('high-growth');
        }
        
        // Format the price as currency
        const formattedPrice = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            maximumFractionDigits: 0
        }).format(result.expected_price);
        
        // Create badges for special features
        const badges = [];
        if (result.best_market) badges.push('<span class="badge badge-recommended">Recommended</span>');
        if (result.talent_hub) badges.push('<span class="badge badge-talent">Talent Hub</span>');
        if (result.economic_growth) badges.push('<span class="badge badge-growth">High Growth</span>');
        
        // Create reasons list for best market
        let reasonsHTML = '';
        if (result.best_market) {
            // Check for wins property first (primary source of reasons)
            if (result.wins && result.wins.length) {
                reasonsHTML = `
                    <div class="reasons-section">
                        <ul class="reasons-list">
                            ${result.wins.map(reason => `<li>${reason}</li>`).join('')}
                        </ul>
                    </div>
                `;
            } 
            // Fall back to best_market_whys if wins isn't available
            else if (result.best_market_whys && result.best_market_whys.length) {
                reasonsHTML = `
                    <div class="reasons-section">
                        <ul class="reasons-list">
                            ${result.best_market_whys.map(reason => `<li>${reason}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        }
        
        // Create details list
        let detailsHTML = '';
        if (result.details && result.details.length) {
            detailsHTML = `
                <div class="details-section">
                    <h4>Market Details:</h4>
                    <ul class="details-list">
                        ${result.details.map(detail => `<li>${detail}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Create the card content
        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${result.market}</div>
                <div class="badges-container">${badges.join('')}</div>
            </div>
            <div class="card-content">
                <div class="card-subtitle">Expected Price: ${formattedPrice}</div>
                ${result.time ? `<div class="timing-info">Best time to rent: ${result.time}</div>` : ''}
                ${reasonsHTML}
                ${detailsHTML}
            </div>
        `;
        
        resultsContainer.appendChild(card);
    });
    

});