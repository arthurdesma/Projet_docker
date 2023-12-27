// Function for validating years
function validateYears() {
    const startYear = parseInt(document.getElementById('startYear').value, 10);
    const endYear = parseInt(document.getElementById('endYear').value, 10);

    if (startYear < 1950 || startYear > 2024 || endYear < 1950 || endYear > 2024) {
        alert('Please enter years between 1950 and 2024.');
        return false;
    }

    if (startYear > endYear) {
        alert('Start year must be less than or equal to end year.');
        return false;
    }

    return true;
}

// Function for updating the database
async function updateDatabase() {
    if (!validateYears()) return;

    try {
        const startYear = document.getElementById('startYear').value;
        const endYear = document.getElementById('endYear').value;

        const response = await fetch(`/update_and_index/?start_year=${startYear}&end_year=${endYear}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error("Error during request:", response.status, response.statusText, errorData);
            alert(`Error: ${response.status} ${response.statusText}\n${JSON.stringify(errorData)}`);
        } else {
            const data = await response.json();
            console.log("API Response:", data);
            alert(`Success: ${JSON.stringify(data)}`);
        }
    } catch (error) {
        console.error("Error during request submission:", error);
        alert(`Error during request submission: ${error}`);
    }
}

// Function for searching and displaying results
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('driverStandingsForm').addEventListener('submit', function (e) {
        e.preventDefault();
        const grandPrix = document.getElementById('grandPrix').value;
        const yearDriver = document.getElementById('yearDriver').value;
        searchDriverStandings(grandPrix, yearDriver);
    });

    document.getElementById('grandPrixResultsForm').addEventListener('submit', function (e) {
        e.preventDefault();
        const yearGrandPrix = document.getElementById('yearGrandPrix').value;
        searchGrandPrixResults(yearGrandPrix);
    });
});

async function searchDriverStandings(grandPrix, year) {
    let url = '/search/driver_standings/?';
    const params = [];
    if (grandPrix) {
        params.push(`grand_prix=${encodeURIComponent(grandPrix)}`);
    }
    // Add the year parameter only if it has a value
    if (year && year.trim() !== '') {
        params.push(`year=${encodeURIComponent(year)}`);
    }
    url += params.join('&');

    const response = await fetch(url);
    const data = await response.json();
    updateTableBody('driverStandingsTableBody', data.data);
}


async function searchGrandPrixResults(year) {
    let url = '/search/grand_prix_results/?';
    // Add the year parameter only if it has a value and is not an empty string
    if (year && year.trim() !== '') {
        url += `year=${encodeURIComponent(year)}`;
    }

    const response = await fetch(url);
    const data = await response.json();
    updateTableBody('grandPrixResultsTableBody', data.data);
}


function displayResults(data, elementId) {
    const resultsElement = document.getElementById(elementId);
    resultsElement.innerHTML = ''; // Clear previous results
    data.data.forEach(item => {
        const div = document.createElement('div');
        div.textContent = JSON.stringify(item);
        resultsElement.appendChild(div);
    });
}

// This function updates the table with search results
function updateTableBody(tableBodyId, items) {
    const tableBody = document.getElementById(tableBodyId);
    tableBody.innerHTML = ''; // Clear existing content

    items.forEach(item => {
        const row = document.createElement('tr');

        // Assuming item contains keys like 'Position', 'Grand Prix', etc.
        Object.keys(item).forEach(key => {
            if (key === '_id') return;

            const cell = document.createElement('td');
            cell.textContent = item[key];
            row.appendChild(cell);
        });

        tableBody.appendChild(row);
    });
}
