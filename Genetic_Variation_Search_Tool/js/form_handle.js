document.addEventListener('DOMContentLoaded', function () {
    const searchTypeElement = document.getElementById('search_type');

    if (searchTypeElement) {
        searchTypeElement.addEventListener('change', showWarning);
    } else {
        console.error("Element with ID 'search_type' not found.");
    }
});

function showWarning() {
    const searchType = document.getElementById('search_type').value;
    const warningBox = document.getElementById('phenotype-warning');
    
    if (searchType === 'phenotype') {
        warningBox.style.display = 'block';
    } else {
        warningBox.style.display = 'none';
    }
}
