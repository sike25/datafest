document.getElementById('rental-form').addEventListener('submit', function(event) {
    event.preventDefault();
    submitForm();
});

// Function to submit form data to Python backend
async function submitForm() {
    console.log('Submit buttonn clicked');
    
    const quarter = document.getElementById('rental-quarter').value;
    const region = document.getElementById('rental-region').value;
    const industry = document.getElementById('industry-type').value;
    const priceMin = document.getElementById('price-min').value;
    const priceMax = document.getElementById('price-max').value;
    const talentNeeded = document.getElementById('talent-needed').checked;

    // Form validation
    if (!quarter || !region || !industry) {
        alert('Please fill out all required fields');
        return;
    }
    
    // Prepare data for sending to backend
    const formData = {
        quarter,
        region,
        industry,
        budget_min: priceMin || null,
        budget_max: priceMax || null,
        talent: talentNeeded
    };

    try {
        // Show loading state (optional)
        const resultContainer = document.getElementById('result-container');
        const resultText = document.getElementById('result-text');
        resultText.textContent = "Processing your request...";
        resultContainer.style.display = 'block';
        
        // Send data to Python backend
        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const responseData = await response.json();
        
        // Display success message
        resultText.textContent = 'Analysis complete!';
        console.log('Server response:', responseData);


        // Store the analysis results in localStorage to access on the results page
        try {
            console.log('Storing data in localStorage');
            localStorage.setItem('analysisResults', JSON.stringify(responseData.message));
            localStorage.setItem('selectedRegion', getRegionText(region));
            console.log('Data stored successfully');
            
            // Navigate to the results page
            console.log('Redirecting to results page...');
            window.location.href = '/results.html';
            
            // Add an additional log - this should NOT appear if redirect works properly
            setTimeout(() => {
                console.log('Still on the page after redirect attempt');
            }, 500);
            
        } catch (storageError) {
            console.error('Error with localStorage or redirect:', storageError);
            resultText.textContent = "Error saving results. Please check console for details.";
        }
        
    } catch (error) {
        console.error('Error submitting form:', error);
        
        // Display error message
        const resultContainer = document.getElementById('result-container');
        const resultText = document.getElementById('result-text');
        resultText.textContent = "Sorry, there was an error processing your request. Please try again later.";
        resultContainer.style.display = 'block';
    }
}

function getRegionText(value) {
    const regions = {
        'midwest': 'Midwest and Central',
        'northeast': 'Northeast',
        'south': 'South',
        'west': 'West'
    };
    return regions[value];
}

// function getIndustryText(value) {
//     const industries = {
//         'tami': 'Technology, Advertising, Media, and Information',
//         'fsi': 'Financial Services and Insurance',
//         'legal': 'Legal Services'
//     };
//     return industries[value];
// }


// function getQuarterText(value) {
//     const quarters = {
//         'q1': 'Q1 (January-March)',
//         'q2': 'Q2 (April-June)',
//         'q3': 'Q3 (July-September)',
//         'q4': 'Q4 (October-December)'
//     };
//     return quarters[value];
// }