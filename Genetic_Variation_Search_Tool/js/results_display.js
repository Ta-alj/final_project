// this is to fetch the MONDO description using the api
async function fetchMondoDescription(mondoId) {
    // Constructing the api url using the provided mondo ids
    const url = `https://www.ebi.ac.uk/ols4/api/ontologies/mondo/terms?obo_id=MONDO:${mondoId}`;

    try {
        //making the requestand checking if its ok
        const response = await fetch(url);
        if (!response.ok) throw new Error('Description not available');


        // going through the data and getting the relevant info needed
        const data = await response.json()
        const terms = data._embedded?.terms;
        
        if (terms && terms.length > 0 && terms[0].description && terms[0].description.length > 0) {
            const description = terms[0].description[0].trim();
            if (description) {
                return description;
            }
        }
        
        return "No description available";

    } catch (error) {
        // fall back message if there is an error with fetching
        return "Error fetching description";
    }
}

// this is to update all the MONDO elements on the page with their fetched descriptions
async function updateDescriptions() {
    // Find all elements that need a MONDO description
    const mondoElements = document.querySelectorAll('[data-mondo]');

    for (const element of mondoElements) {
        // Get the MONDO ID from the element and fetch the description
        const mondoId = element.getAttribute('data-mondo');
        const description = await fetchMondoDescription(mondoId);
        element.textContent = description;
    }
}


// Show or hide the warning message based on the search type
function showWarning() {
    const searchType = document.getElementById('search_type').value;
    const warningBox = document.getElementById('phenotype-warning');

    // Display the warning only if 'Phenotype' is selected
    if (searchType === 'phenotype') {
        warningBox.style.display = 'block';
    } else {
        warningBox.style.display = 'none';
    }
}
 // Run the function after the page is fully loaded
document.addEventListener("DOMContentLoaded", function() {
    updateDescriptions();
    const searchTypeElement = document.getElementById('search_type');
    if (searchTypeElement) {
        searchTypeElement.addEventListener('change', showWarning);
    }
});
