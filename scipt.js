const OWNER_KEY = 'your_owner_key'; // Replace with your actual owner key
const keys = JSON.parse(localStorage.getItem('keys')) || {};

function login() {
    const ownerKeyInput = document.getElementById('ownerKeyInput').value;
    if (ownerKeyInput === OWNER_KEY) {
        sessionStorage.setItem('authenticated', 'true');
        showDashboard();
    } else {
        alert('Invalid Owner Key');
    }
}

function logout() {
    sessionStorage.removeItem('authenticated');
    showLogin();
}

function showLogin() {
    document.getElementById('loginPage').style.display = 'block';
    document.getElementById('dashboardPage').style.display = 'none';
    document.getElementById('stepPage').style.display = 'none';
    document.getElementById('completePage').style.display = 'none';
}

function showDashboard() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboardPage').style.display = 'block';
    document.getElementById('stepPage').style.display = 'none';
    document.getElementById('completePage').style.display = 'none';
    updateKeysTable();
}

function showStep(step) {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboardPage').style.display = 'none';
    document.getElementById('stepPage').style.display = 'block';
    document.getElementById('completePage').style.display = 'none';
    document.getElementById('currentStep').innerText = step;
}

function showComplete(key) {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboardPage').style.display = 'none';
    document.getElementById('stepPage').style.display = 'none';
    document.getElementById('completePage').style.display = 'block';
    document.getElementById('generatedKey').innerText = key;
}

function updateKeysTable() {
    const keysTableBody = document.querySelector('#keysTable tbody');
    keysTableBody.innerHTML = '';

    for (const ip in keys) {
        const row = document.createElement('tr');
        const keyCell = document.createElement('td');
        keyCell.innerText = keys[ip].key;
        const ipCell = document.createElement('td');
        ipCell.innerText = ip;
        const expirationCell = document.createElement('td');
        expirationCell.innerText = keys[ip].expiration;
        const actionsCell = document.createElement('td');
        
        const deleteButton = document.createElement('button');
        deleteButton.innerText = 'Delete';
        deleteButton.onclick = () => deleteKey(ip);
        
        actionsCell.appendChild(deleteButton);
        
        row.appendChild(keyCell);
        row.appendChild(ipCell);
        row.appendChild(expirationCell);
        row.appendChild(actionsCell);
        keysTableBody.appendChild(row);
    }
}

function deleteKey(ip) {
    if (confirm('Are you sure you want to delete this key?')) {
        delete keys[ip];
        localStorage.setItem('keys', JSON.stringify(keys));
        updateKeysTable();
    }
}

function generateKey(ip) {
    const key = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const expiration = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
    keys[ip] = { key, expiration, ip };
    localStorage.setItem('keys', JSON.stringify(keys));
    return key;
}

function nextStep() {
    let currentStep = parseInt(document.getElementById('currentStep').innerText);
    if (currentStep < 3) {
        showStep(currentStep + 1);
    } else {
        const ip = 'user-ip-placeholder'; // Replace with actual user IP
        const key = generateKey(ip);
        showComplete(key);
    }
}

window.onload = () => {
    if (sessionStorage.getItem('authenticated') === 'true') {
        showDashboard();
    } else {
        showLogin();
    }
};
