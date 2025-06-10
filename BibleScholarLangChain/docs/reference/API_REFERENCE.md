# BibleScholarProject API Reference

This document provides a comprehensive reference for all API endpoints in the BibleScholarProject.

*This document is complemented by the [api_standards](.cursor/rules/standards/api_standards.mdc) cursor rule.*

## Base URLs
- Lexicon API: `http://localhost:5000`
- Web App: `http://localhost:5001`
- Vector Search Demo: `http://localhost:5050`
- Bible QA API: `http://localhost:8000`
- Contextual Insights API: `http://localhost:5000`

## Health Endpoints

### Check Lexicon API Health
```
GET /health
```
Returns a 200 status code if the API is running properly.

### Check Web App Health
```
GET /health
```
Returns a 200 status code if the web app is running properly.

## Theological Terms Endpoints

### Theological Terms Report
```
GET /api/theological_terms_report
```
Returns a comprehensive report of theological terms with occurrence statistics.

Web App Route:
```
GET /theological_terms_report
```

### Validate Critical Hebrew Terms
```
GET /api/lexicon/hebrew/validate_critical_terms
```
Validates that critical Hebrew theological terms meet minimum occurrence counts.

Web App Route:
```
GET /hebrew_terms_validation
```

### Cross Language Terms
```
GET /api/cross_language/terms
```
Provides comparison of theological terms across different language translations.

Web App Route:
```
GET /cross_language
```

## Semantic Search Endpoints

### Vector Search
```
GET /api/vector-search
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| q | string | (required) | The search query text |
| translation | string | "KJV" | Translation to search (KJV, ASV, TAHOT, TAGNT) |
| limit | integer | 10 | Maximum number of results |

**Example Response:**

```json
[
  {
    "book_name": "Genesis",
    "chapter_num": 1,
    "verse_num": 1,
    "verse_text": "In the beginning God created the heaven and the earth.",
    "similarity": 0.92
  }
]
```

### Similar Verses
```
GET /api/similar-verses
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| book | string | (required) | Book name |
| chapter | integer | (required) | Chapter number |
| verse | integer | (required) | Verse number |
| translation | string | "KJV" | Translation to search |
| limit | integer | 10 | Maximum number of results |

