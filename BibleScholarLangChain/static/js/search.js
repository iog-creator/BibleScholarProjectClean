// Enhanced search.js with comprehensive error handling and loading states

// Global variables
let currentSearch = null;

function searchVerses() {
    const query = document.getElementById('searchInput').value.trim();
    const resultsDiv = document.getElementById('searchResults');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorAlert = document.getElementById('errorAlert');
    const searchStats = document.getElementById('searchStats');
    const searchButton = document.getElementById('searchButton');
    
    // Validate input
    if (!query) {
        showError('Please enter a search term');
        return;
    }
    
    // Show loading state
    showLoading(true);
    hideError();
    hideStats();
    resultsDiv.innerHTML = '';
    searchButton.disabled = true;
    
    // Cancel previous search if still running
    if (currentSearch) {
        currentSearch.abort();
    }
    
    // Create new AbortController for this search
    const controller = new AbortController();
    currentSearch = controller;
    
    const startTime = Date.now();
    
    // Perform search with timeout
    const timeoutId = setTimeout(() => {
        controller.abort();
        showError('Search timed out. Please try a simpler query.');
        showLoading(false);
        searchButton.disabled = false;
    }, 30000); // 30 second timeout
    
    fetch(`/api/search?q=${encodeURIComponent(query)}&type=verse`, {
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`Search failed: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        const totalTime = Date.now() - startTime;
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Show search statistics
        showStats(data, totalTime);
        
        // Display results
        displayResults(data.results, query);
        
    })
    .catch(error => {
        if (error.name === 'AbortError') {
            console.log('Search was cancelled');
        } else {
            console.error('Search error:', error);
            showError(`Search failed: ${error.message}`);
        }
    })
    .finally(() => {
        showLoading(false);
        searchButton.disabled = false;
        currentSearch = null;
        clearTimeout(timeoutId);
    });
}

function displayResults(results, query) {
    const resultsDiv = document.getElementById('searchResults');
    
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                No verses found for "${query}". Try different search terms or check spelling.
            </div>
        `;
        return;
    }
    
    let html = `<h6 class="mb-3">Found ${results.length} verse${results.length === 1 ? '' : 's'} for "${query}":</h6>`;
    
    results.forEach((result, index) => {
        html += `
            <div class="card verse-card">
                <div class="card-body">
                    <h6 class="verse-reference">
                        <i class="fas fa-bookmark"></i>
                        ${result.book} ${result.chapter}:${result.verse}
                    </h6>
                    <p class="verse-text">${highlightSearchTerms(result.text, query)}</p>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="getInsights('${result.book} ${result.chapter}:${result.verse}', '${escapeHtml(result.text)}')">
                            <i class="fas fa-lightbulb"></i>
                            Get Insights
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="copyVerse('${result.book} ${result.chapter}:${result.verse}', '${escapeHtml(result.text)}')">
                            <i class="fas fa-copy"></i>
                            Copy
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

function highlightSearchTerms(text, query) {
    if (!query || query.length < 2) return text;
    
    const words = query.split(/\s+/).filter(word => word.length > 1);
    let highlightedText = text;
    
    words.forEach(word => {
        const regex = new RegExp(`(${escapeRegex(word)})`, 'gi');
        highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
    });
    
    return highlightedText;
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function escapeHtml(text) {
    return text.replace(/'/g, '&#39;').replace(/"/g, '&quot;');
}

function showLoading(show) {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = show ? 'block' : 'none';
    }
}

function hideError() {
    const errorAlert = document.getElementById('errorAlert');
    if (errorAlert) {
        errorAlert.style.display = 'none';
    }
}

function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    if (errorAlert && errorMessage) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
    }
}

function showStats(data, totalTime) {
    const searchStats = document.getElementById('searchStats');
    if (searchStats) {
        const serverTime = data.search_time ? `${data.search_time}s` : 'N/A';
        const clientTime = `${(totalTime / 1000).toFixed(3)}s`;
        
        searchStats.innerHTML = `
            <i class="fas fa-clock"></i>
            Found ${data.count || 0} results in ${clientTime} (server: ${serverTime})
        `;
        searchStats.style.display = 'block';
    }
}

function hideStats() {
    const searchStats = document.getElementById('searchStats');
    if (searchStats) {
        searchStats.style.display = 'none';
    }
}

function getInsights(reference, text) {
    // Show loading state
    const insightsDiv = document.createElement('div');
    insightsDiv.id = 'insights-modal';
    insightsDiv.innerHTML = `
        <div class="modal" style="display: block; background: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1000;">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Biblical Insights for ${reference}</h5>
                        <button type="button" class="btn-close" onclick="closeInsights()"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">Getting insights from LM Studio...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(insightsDiv);

    // Call LM Studio for insights
    fetch('http://localhost:5000/api/contextual_insights/insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            query: `Provide biblical insights and commentary for ${reference}: "${text}". Include theological significance, historical context, and practical applications.`,
            include_verses: false
        })
    })
    .then(response => response.json())
    .then(data => {
        const modalBody = insightsDiv.querySelector('.modal-body');
        if (data.insights) {
            modalBody.innerHTML = `
                <div class="insights-content">
                    <h6 class="text-primary">${reference}</h6>
                    <blockquote class="blockquote border-start border-primary ps-3 mb-3">
                        <p class="mb-0">"${text}"</p>
                    </blockquote>
                    <div class="insights-text" style="white-space: pre-wrap; line-height: 1.6;">
                        ${data.insights}
                    </div>
                    <small class="text-muted mt-3 d-block">
                        Generated by ${data.model} • ${new Date().toLocaleTimeString()}
                    </small>
                </div>
            `;
        } else {
            modalBody.innerHTML = `
                <div class="alert alert-danger">
                    <h6>Error getting insights</h6>
                    <p>${data.error || 'Unknown error occurred'}</p>
                    <button class="btn btn-secondary" onclick="closeInsights()">Close</button>
                </div>
            `;
        }
    })
    .catch(error => {
        const modalBody = insightsDiv.querySelector('.modal-body');
        modalBody.innerHTML = `
            <div class="alert alert-danger">
                <h6>Failed to get insights</h6>
                <p>Error: ${error.message}</p>
                <p><small>Make sure the API server is running on port 5000 and LM Studio is accessible.</small></p>
                <button class="btn btn-secondary" onclick="closeInsights()">Close</button>
            </div>
        `;
    });
}

