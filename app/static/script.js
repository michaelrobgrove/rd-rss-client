document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.setAttribute('data-theme', 
                document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
        });
    }

    // Feed management
    const addFeedBtn = document.getElementById('add-feed-btn');
    if (addFeedBtn) {
        addFeedBtn.addEventListener('click', addFeed);
    }

    // Settings management
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }

    // Manual refresh button
    const refreshBtn = document.getElementById('refresh-feeds-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshFeeds);
    }

    // API method call button
    const callApiBtn = document.getElementById('call-api-btn');
    if (callApiBtn) {
        callApiBtn.addEventListener('click', callApi);
    }
});

function addFeed() {
    const url = document.getElementById('feed-url').value;
    if (!url) {
        showAlert('Please enter a feed URL');
        return;
    }

    fetch('/api/feeds', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.reload();
        } else {
            showAlert('Failed to add feed: ' + data.message);
        }
    })
    .catch(error => showAlert('Error adding feed'));
}

function removeFeed(id) {
    if (confirm('Are you sure you want to remove this feed?')) {
        fetch(`/api/feeds/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.reload();
            } else {
                showAlert('Failed to remove feed');
            }
        })
        .catch(error => showAlert('Error removing feed'));
    }
}

function saveSettings() {
    const rdApiKey = document.getElementById('rd-api-key').value;
    
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rd_api_key: rdApiKey })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('Settings saved successfully');
        } else {
            showAlert('Failed to save settings');
        }
    })
    .catch(error => showAlert('Error saving settings'));
}

function refreshFeeds() {
    fetch('/api/refresh', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('Feeds refreshed successfully');
        } else {
            showAlert('Failed to refresh feeds');
        }
    })
    .catch(error => showAlert('Error refreshing feeds'));
}

function callApi() {
    const apiMethod = document.getElementById('api-method').value;
    let url = `/api/${apiMethod}`;
    let method = 'GET';
    let body = null;

    if (apiMethod === 'unrestrict_link') {
        const link = prompt('Enter the link to unrestrict:');
        if (!link) {
            showAlert('Link is required');
            return;
        }
        method = 'POST';
        body = JSON.stringify({ link: link });
    } else if (apiMethod === 'get_streaming_links' || apiMethod === 'delete_download') {
        const id = prompt('Enter the file/download ID:');
        if (!id) {
            showAlert('ID is required');
            return;
        }
        url += `/${id}`;
        if (apiMethod === 'delete_download') {
            method = 'DELETE';
        }
    } else if (apiMethod === 'update_user_settings') {
        const settings = prompt('Enter the settings as JSON:');
        if (!settings) {
            showAlert('Settings are required');
            return;
        }
        method = 'POST';
        body = settings;
    }

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: body
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('api-response').textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => showAlert('Error calling API'));
}

function showAlert(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert';
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}