### Compare Translations
```
GET /api/compare-translations
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| book | string | (required) | Book name |
| chapter | integer | (required) | Chapter number |
| verse | integer | (required) | Verse number |
| source_translation | string | "KJV" | Source translation |
| target_translations | string | "ASV,TAHOT,TAGNT" | Comma-separated list of target translations |

## Comprehensive Search API

The Comprehensive Search API enables powerful semantic search across all database resources, including verses, lexicons, proper names, and cross-language mappings.

### Base URL

All Comprehensive Search API endpoints are prefixed with:
```
/api/comprehensive
```

### Endpoints

#### Vector Search

```
GET /api/comprehensive/vector-search
```

Performs semantic vector search across multiple translations with rich contextual data.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| q | string | (required) | The search query text |
| translation | string | "KJV" | Primary translation to search (KJV, ASV, TAHOT, TAGNT) |
| include_lexicon | boolean | true | Include lexical data for words |
| include_related | boolean | true | Include related terms |
| include_names | boolean | true | Include proper name data |
| cross_language | boolean | false | Search across language boundaries |
| limit | integer | 10 | Maximum number of results (max: 50) |

**Example Response:**

```json
{
  "query": "God created",
  "translation": "KJV",
  "cross_language": true,
  "results": [
    {
      "reference": "Genesis 1:1",
      "text": "In the beginning God created the heaven and the earth.",
      "translation": "KJV",
      "similarity": 97.56,
      "lexical_data": [
        {
          "word": "created",
          "position": 4,
          "strongs_id": "H1254",
          "grammar": "Qal",
          "lemma": "בָּרָא",
          "definition": "to create"
        }
      ]
    },
    {
      "reference": "בראשית 1:1",
      "text": "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃",
      "translation": "TAHOT",
      "similarity": 92.34,
      "cross_language": true
    }
  ]
}
```

#### Theological Term Search

```
GET /api/comprehensive/theological-term-search
```

Searches for theological terms across translations and finds occurrences with context.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| term | string | (required) | Theological term to search |
| language | string | "english" | Term language (hebrew, greek, english, arabic) |
| include_equivalent | boolean | true | Include equivalent terms in other languages |
| limit | integer | 10 | Maximum number of results (max: 50) |

**Example Response:**

```json
{
  "term": "elohim",
  "language": "hebrew",
  "term_info": [
    {
      "hebrew_term": "אלהים",
      "greek_term": "θεός",
      "english_term": "God",
      "strongs_id": "H430",
      "theological_category": "deity"
    }
  ],
  "verses": [
    {
      "reference": "Genesis 1:1",
      "text": "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃",
      "translation": "TAHOT",
      "term_info": {
        "word": "אֱלֹהִ֑ים",
        "strongs_id": "H430",
        "lemma": "אֱלֹהִים",
        "definition": "God, gods"
      }
    }
  ],
  "count": 1
}
```

#### Name Search

```
GET /api/comprehensive/name-search
```

Searches for biblical proper names and their relationships.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| name | string | (required) | Proper name to search |
| include_relationships | boolean | true | Include related names |
| relationship_type | string | "" | Filter by relationship type |
| limit | integer | 20 | Maximum number of results (max: 50) |

**Example Response:**

```json
{
  "query": "Moses",
  "count": 1,
  "results": {
    "names": [
      {
        "name": "Moses",
        "hebrew": "מֹשֶׁה",
        "transliteration": "mōšeh",
        "description": "Hebrew prophet and lawgiver",
        "occurrences": 847
      }
    ],
    "relationships": [
      {
        "name1": "Moses",
        "name2": "Aaron",
        "relationship_type": "brother"
      },
      {
        "name1": "Moses",
        "name2": "Pharaoh",
        "relationship_type": "confrontation"
      }
    ]
  }
}
```

## Additional API Endpoints
```
API /api/verse/names
```
Needs documentation.


```
API /api/vector-search-with-lexicon
```
Needs documentation.


```
API /api/vector-search
```
Needs documentation.


```
API /api/theological_terms_report
```
Needs documentation.


```
API /api/tagged/verse
```
Needs documentation.


```
API /api/tagged/search
```
Needs documentation.


```
API /api/similar-verses
```
Needs documentation.


```
API /api/resources/translations
```
Needs documentation.


```
API /api/resources/manuscripts
```
Needs documentation.


```
API /api/resources/commentaries
```
Needs documentation.


```
API /api/resources/archaeology
```
Needs documentation.


```
API /api/resources
```
Needs documentation.


```
API /api/names/search
```
Needs documentation.


```
API /api/names
```
Needs documentation.


```
API /api/morphology/hebrew
```
Needs documentation.


```
API /api/morphology/greek
```
Needs documentation.


```
API /api/lexicon/stats
```
Needs documentation.


```
API /api/lexicon/search
```
Needs documentation.


```
API /api/lexicon/hebrew/validate_critical_terms
```
Needs documentation.


```
API /api/dspy/ask_with_context
```
Needs documentation.


```
API /api/cross_language/terms
```
Needs documentation.


```
API /api/cross-language-search
```
Needs documentation.


```
API /api/compare-translations
```
Needs documentation.



### Lexicon API

Provides access to lexicon data from `bible.hebrew_entries` and `bible.greek_entries`.

### Endpoints
- **GET /api/lexicon/stats**: Returns row counts for `hebrew_entries` and `greek_entries`.
  - Response: `{ "status": "success", "stats": { "hebrew_entries": 9360, "greek_entries": 10847 } }`
- **GET /api/lexicon/search?strongs_id=<id>**: Searches for a lexicon entry by Strong's ID.
  - Example: `/api/lexicon/search?strongs_id=H430`
  - Response: `{ "status": "success", "entry": { "strongs_id": "H430", "lemma": "אֱלֹהִים", "transliteration": "Elohim", "definition": "God" } }`

### Tagged Text API

```
GET /api/tagged/verse
```
Returns a verse with tagged words.

```
GET /api/tagged/search
```
Searches for tagged words in the text.

### Morphology API

```
GET /api/morphology/hebrew
```
Returns Hebrew morphology code explanations.

```
GET /api/morphology/greek
```
Returns Greek morphology code explanations.

### Proper Names API

```
GET /api/names
```
Returns a list of biblical proper names.

```
GET /api/names/search
```
Searches for proper names.

```
GET /api/verse/names
```
Returns proper names mentioned in a specific verse.

### Resources API

```
GET /api/resources/commentaries
```
Returns commentaries related to biblical texts.

```
GET /api/resources/archaeology
```
Returns archaeological data related to biblical texts.

```
GET /api/resources/manuscripts
```
Returns information about biblical manuscripts.

```
GET /api/resources/translations
```
Returns information about Bible translations.

### DSPy API

The DSPy API provides endpoints for Bible question answering with enhanced DSPy 2.6 features including multi-turn conversation history.

### Base URL

```
/api/dspy
```

### Health Check

```http
GET /api/dspy/health
```

Returns the status of the DSPy API and model.

**Response**

```json
{
  "status": "ok",
  "message": "DSPy API is running with model loaded",
  "version": "2.0.0",
  "dspy_version": "2.6.23"
}
```

### Ask a Question

```http
POST /api/dspy/ask
Content-Type: application/json
```

Ask a question without providing specific Bible context.

**Request Body**

```json
{
  "question": "Who was Moses?",
  "session_id": "optional-session-id-for-conversation-history"
}
```

**Response**

```json
{
  "question": "Who was Moses?",
  "answer": "Moses was a prophet and leader in the Old Testament who led the Israelites out of slavery in Egypt. He is known for receiving the Ten Commandments from God on Mount Sinai and for writing the first five books of the Bible, known as the Pentateuch or Torah.",
  "session_id": "user-123",
  "history_length": 1
}
```

### Ask with Context

```http
POST /api/dspy/ask_with_context
Content-Type: application/json
```

Ask a question with specific Bible context.

**Request Body**

```json
{
  "question": "What did Moses do?",
  "context": "Moses led the Israelites out of Egypt across the Red Sea.",
  "session_id": "optional-session-id-for-conversation-history"
}
```

**Response**

```json
{
  "question": "What did Moses do?",
  "answer": "According to the context, Moses led the Israelites out of Egypt across the Red Sea.",
  "context": "Moses led the Israelites out of Egypt across the Red Sea.",
  "session_id": "user-123",
  "history_length": 2
}
```

### Get Conversation History

```http
GET /api/dspy/conversation?session_id=user-123
```

Get the conversation history for a session.

**Response**

```json
{
  "session_id": "user-123",
  "conversation": [
    {
      "role": "user",
      "content": "Who was Moses?",
      "turn": 1
    },
    {
      "role": "assistant",
      "content": "Moses was a prophet and leader in the Old Testament who led the Israelites out of slavery in Egypt. He is known for receiving the Ten Commandments from God on Mount Sinai and for writing the first five books of the Bible, known as the Pentateuch or Torah.",
      "turn": 2
    },
    {
      "role": "user",
      "content": "What did Moses do?",
      "turn": 3
    },
    {
      "role": "assistant",
      "content": "According to the context, Moses led the Israelites out of Egypt across the Red Sea.",
      "turn": 4
    }
  ],
  "turns": 2
}
```

### Clear Conversation History

```http
DELETE /api/dspy/conversation?session_id=user-123
```

Clear the conversation history for a session.

**Response**

```json
{
  "status": "ok",
  "message": "Conversation history cleared for session user-123"
}
```

### Bible QA API

```
POST /api/question
```
Answers Bible questions using the trained DSPy model, optionally using Claude API when configured.

**Request:**
```json
{
  "question": "Who created the heavens and the earth?",
  "context": "In the beginning God created the heaven and the earth.",
  "model_version": "latest"
}
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| question | string | (required) | The Bible question to answer |
| context | string | "" | Optional biblical context to improve answer |
| model_version | string | "latest" | Version of the model to use |

