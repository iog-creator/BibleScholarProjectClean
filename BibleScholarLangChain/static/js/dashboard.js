// dashboard.js - Study Dashboard UI logic

document.addEventListener('DOMContentLoaded', function() {
    console.log('Study Dashboard loaded');

    // --- User Feedback Helpers ---
    function showLoading(container, message = "Loading...") {
        if (typeof container === 'string') {
            const element = document.getElementById(container);
            if (element) {
                element.innerHTML = `<div class="loading">${message}</div>`;
            }
        } else if (container) {
            container.innerHTML = `<div class="loading">${message}</div>`;
        }
    }
    
    function showError(container, message) {
        if (typeof container === 'string') {
            const element = document.getElementById(container);
            if (element) {
                element.innerHTML = `<div class="error-message">${message}</div>`;
            }
        } else if (container) {
            container.innerHTML = `<div class="error-message">${message}</div>`;
        } else {
            console.error(message);
        }
    }

    // --- Tone and Theme Toggles ---
    document.getElementById('tone-simple').addEventListener('click', function() {
        this.classList.add('active');
        document.getElementById('tone-detailed').classList.remove('active');
    });
    document.getElementById('tone-detailed').addEventListener('click', function() {
        this.classList.add('active');
        document.getElementById('tone-simple').classList.remove('active');
    });
    document.getElementById('theme-light').addEventListener('click', function() {
        this.classList.add('active');
        document.getElementById('theme-dark').classList.remove('active');
    });
    document.getElementById('theme-dark').addEventListener('click', function() {
        this.classList.add('active');
        document.getElementById('theme-light').classList.remove('active');
    });

    // --- Double-click Expansion (Swapping) ---
    const leftPanel = document.getElementById('leftPanel');
    const centerPanel = document.getElementById('centerPanel');
    const rightPanel = document.getElementById('rightPanel');
    const historicalCard = rightPanel.querySelector('.dashboard-card');
    const verseCard = centerPanel.querySelector('[data-tab="verse"]');
    const chatCard = centerPanel.querySelector('[data-tab="chat"]');
    function swapPanels(expandTab) {
        leftPanel.className = 'col-md-2';
        centerPanel.className = 'col-md-6';
        rightPanel.className = 'col-md-4';
        centerPanel.innerHTML = '';
        rightPanel.innerHTML = '';
        if (expandTab === 'historical') {
            centerPanel.appendChild(historicalCard);
            rightPanel.appendChild(verseCard);
            rightPanel.appendChild(chatCard);
            showLinkedEventsList(true);
        } else if (expandTab === 'verse') {
            centerPanel.appendChild(verseCard);
            centerPanel.appendChild(chatCard);
            rightPanel.appendChild(historicalCard);
            showLinkedEventsList(false);
        } else if (expandTab === 'chat') {
            centerPanel.appendChild(chatCard);
            centerPanel.appendChild(verseCard);
            rightPanel.appendChild(historicalCard);
            showLinkedEventsList(false);
        }
    }
    verseCard.addEventListener('dblclick', function() { swapPanels('verse'); });
    chatCard.addEventListener('dblclick', function() { swapPanels('chat'); });
    historicalCard.addEventListener('dblclick', function() { swapPanels('historical'); });

    // --- Linked Events List (for teaching, mock data) ---
    function renderLinkedEventsList(linkedPairs) {
        const linkedEventsDiv = document.getElementById('linkedEvents');
        linkedEventsDiv.innerHTML = '';
        linkedPairs.forEach(pair => {
            const div = document.createElement('div');
            div.className = 'd-flex align-items-center mb-2';
            div.innerHTML = `
                <svg width="18" height="18" style="margin-right:8px;">
                    <defs>
                        <linearGradient id="splitGradientSmall" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="50%" stop-color="#20C997"/>
                            <stop offset="50%" stop-color="#6C757D"/>
                        </linearGradient>
                    </defs>
                    <circle cx="9" cy="9" r="8" fill="url(#splitGradientSmall)" stroke="#5A32A3" stroke-width="1.5"/>
                </svg>
                <span style="font-size:13px;">${pair.biblical} <span style="color:#888;">&#8596;</span> ${pair.world}</span>
            `;
            linkedEventsDiv.appendChild(div);
        });
    }
    const mockLinkedPairs = [
        { biblical: 'Creation (~4000 BC)', world: 'Sumerian Civilization (~3000 BC)' },
        { biblical: 'Flood (~2348 BC)', world: 'Great Pyramid (~2560 BC)' },
    ];
    function showLinkedEventsList(show) {
        const linkedEventsDiv = document.getElementById('linkedEvents');
        const linkedCircle = document.getElementById('linkedCircle');
        if (show) {
            renderLinkedEventsList(mockLinkedPairs);
            linkedEventsDiv.style.display = '';
            if (linkedCircle) linkedCircle.style.display = '';
        } else {
            linkedEventsDiv.style.display = 'none';
            if (linkedCircle) linkedCircle.style.display = 'none';
        }
    }
    showLinkedEventsList(false);

    // --- Verse Search ---
    const searchInput = document.getElementById('searchInput');
    const verseReference = document.getElementById('verseReference');
    const verseText = document.getElementById('verseText');
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (!query) {
                showError('verseReference', 'Please enter a verse reference');
                return;
            }
            showLoading('verseReference', 'Searching...');
            fetch(`/api/search?q=${encodeURIComponent(query)}&type=verse`)
                .then(res => {
                    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                    return res.json();
                })
                .then(data => {
                    if (data.verses && data.verses.length > 0) {
                        const v = data.verses[0];
                        verseReference.textContent = `${v.book_name} ${v.chapter_num}:${v.verse_num}`;
                        verseText.textContent = v.verse_text;
                    } else {
                        verseReference.textContent = 'No verse found';
                        verseText.textContent = '-';
                    }
                })
                .catch(err => {
                    showError('verseReference', 'Error searching for verse');
                    console.error(err);
                });
        }
    });

    // --- Chat Functionality ---
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendChat = document.getElementById('sendChat');
    const clearChat = document.getElementById('clearChat');
    function appendChatMessage(role, text) {
        const div = document.createElement('div');
        div.className = `chat-msg chat-msg-${role}`;
        div.style.background = role === 'user' ? '#E6F4FA' : '#F5F3FF';
        div.style.margin = '8px 0';
        div.style.padding = '8px 12px';
        div.style.borderRadius = '8px';
        div.style.maxWidth = '80%';
        div.style.alignSelf = role === 'user' ? 'flex-end' : 'flex-start';
        div.innerHTML = text; // Use innerHTML to support links
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    function sendChatMessage() {
        const msg = chatInput.value.trim();
        if (!msg) return;
        appendChatMessage('user', msg);
        chatInput.value = '';
        showLoading('chatMessages', 'Generating response...');
        const verseMatch = msg.match(/(Genesis|John|Psalm)\s+\d+:\d+/i);
        const selectedTranslation = document.getElementById('translationSelect').value;
        const requestBody = verseMatch 
            ? { type: 'verse', reference: verseMatch[0], translation: selectedTranslation }
            : { type: 'text_snippet', text: msg, translation: selectedTranslation };
        console.log('Sending request to /api/contextual_insights/insights with body:', requestBody);
        fetch('/api/contextual_insights/insights', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        })
        .then(res => {
            console.log('Response status:', res.status);
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.insights) {
                const insightId = `insight-${Date.now()}`;
                const summary = data.insights.summary || 'No summary available.';
                appendChatMessage('assistant', `${summary} <a href="#" class="view-insights" data-insight-id="${insightId}">[View Detailed Insights]</a>`);
                localStorage.setItem(insightId, JSON.stringify(data.insights));
            } else {
                appendChatMessage('assistant', 'No insights available for this query.');
            }
        })
        .catch(err => {
            appendChatMessage('assistant', 'Unexpected response from server, please try again.');
            console.error('Fetch error:', err);
        });
    }
    sendChat.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') sendChatMessage();
    });
    clearChat.addEventListener('click', function() {
        chatMessages.innerHTML = '';
    });
    document.getElementById('askAboutVerse').addEventListener('click', function(e) {
        e.preventDefault();
        const ref = verseReference.textContent;
        if (ref && ref !== 'No verse selected' && ref !== 'No verse found') {
            chatInput.value = `Explain ${ref}`;
            sendChatMessage();
        } else {
            showError('chatMessages', 'No verse selected to analyze');
        }
    });

    // --- View Detailed Insights Modal ---
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('view-insights')) {
            e.preventDefault();
            const insightId = e.target.getAttribute('data-insight-id');
            const insights = JSON.parse(localStorage.getItem(insightId));
            if (insights) {
                const insightsContent = document.getElementById('insightsContent');
                insightsContent.innerHTML = `
                    <div class="card mb-3">
                        <div class="card-header"><strong>Summary</strong></div>
                        <div class="card-body">${insights.summary || 'No summary available.'}</div>
                    </div>
                    <div class="card mb-3">
                        <div class="card-header"><strong>Theological Terms</strong></div>
                        <div class="card-body">
                            ${insights.theological_terms ? Object.entries(insights.theological_terms).map(([term, def]) => `<p><b>${term}</b>: ${def}</p>`).join('') : 'No theological terms found.'}
                        </div>
                    </div>
                    <div class="card mb-3">
                        <div class="card-header"><strong>Cross References</strong></div>
                        <div class="card-body">
                            ${insights.cross_references && insights.cross_references.length > 0 ? 
                                '<ul>' + insights.cross_references.map(ref => `<li>${ref.reference} (${ref.translation || 'KJV'}): ${ref.text} <br><small>${ref.reason || ''}</small></li>`).join('') + '</ul>' : 
                                'No cross references found.'}
                        </div>
                    </div>
                    <div class="card mb-3">
                        <div class="card-header"><strong>Historical Context</strong></div>
                        <div class="card-body">${insights.historical_context || 'No historical context available.'}</div>
                    </div>
                `;
                const modal = new bootstrap.Modal(document.getElementById('insightsModal'));
                modal.show();
            }
        }
    });

    // --- Database Statistics Fetch ---
    fetch('/api/lexicon/stats')
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.stats) {
                document.getElementById('hebrewLexiconCount').textContent = data.stats.hebrew_entries || 'N/A';
                document.getElementById('greekLexiconCount').textContent = data.stats.greek_entries || 'N/A';
            } else {
                showError('hebrewLexiconCount', 'Error loading statistics');
                showError('greekLexiconCount', 'Error loading statistics');
            }
        })
        .catch(err => {
            showError('hebrewLexiconCount', 'Error loading statistics');
            showError('greekLexiconCount', 'Error loading statistics');
            console.error(err);
        });
    fetch('/api/names')
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data) {
                document.getElementById('verseCount').textContent = data.verse_count || 'N/A';
                document.getElementById('properNamesCount').textContent = data.proper_names_count || 'N/A';
            } else {
                showError('verseCount', 'Error loading statistics');
                showError('properNamesCount', 'Error loading statistics');
            }
        })
        .catch(err => {
            showError('verseCount', 'Error loading statistics');
            showError('properNamesCount', 'Error loading statistics');
            console.error(err);
        });

    // --- History Details Update on Timeline Click ---
    document.querySelectorAll('#biblicalTimeline li, #worldTimeline li').forEach(item => {
        item.addEventListener('click', function() {
            const eventName = this.textContent.split(':')[0].trim();
            const description = this.textContent.split(':')[1].trim();
            const verse = this.textContent.match(/\((.*?)\)/)?.[1] || '';
            updateHistoryDetails({
                name: eventName,
                description: description,
                verse: verse,
                isBiblical: this.parentElement.id === 'biblicalTimeline'
            });
        });
    });
    function updateHistoryDetails(event) {
        const historyDetails = document.getElementById('historyDetails');
        const imageUrl = `https://via.placeholder.com/100x75.png?text=${encodeURIComponent(event.name)}`;
        const relatedInfo = event.isBiblical 
            ? `Related: ${event.verse || 'N/A'}`
            : `Related: ${event.verse || 'Historical context of the period.'}`;
        const description = event.description + (event.isBiblical 
            ? ' This event is foundational to biblical history.' 
            : ' This event shaped the historical context.');
        historyDetails.innerHTML = `
            <div class="history-content">
                <img src="${imageUrl}" alt="${event.name}" style="width:100px; height:auto; margin-bottom:10px; border:1px solid #E9ECEF; border-radius:4px;">
                <p>${description}</p>
                <p>${relatedInfo}</p>
                <small>Source: ${event.isBiblical ? 'STEPBible' : 'Historical Records'}</small>
            </div>
        `;
        historyDetails.scrollTop = 0;
        // Add error event listener to the image
        const img = historyDetails.querySelector('img');
        img.addEventListener('error', function() {
            this.src = 'https://via.placeholder.com/100x75.png?text=Image+Unavailable';
            this.alt = 'Image unavailable';
        });
    }

    // Expose for test automation
    window.updateHistoryDetails = updateHistoryDetails;

    // Elements
    const verseForm = document.getElementById('verseForm');
    const reference = document.getElementById('reference');
    const translation = document.getElementById('translation');
    const results = document.getElementById('results');
    const referenceHeading = document.getElementById('referenceHeading');
    const verseText = document.getElementById('verseText');
    const context = document.getElementById('context');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    
    // Insights elements
    const historicalContextContent = document.getElementById('historicalContextContent');
    const theologicalSignificanceContent = document.getElementById('theologicalSignificanceContent');
    const keyThemesContent = document.getElementById('keyThemesContent');
    const applicationContent = document.getElementById('applicationContent');
    
    // Vector search elements
    const vectorSearchForm = document.getElementById('vectorSearchForm');
    const searchQuery = document.getElementById('searchQuery');
    const searchResults = document.getElementById('searchResults');
    const similarVerses = document.getElementById('similarVerses');
    const searchLoading = document.getElementById('searchLoading');
    const searchError = document.getElementById('searchError');
    
    // Cross references
    const crossReferences = document.getElementById('crossReferences');
    
    // API endpoints
    const API_BASE_URL = '/api';
    
    // Get insights
    if (verseForm) {
        verseForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const referenceValue = reference.value.trim();
            const translationValue = translation.value;
            
            if (!referenceValue) {
                showError('Please enter a Bible reference');
                return;
            }
            
            // Show loading
            loading.classList.remove('d-none');
            results.classList.add('d-none');
            error.classList.add('d-none');
            
            // API call
            fetch(`${API_BASE_URL}/contextual_insights/insights`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'verse',
                    reference: referenceValue,
                    translation: translationValue
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                // Hide loading
                loading.classList.add('d-none');
                
                // Show results
                results.classList.remove('d-none');
                
                // Update reference and verse text
                referenceHeading.textContent = data.reference;
                verseText.textContent = data.verse_text;
                
                // Update context
                context.innerHTML = '';
                if (data.context && data.context.length > 0) {
                    data.context.forEach(verse => {
                        const verseElement = document.createElement('p');
                        verseElement.textContent = `${verse.verse_num}: ${verse.verse_text}`;
                        if (parseInt(verse.verse_num) === parseInt(referenceValue.split(':')[1])) {
                            verseElement.style.fontWeight = 'bold';
                        }
                        context.appendChild(verseElement);
                    });
                } else {
                    context.innerHTML = '<p>No context available</p>';
                }
                
                // Update insights
                if (data.insights) {
                    historicalContextContent.textContent = data.insights.historical_context || 'No information available';
                    theologicalSignificanceContent.textContent = data.insights.theological_significance || 'No information available';
                    keyThemesContent.textContent = data.insights.key_themes || 'No information available';
                    applicationContent.textContent = data.insights.application || 'No information available';
                }
                
                // Update cross references
                updateCrossReferences(data.cross_references);
            })
            .catch(err => {
                // Hide loading
                loading.classList.add('d-none');
                
                // Show error
                showError(err.message);
            });
        });
    }
    
    // Vector search
    if (vectorSearchForm) {
        vectorSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const query = searchQuery.value.trim();
            
            if (!query) {
                showSearchError('Please enter a search query');
                return;
            }
            
            // Show loading
            searchLoading.classList.remove('d-none');
            searchResults.classList.add('d-none');
            searchError.classList.add('d-none');
            
            // API call
            fetch(`${API_BASE_URL}/vector_search/vector-search?q=${encodeURIComponent(query)}&translation=${translation.value}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                // Hide loading
                searchLoading.classList.add('d-none');
                
                // Show results
                searchResults.classList.remove('d-none');
                
                // Update similar verses
                similarVerses.innerHTML = '';
                if (data.results && data.results.length > 0) {
                    data.results.forEach(verse => {
                        const verseElement = document.createElement('div');
                        verseElement.className = 'similar-verse';
                        
                        const referenceSpan = document.createElement('span');
                        referenceSpan.className = 'fw-bold';
                        referenceSpan.textContent = `${verse.book_name} ${verse.chapter_num}:${verse.verse_num}`;
                        
                        const similaritySpan = document.createElement('span');
                        similaritySpan.className = 'similarity-score';
                        similaritySpan.textContent = `${Math.round(verse.similarity * 100)}%`;
                        
                        const textParagraph = document.createElement('p');
                        textParagraph.textContent = verse.verse_text;
                        
                        verseElement.appendChild(referenceSpan);
                        verseElement.appendChild(similaritySpan);
                        verseElement.appendChild(document.createElement('br'));
                        verseElement.appendChild(textParagraph);
                        
                        // Add click event to load verse
                        verseElement.addEventListener('click', function() {
                            reference.value = `${verse.book_name} ${verse.chapter_num}:${verse.verse_num}`;
                            verseForm.dispatchEvent(new Event('submit'));
                        });
                        
                        similarVerses.appendChild(verseElement);
                    });
                } else {
                    similarVerses.innerHTML = '<p>No similar verses found</p>';
                }
            })
            .catch(err => {
                // Hide loading
                searchLoading.classList.add('d-none');
                
                // Show error
                showSearchError(err.message);
            });
        });
    }
    
    // Helper function to update cross references
    function updateCrossReferences(refs) {
        crossReferences.innerHTML = '';
        
        if (refs && refs.length > 0) {
            refs.forEach(ref => {
                const refElement = document.createElement('div');
                refElement.className = 'cross-reference';
                
                const referenceSpan = document.createElement('span');
                referenceSpan.className = 'fw-bold';
                referenceSpan.textContent = ref.reference;
                
                const textParagraph = document.createElement('p');
                textParagraph.textContent = ref.text;
                
                refElement.appendChild(referenceSpan);
                refElement.appendChild(document.createElement('br'));
                refElement.appendChild(textParagraph);
                
                // Add click event to load verse
                refElement.addEventListener('click', function() {
                    reference.value = ref.reference;
                    verseForm.dispatchEvent(new Event('submit'));
                });
                
                crossReferences.appendChild(refElement);
            });
        } else {
            crossReferences.innerHTML = '<p>No cross references available</p>';
        }
    }
    
    // Helper function to show search error
    function showSearchError(message) {
        searchError.textContent = message;
        searchError.classList.remove('d-none');
    }
    
    // Set a default verse on load
    if (reference) {
        reference.value = 'John 3:16';
        setTimeout(() => {
            verseForm.dispatchEvent(new Event('submit'));
        }, 500);
    }

    // Vector Search Form
    const vectorSearchForm = document.getElementById('vector-search-form');
    const vectorResults = document.getElementById('vector-results');
    
    if (vectorSearchForm) {
        vectorSearchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(vectorSearchForm);
            const query = formData.get('q');
            const translation = formData.get('translation');
            
            if (!query) {
                showError(vectorResults, 'Please enter a search query');
                return;
            }
            
            try {
                showLoading(vectorResults);
                
                const response = await fetch(`/api/vector_search/vector-search?q=${encodeURIComponent(query)}&translation=${encodeURIComponent(translation)}&limit=10`);
                const data = await response.json();
                
                if (response.ok) {
                    displayVectorResults(data, vectorResults);
                } else {
                    showError(vectorResults, data.error || 'An error occurred');
                }
            } catch (error) {
                showError(vectorResults, 'Failed to fetch results');
                console.error(error);
            }
        });
    }
    
    // Lexicon Form
    const lexiconForm = document.getElementById('lexicon-form');
    const lexiconResults = document.getElementById('lexicon-results');
    
    if (lexiconForm) {
        lexiconForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(lexiconForm);
            const strongsId = formData.get('strongs_id');
            
            if (!strongsId) {
                showError(lexiconResults, 'Please enter a Strong\'s ID');
                return;
            }
            
            try {
                showLoading(lexiconResults);
                
                const response = await fetch(`/api/lexicon/search?strongs_id=${encodeURIComponent(strongsId)}`);
                const data = await response.json();
                
                if (response.ok) {
                    displayLexiconResults(data, lexiconResults);
                } else {
                    showError(lexiconResults, data.error || 'An error occurred');
                }
            } catch (error) {
                showError(lexiconResults, 'Failed to fetch results');
                console.error(error);
            }
        });
    }
    
    // Verse Search Form
    const verseSearchForm = document.getElementById('verse-search-form');
    const verseResults = document.getElementById('verse-results');
    
    if (verseSearchForm) {
        verseSearchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(verseSearchForm);
            const query = formData.get('q');
            const type = formData.get('type');
            
            if (!query) {
                showError(verseResults, 'Please enter a search query');
                return;
            }
            
            try {
                showLoading(verseResults);
                
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&type=${encodeURIComponent(type)}`);
                const data = await response.json();
                
                if (response.ok) {
                    displayVerseResults(data, verseResults);
                } else {
                    showError(verseResults, data.error || 'An error occurred');
                }
            } catch (error) {
                showError(verseResults, 'Failed to fetch results');
                console.error(error);
            }
        });
    }

    function displayVectorResults(data, container) {
        if (!container) return;
        
        if (!data.results || data.results.length === 0) {
            container.innerHTML = '<p>No similar verses found.</p>';
            return;
        }
        
        let html = '<h3>Similar Verses</h3><ul>';
        
        data.results.forEach(verse => {
            const similarity = Math.round(verse.similarity * 100);
            html += `
                <li>
                    <span class="reference">${verse.book_name} ${verse.chapter_num}:${verse.verse_num} (${verse.translation_source})</span>
                    <span class="similarity">${similarity}% similarity</span>
                    <p class="verse-text">${verse.verse_text}</p>
                </li>
            `;
        });
        
        html += '</ul>';
        container.innerHTML = html;
    }
    
    function displayLexiconResults(data, container) {
        if (!container) return;
        
        if (!data.entry) {
            container.innerHTML = '<p>No lexicon entry found.</p>';
            return;
        }
        
        const entry = data.entry;
        
        let html = `
            <h3>Lexicon Entry: ${entry.strongs_id}</h3>
            <div class="lexicon-data">
                <p><strong>Lemma:</strong> ${entry.lemma}</p>
                <p><strong>Transliteration:</strong> ${entry.transliteration}</p>
                <p><strong>Definition:</strong> ${entry.definition}</p>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    function displayVerseResults(data, container) {
        if (!container) return;
        
        if (!data.verses || data.verses.length === 0) {
            container.innerHTML = '<p>No verses found.</p>';
            return;
        }
        
        let html = '<h3>Verses Found</h3><ul>';
        
        data.verses.forEach(verse => {
            html += `
                <li>
                    <span class="reference">${verse.book_name} ${verse.chapter_num}:${verse.verse_num} (${verse.translation_source})</span>
                    <p class="verse-text">${verse.verse_text}</p>
                </li>
            `;
        });
        
        html += '</ul>';
        container.innerHTML = html;
    }
}); 