function closeInsights() {
    const modal = document.getElementById('insights-modal');
    if (modal) {
        modal.remove();
    }
}

function copyVerse(reference, text) {
    const verseText = `${reference} - ${text}`;
    navigator.clipboard.writeText(verseText).then(() => {
        // Show temporary success message
        const btn = event.target;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.classList.replace('btn-outline-secondary', 'btn-success');
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.replace('btn-success', 'btn-outline-secondary');
        }, 2000);
    }).catch(err => {
        showError('Failed to copy verse to clipboard');
    });
}

// Handle Enter key in search input
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchVerses();
            }
        });
        
        // Focus on search input
        searchInput.focus();
    }
    
    // Test server connectivity on page load
    testServerHealth();
});

function testServerHealth() {
    Promise.all([
        fetch('/health').then(r => r.json()),
        fetch('http://localhost:5000/health').then(r => r.json())
    ])
    .then(([webHealth, apiHealth]) => {
        console.log('Server health check:', { web: webHealth, api: apiHealth });
        
        // Show connection status in console
        if (webHealth.status === 'OK' && apiHealth.status === 'ok') {
            console.log('✅ All servers are healthy');
        }
    })
    .catch(error => {
        console.warn('⚠️ Server health check failed:', error);
        // Don't show error to user unless they try to search
    });
} 