**Response:**
```json
{
  "answer": "God created the heavens and the earth.",
  "model_info": {
    "model_type": "T5 Bible QA",
    "model_path": "models/dspy/bible_qa_t5/bible_qa_t5_latest"
  },
  "status": "success"
}
```

### Optimized Bible QA API

```
POST /api/bible_qa/question
```
Answers Bible questions using the optimized Bible QA model trained with non-synthetic Bible trivia data, providing more accurate and concise answers with proper scripture references.

**Request:**
```json
{
  "question": "Who was the first person to see Jesus after his resurrection?",
  "context": ""
}
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| question | string | (required) | The Bible question to answer |
| context | string | "" | Optional biblical context to improve answer |

**Response:**
```json
{
  "status": "success",
  "answer": "Mary Magdalene (John 20:1-18)",
  "model_info": {
    "model_type": "Bible QA (Optimized with Non-Synthetic Data)",
    "response_time": "1.23s"
  }
}
```

```
GET /api/bible_qa/status
```
Checks if the optimized Bible QA model is loaded and available.

**Response:**
```json
{
  "status": "OK",
  "model_loaded": true
}
```

```
GET /api/models
```
```

## Contextual Insights API

The Contextual Insights API provides rich, multi-faceted insights for Bible verses, topics, or text snippets using direct LM Studio chat completions via `query_lm_studio` in `contextual_insights_minimal.py`.

### Base URL
```
http://localhost:5000/api/contextual_insights
```

### Health Check

```
GET /api/contextual_insights/health
```
Checks if the Contextual Insights API is running and accessible.

**Response:**
```json
{
  "status": "ok"
}
```

### Generate Insights

```
POST /api/contextual_insights/insights
```
Generates comprehensive insights for a Bible verse, topic, or text snippet.

**Request Parameters:**

The endpoint accepts three types of requests based on the `type` field:

**1. Verse Focus:**

```json
{
  "type": "verse",
  "reference": "John 3:16",
  "translation": "KJV"
}
```

**2. Topic Focus:**

```json
{
  "type": "topic",
  "query_text": "Sermon on the Mount"
}
```

**3. Text Snippet Focus:**

```json
{
  "type": "text_snippet",
  "text": "Blessed are the poor in spirit, for theirs is the kingdom of heaven."
}
```

**Response:**
```json
{
  "input": {
    "type": "verse",
    "reference": "John 3:16",
    "translation": "KJV"
  },
  "insights": {
    "summary": "John 3:16 teaches that God's love led Him to send His Son, Jesus Christ, so that whoever believes in Him may not perish but have eternal life. This verse emphasizes the concept of salvation through faith in Jesus and highlights the depth of God's love for humanity.",
    "theological_terms": {
      "Grace": "Unmerited favor shown by God to sinners",
      "Salvation": "Deliverance from sin and its consequences through faith in Christ",
      "Eternal Life": "A quality of life that begins at salvation and continues forever"
    },
    "cross_references": [{"reference": "John 1:29", "text": "Behold the Lamb of God who takes away the sin of the world!", "reason": "Introduces Jesus as the sacrifice for sins."}],
    "historical_context": "The Gospel of John was written around 90-110 AD...",
    "original_language_notes": [{"word": "παῖς", "strongs_id": "G5207", "meaning": "Son; used here in reference to Jesus as the Son of God."}],
    "related_entities": {"people": [{"name": "Jesus Christ", "description": "The central figure of Christianity, believed to be the Son of God and Savior of humanity"}], "places": []},
    "translation_variants": [...],
    "lexical_data": [
      {
        "word": "ἀγάπη",
        "strongs_id": "G26",
        "lemma": "ἀγάπη",
        "transliteration": "agapē",
        "definition": "Self-sacrificial love"
      }
    ]
  },
  "processing_time_seconds": 7.38
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| summary | string | 2-3 sentence summary from primary sources |
| theological_terms | object | Dictionary of theological terms and definitions |
| cross_references | array | Array of cross-reference objects with keys `reference`, `text`, `reason` |
| historical_context | string | Historical context from primary and pre-1990 commentaries |
| original_language_notes | array | Array of language notes objects with keys `word`, `strongs_id`, `meaning` |
| related_entities | object | Object containing `people` (array) and `places` (array) |
| translation_variants | array | List of translation variants from the database with `translation`, `text`, and `notes` |
| lexical_data | array | List of lexical entries for words in the verse, each containing `word` (original text), `strongs_id`, `lemma`, `transliteration`, and `definition`. |

**Error Responses:**

Missing or invalid input:
```json
{
  "error": "No JSON data provided"
}
```
Invalid focus type:
```json
{
  "error": "Invalid focus type"
}
```
Missing required fields:
```json
{
  "error": "No verse reference provided"
}
```

### Web Interface

You can also access Contextual Insights via a web UI at `/insights`, which renders `lexical_data` in a table format alongside summaries, theological terms, and other insights.

## Modification History

| Date | Change | Author |
|------|--------|--------|
| 2025-05-12 | Added lexical_data field to Contextual Insights API | BibleScholar Team |
| 2025-05-12 | Added web UI integration to display lexical_data | BibleScholar Team |
| 2025-05-10 | Added Optimized Bible QA API endpoints | BibleScholar Team |
| 2025-05-06 | Moved to reference directory and updated cross-references | BibleScholar Team |
| 2025-05-01 | Added semantic search endpoints | BibleScholar Team |
| 2025-04-15 | Added comprehensive search API documentation | BibleScholar Team |
| 2025-03-20 | Added theological terms endpoints | BibleScholar Team |
| 2025-02-10 | Initial API documentation | BibleScholar Team |
| 2025-05-12 | Added Lexicon API with /stats and /search endpoints | BibleScholar Team |

> **NOTE (2025-05): All API endpoints (including contextual insights) are now served from the unified Flask app on port 5000. Do not use port 5002. Use API_BASE_URL (http://localhost:5000) for all API calls.**

## Endpoints

### /vector-search
- Returns most similar verses for a query and translation.
- Example:
  ```bash
  curl "http://localhost:5000/api/vector-search?q=faith&translation=KJV&limit=5"
  ```
- Response: JSON with `verse_id`, `book_name`, `chapter_num`, `verse_num`, `similarity`.

### /similar-verses
- Returns verses similar to a reference verse.
- Example:
  ```bash
  curl "http://localhost:5000/api/similar-verses?reference=John 3:16&translation=KJV&limit=5"
  ```
- Response: JSON with similar fields as above.

### /compare-translations
- Compares semantic similarity of a verse across translations.
- Example:
  ```bash
  curl "http://localhost:5000/api/compare-translations?reference=John 3:16"
  ```
- Response: JSON with similarity scores per translation.

## Supported Translations
- KJV, ASV, TAHOT, YLT

## Validation
- Ensure embeddings are present:
  ```bash
  psql -U postgres -d bible_db -c "SELECT translation_source, COUNT(*) FROM bible.verse_embeddings GROUP BY translation_source;"
  ```
  - Expect ~31k rows per translation.

## Updates (2025-05-19)
- Documented endpoints and validation steps.
- Clarified translation support.

# API Reference: Study Dashboard

## /api/search
- **Method:** GET
- **Parameters:**
  - `q` (string): Query string (verse, word, or lexicon)
  - `type` (string): 'verse', 'word', or 'lexicon'
  - `lang` (string, optional): For `lexicon` and `word` searches, specify 'hebrew', 'greek', or 'both' (default: 'both').
- **Example:**
  ```http
  GET /api/search?q=John%203:16&type=verse
  ```
- **Response:**
  ```json
  { "verses": [ { "book_name": "John", "chapter_num": 3, "verse_num": 16, "verse_text": "For God so loved...", "translation_source": "KJV" } ] }
  ```
- **Errors:**
  - 400: Missing parameters
  - 500: Database error

## /api/dspy/ask_with_context
- **Method:** POST
- **Body:**
  ```json
  { "question": "Explain John 3:16" }
  ```
- **Response:**
  ```json
  { "answer": "This verse means..." }
  ```
- **Errors:**
  - 503: AI unavailable
  - 500: Server error

## /api/dspy/conversation
- **Method:** GET, DELETE
- **Parameters:**
  - `session_id` (optional): Session identifier
- **Response:**
  ```json
  { "session_id": "...", "conversation": [ ... ], "turns": 2 }
  ```
- **Errors:**
  - 500: Server error

