#!/usr/bin/env python3
"""
Enhanced Contextual Insights API with Advanced Biblical Analysis
Provides high-quality, scholarly insights using sophisticated prompt engineering
and comprehensive data integration techniques.

Key Improvements:
- Advanced prompt engineering with role-based analysis
- Multi-stage analysis pipeline
- Enhanced theological depth and scholarly rigor
- Better cross-reference analysis and thematic connections
- Improved original language analysis
- Structured output with confidence scoring
"""
from flask import Blueprint, request, jsonify
import requests
import time
import os
import sys
import json
import psycopg
from psycopg.rows import dict_row
from colorama import Fore, init
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from BibleScholarLangChain.scripts.db_config import get_lm_studio_config, get_database_url
from BibleScholarLangChain.src.utils.bible_reference_parser import normalize_book_name_to_db

init(autoreset=True)
enhanced_insights_bp = Blueprint('enhanced_insights', __name__)

class AnalysisType(Enum):
    VERSE_SPECIFIC = "verse_specific"
    THEMATIC = "thematic"
    THEOLOGICAL = "theological"
    LEXICAL = "lexical"
    HISTORICAL = "historical"

@dataclass
class AnalysisContext:
    """Structured context for analysis"""
    query: str
    analysis_type: AnalysisType
    verses_data: List[Dict]
    strongs_data: List[Dict]
    morphology_data: List[Dict]
    cross_refs_data: List[Dict]
    semantic_verses: List[Dict]
    translation_analysis: Optional[Dict] = None
    confidence_score: float = 0.0

class EnhancedBibleAnalyzer:
    """Enhanced Bible analysis with sophisticated prompt engineering"""
    
    def __init__(self):
        config = get_lm_studio_config()
        self.base_url = config['base_url']
        self.chat_model = config['models']['chat']
        self.embedding_model = config['models']['embeddings']
        self.timeout = config['timeout']
        self.chat_url = f"{self.base_url}/chat/completions"
        self.embeddings_url = f"{self.base_url}/embeddings"
        self.available_translations = ['KJV', 'ASV', 'YLT', 'TAHOT']
        
        # Enhanced prompt templates
        self.prompt_templates = self._load_prompt_templates()
        
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load sophisticated prompt templates for different analysis types"""
        return {
            "scholar_role": """You are Dr. Sarah Cohen, a distinguished professor of Biblical Studies at Oxford University with 25 years of experience in:
- Hebrew and Greek exegesis
- Ancient Near Eastern history and culture
- Biblical theology and systematic theology
- Textual criticism and manuscript analysis
- Cross-cultural biblical interpretation

Your expertise includes:
- Deep knowledge of original languages (Hebrew, Aramaic, Greek)
- Understanding of ancient cultural contexts
- Mastery of theological traditions and interpretations
- Ability to connect biblical themes across testaments
- Scholarly analysis of biblical texts with academic rigor

You must provide insights that are:
1. Academically rigorous and well-reasoned
2. Grounded in the provided biblical data
3. Respectful of multiple theological perspectives
4. Rich in historical and cultural context
5. Theologically sound and biblically faithful""",

            "verse_analysis": """ANALYZE THIS BIBLICAL VERSE/REFERENCE:

{query}

AVAILABLE TRANSLATIONS (USE ONLY THESE):
{translations}

ORIGINAL LANGUAGE DATA:
{original_language}

GRAMMATICAL ANALYSIS:
{morphology}

CROSS-REFERENCES:
{cross_references}

SEMANTIC CONNECTIONS:
{semantic_connections}

Provide a comprehensive analysis that includes:

1. **LITERAL MEANING**: What does the text say in its most basic form?
2. **ORIGINAL LANGUAGE INSIGHTS**: How do the Hebrew/Greek words enhance understanding?
3. **GRAMMATICAL SIGNIFICANCE**: What grammatical features are important?
4. **HISTORICAL CONTEXT**: What historical/cultural background is relevant?
5. **THEOLOGICAL IMPLICATIONS**: What theological truths are revealed?
6. **CROSS-REFERENCE CONNECTIONS**: How does this connect to other biblical passages?
7. **PRACTICAL APPLICATION**: How does this apply to Christian life today?

Format your response with clear sections and scholarly depth.""",

            "thematic_analysis": """ANALYZE THIS BIBLICAL THEME/TOPIC:

{query}

RELEVANT VERSES:
{verses}

LEXICAL DATA:
{lexical_data}

THEMATIC CONNECTIONS:
{thematic_connections}

Provide a comprehensive thematic analysis that includes:

1. **THEME DEFINITION**: What is the core concept being explored?
2. **BIBLICAL DEVELOPMENT**: How does this theme develop throughout Scripture?
3. **ORIGINAL LANGUAGE ROOTS**: What do the key terms mean in Hebrew/Greek?
4. **THEOLOGICAL SIGNIFICANCE**: What theological truths does this theme reveal?
5. **HISTORICAL PROGRESSION**: How does this theme evolve across biblical history?
6. **PRACTICAL IMPLICATIONS**: How should this theme influence Christian living?
7. **CONTEMPORARY RELEVANCE**: How does this theme speak to modern believers?

Provide scholarly depth with specific biblical references.""",

            "theological_analysis": """CONDUCT A THEOLOGICAL ANALYSIS OF:

{query}

BIBLICAL DATA:
{biblical_data}

THEOLOGICAL TERMS:
{theological_terms}

SYSTEMATIC CONNECTIONS:
{systematic_connections}

Provide a comprehensive theological analysis that includes:

1. **DOCTRINAL FOUNDATION**: What theological doctrines are supported?
2. **BIBLICAL EVIDENCE**: What specific texts support these conclusions?
3. **ORTHODOX INTERPRETATION**: How does this align with historic Christian teaching?
4. **DENOMINATIONAL PERSPECTIVES**: What different theological traditions say
5. **PRACTICAL THEOLOGY**: How does this doctrine apply to Christian practice?
6. **CONTEMPORARY CHALLENGES**: How does this address modern theological questions?
7. **PASTORAL IMPLICATIONS**: How should this inform pastoral ministry?

Maintain theological accuracy and scholarly rigor.""",

            "lexical_analysis": """CONDUCT A LEXICAL ANALYSIS OF:

{query}

STRONG'S DATA:
{strongs_data}

MORPHOLOGICAL DATA:
{morphology_data}

USAGE PATTERNS:
{usage_patterns}

Provide a comprehensive lexical analysis that includes:

1. **ETYMOLOGY**: What are the linguistic roots and development?
2. **SEMANTIC RANGE**: What is the full range of meanings?
3. **GRAMMATICAL USAGE**: How is this word used grammatically?
4. **BIBLICAL FREQUENCY**: How often and where does this word appear?
5. **THEOLOGICAL SIGNIFICANCE**: What theological weight does this word carry?
6. **TRANSLATION CHALLENGES**: What translation issues arise?
7. **EXEGETICAL IMPLICATIONS**: How does this affect interpretation?

Provide detailed linguistic analysis with biblical examples."""
        }

    def get_db_connection(self):
        """Get database connection"""
        conn_str = get_database_url()
        return psycopg.connect(conn_str, row_factory=dict_row)

    def determine_analysis_type(self, query: str) -> AnalysisType:
        """Determine the type of analysis needed based on the query"""
        query_lower = query.lower()
        
        # Check for verse references
        verse_pattern = r'(\d*\s*\w+)\s+(\d+):(\d+)'
        if re.search(verse_pattern, query):
            return AnalysisType.VERSE_SPECIFIC
        
        # Check for theological terms
        theological_terms = ['god', 'jesus', 'christ', 'holy spirit', 'trinity', 'salvation', 
                           'grace', 'faith', 'sin', 'redemption', 'atonement', 'justification']
        if any(term in query_lower for term in theological_terms):
            return AnalysisType.THEOLOGICAL
        
        # Check for lexical/word study queries
        lexical_indicators = ['meaning of', 'definition of', 'hebrew word', 'greek word', 
                             'strong\'s', 'lexical', 'word study']
        if any(indicator in query_lower for indicator in lexical_indicators):
            return AnalysisType.LEXICAL
        
        # Check for historical/cultural queries
        historical_indicators = ['when', 'where', 'who', 'history', 'culture', 'background', 
                               'context', 'ancient', 'biblical times']
        if any(indicator in query_lower for indicator in historical_indicators):
            return AnalysisType.HISTORICAL
        
        # Default to thematic analysis
        return AnalysisType.THEMATIC

    def create_enhanced_prompt(self, context: AnalysisContext) -> str:
        """Create a sophisticated prompt based on analysis type and context"""
        
        # Start with scholar role
        prompt = self.prompt_templates["scholar_role"] + "\n\n"
        
        # Add analysis-specific prompt
        if context.analysis_type == AnalysisType.VERSE_SPECIFIC:
            prompt += self._create_verse_analysis_prompt(context)
        elif context.analysis_type == AnalysisType.THEMATIC:
            prompt += self._create_thematic_analysis_prompt(context)
        elif context.analysis_type == AnalysisType.THEOLOGICAL:
            prompt += self._create_theological_analysis_prompt(context)
        elif context.analysis_type == AnalysisType.LEXICAL:
            prompt += self._create_lexical_analysis_prompt(context)
        else:
            prompt += self._create_thematic_analysis_prompt(context)
        
        return prompt

    def _create_verse_analysis_prompt(self, context: AnalysisContext) -> str:
        """Create verse-specific analysis prompt"""
        translations = self._format_translations(context.verses_data)
        original_language = self._format_original_language(context.strongs_data)
        morphology = self._format_morphology(context.morphology_data)
        cross_references = self._format_cross_references(context.cross_refs_data)
        semantic_connections = self._format_semantic_connections(context.semantic_verses)
        
        return self.prompt_templates["verse_analysis"].format(
            query=context.query,
            translations=translations,
            original_language=original_language,
            morphology=morphology,
            cross_references=cross_references,
            semantic_connections=semantic_connections
        )

    def _create_thematic_analysis_prompt(self, context: AnalysisContext) -> str:
        """Create thematic analysis prompt"""
        verses = self._format_verses(context.verses_data)
        lexical_data = self._format_lexical_data(context.strongs_data)
        thematic_connections = self._format_thematic_connections(context.cross_refs_data, context.semantic_verses)
        
        return self.prompt_templates["thematic_analysis"].format(
            query=context.query,
            verses=verses,
            lexical_data=lexical_data,
            thematic_connections=thematic_connections
        )

    def _create_theological_analysis_prompt(self, context: AnalysisContext) -> str:
        """Create theological analysis prompt"""
        biblical_data = self._format_biblical_data(context.verses_data, context.strongs_data)
        theological_terms = self._extract_theological_terms(context.query, context.strongs_data)
        systematic_connections = self._format_systematic_connections(context.cross_refs_data)
        
        return self.prompt_templates["theological_analysis"].format(
            query=context.query,
            biblical_data=biblical_data,
            theological_terms=theological_terms,
            systematic_connections=systematic_connections
        )

    def _create_lexical_analysis_prompt(self, context: AnalysisContext) -> str:
        """Create lexical analysis prompt"""
        strongs_data = self._format_strongs_data(context.strongs_data)
        morphology_data = self._format_morphology_data(context.morphology_data)
        usage_patterns = self._format_usage_patterns(context.verses_data, context.strongs_data)
        
        return self.prompt_templates["lexical_analysis"].format(
            query=context.query,
            strongs_data=strongs_data,
            morphology_data=morphology_data,
            usage_patterns=usage_patterns
        )

    def _format_translations(self, verses_data: List[Dict]) -> str:
        """Format translation data for prompt"""
        if not verses_data:
            return "No translation data available."
        
        formatted = []
        for verse in verses_data[:5]:  # Limit for readability
            formatted.append(f"• {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']} ({verse['translation_source']}): {verse['text']}")
        
        return "\n".join(formatted)

    def _format_original_language(self, strongs_data: List[Dict]) -> str:
        """Format original language data for prompt"""
        if not strongs_data:
            return "No original language data available."
        
        formatted = []
        for word in strongs_data[:8]:  # Limit for readability
            word_text = word.get('word_text', word.get('gloss', 'N/A'))
            lemma = word.get('lemma', 'N/A')
            definition = word.get('definition', 'N/A')
            strongs_id = word.get('strongs_id', 'N/A')
            language = word.get('language', 'Unknown')
            formatted.append(f"• {word_text} ({strongs_id}, {language}): {lemma} - {definition}")
        
        return "\n".join(formatted)

    def _format_morphology(self, morphology_data: List[Dict]) -> str:
        """Format morphological data for prompt"""
        if not morphology_data:
            return "No morphological data available."
        
        formatted = []
        for morph in morphology_data[:6]:  # Limit for readability
            word_text = morph.get('word_text', 'N/A')
            grammar_code = morph.get('grammar_code', 'N/A')
            gloss = morph.get('gloss', 'N/A')
            language = morph.get('language', 'Unknown')
            formatted.append(f"• {word_text} ({language}) [{grammar_code}]: {gloss}")
        
        return "\n".join(formatted)

    def _format_cross_references(self, cross_refs_data: List[Dict]) -> str:
        """Format cross-references for prompt"""
        if not cross_refs_data:
            return "No cross-references available."
        
        formatted = []
        for ref in cross_refs_data[:5]:  # Limit for readability
            formatted.append(f"• {ref['book_name']} {ref['chapter_num']}:{ref['verse_num']}: {ref['text'][:100]}...")
        
        return "\n".join(formatted)

    def _format_semantic_connections(self, semantic_verses: List[Dict]) -> str:
        """Format semantic connections for prompt"""
        if not semantic_verses:
            return "No semantic connections available."
        
        formatted = []
        for verse in semantic_verses[:3]:  # Limit for readability
            formatted.append(f"• {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']}: {verse['text'][:100]}...")
        
        return "\n".join(formatted)

    def _format_verses(self, verses_data: List[Dict]) -> str:
        """Format verses for thematic analysis"""
        if not verses_data:
            return "No verses available."
        
        formatted = []
        for verse in verses_data[:8]:  # Limit for readability
            formatted.append(f"• {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']} ({verse['translation_source']}): {verse['text']}")
        
        return "\n".join(formatted)

    def _format_lexical_data(self, strongs_data: List[Dict]) -> str:
        """Format lexical data for thematic analysis"""
        if not strongs_data:
            return "No lexical data available."
        
        formatted = []
        for word in strongs_data[:6]:  # Limit for readability
            word_text = word.get('word_text', word.get('gloss', 'N/A'))
            definition = word.get('definition', 'N/A')
            language = word.get('language', 'Unknown')
            formatted.append(f"• {word_text} ({language}): {definition}")
        
        return "\n".join(formatted)

    def _format_thematic_connections(self, cross_refs_data: List[Dict], semantic_verses: List[Dict]) -> str:
        """Format thematic connections"""
        connections = []
        
        # Add cross-references
        for ref in cross_refs_data[:3]:
            connections.append(f"• Cross-reference: {ref['book_name']} {ref['chapter_num']}:{ref['verse_num']}")
        
        # Add semantic connections
        for verse in semantic_verses[:3]:
            connections.append(f"• Semantic: {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']}")
        
        return "\n".join(connections) if connections else "No thematic connections available."

    def _format_biblical_data(self, verses_data: List[Dict], strongs_data: List[Dict]) -> str:
        """Format biblical data for theological analysis"""
        formatted = []
        
        # Add verses
        for verse in verses_data[:5]:
            formatted.append(f"• {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']}: {verse['text']}")
        
        # Add key terms
        for word in strongs_data[:3]:
            word_text = word.get('word_text', word.get('gloss', 'N/A'))
            definition = word.get('definition', 'N/A')
            formatted.append(f"• Key term: {word_text} - {definition}")
        
        return "\n".join(formatted)

    def _extract_theological_terms(self, query: str, strongs_data: List[Dict]) -> str:
        """Extract theological terms from query and data"""
        terms = []
        
        # Extract from query
        theological_keywords = ['god', 'jesus', 'christ', 'holy spirit', 'salvation', 'grace', 'faith', 'sin']
        query_lower = query.lower()
        for keyword in theological_keywords:
            if keyword in query_lower:
                terms.append(f"• {keyword.title()}: Central theological concept")
        
        # Extract from Strong's data
        for word in strongs_data[:3]:
            word_text = word.get('word_text', word.get('gloss', 'N/A'))
            definition = word.get('definition', 'N/A')
            terms.append(f"• {word_text}: {definition}")
        
        return "\n".join(terms) if terms else "No specific theological terms identified."

    def _format_systematic_connections(self, cross_refs_data: List[Dict]) -> str:
        """Format systematic theological connections"""
        if not cross_refs_data:
            return "No systematic connections available."
        
        formatted = []
        for ref in cross_refs_data[:4]:
            formatted.append(f"• {ref['book_name']} {ref['chapter_num']}:{ref['verse_num']}: Related theological concept")
        
        return "\n".join(formatted)

    def _format_strongs_data(self, strongs_data: List[Dict]) -> str:
        """Format Strong's data for lexical analysis"""
        if not strongs_data:
            return "No Strong's data available."
        
        formatted = []
        for word in strongs_data[:6]:
            word_text = word.get('word_text', word.get('gloss', 'N/A'))
            lemma = word.get('lemma', 'N/A')
            definition = word.get('definition', 'N/A')
            strongs_id = word.get('strongs_id', 'N/A')
            language = word.get('language', 'Unknown')
            formatted.append(f"• {word_text} ({strongs_id}, {language}): {lemma} - {definition}")
        
        return "\n".join(formatted)

    def _format_morphology_data(self, morphology_data: List[Dict]) -> str:
        """Format morphology data for lexical analysis"""
        if not morphology_data:
            return "No morphology data available."
        
        formatted = []
        for morph in morphology_data[:6]:
            word_text = morph.get('word_text', 'N/A')
            grammar_code = morph.get('grammar_code', 'N/A')
            gloss = morph.get('gloss', 'N/A')
            language = morph.get('language', 'Unknown')
            formatted.append(f"• {word_text} ({language}) [{grammar_code}]: {gloss}")
        
        return "\n".join(formatted)

    def _format_usage_patterns(self, verses_data: List[Dict], strongs_data: List[Dict]) -> str:
        """Format usage patterns for lexical analysis"""
        if not verses_data:
            return "No usage patterns available."
        
        formatted = []
        for verse in verses_data[:4]:
            formatted.append(f"• {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']}: Usage example")
        
        return "\n".join(formatted)

    def generate_enhanced_analysis(self, context: AnalysisContext) -> Dict[str, Any]:
        """Generate enhanced analysis using sophisticated prompt engineering"""
        try:
            start_time = time.time()
            
            # Create enhanced prompt
            prompt = self.create_enhanced_prompt(context)
            
            # Generate response using LM Studio
            response = requests.post(
                self.chat_url,
                json={
                    "model": self.chat_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 8192,
                    "temperature": 0.3,  # Lower temperature for more consistent quality
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                analysis_text = response.json()["choices"][0]["message"]["content"]
                
                # Calculate confidence score based on data quality
                confidence_score = self._calculate_confidence_score(context)
                
                # Structure the response
                structured_response = {
                    "analysis_type": context.analysis_type.value,
                    "confidence_score": confidence_score,
                    "processing_time": round(time.time() - start_time, 2),
                    "comprehensive_analysis": analysis_text,
                    "data_sources_used": self._get_data_sources_summary(context),
                    "recommendations": self._generate_recommendations(context)
                }
                
                return structured_response
            else:
                return {
                    "error": f"LM Studio error: {response.status_code}",
                    "analysis_type": context.analysis_type.value,
                    "confidence_score": 0.0
                }
                
        except Exception as e:
            return {
                "error": f"Analysis generation error: {str(e)}",
                "analysis_type": context.analysis_type.value,
                "confidence_score": 0.0
            }

    def _calculate_confidence_score(self, context: AnalysisContext) -> float:
        """Calculate confidence score based on data quality and quantity"""
        score = 0.0
        
        # Base score for having any data
        if context.verses_data:
            score += 0.2
        
        # Strong's data quality
        if context.strongs_data:
            score += 0.2
            if len(context.strongs_data) > 3:
                score += 0.1
        
        # Morphology data quality
        if context.morphology_data:
            score += 0.15
            if len(context.morphology_data) > 2:
                score += 0.05
        
        # Cross-references quality
        if context.cross_refs_data:
            score += 0.15
            if len(context.cross_refs_data) > 3:
                score += 0.05
        
        # Semantic connections quality
        if context.semantic_verses:
            score += 0.1
            if len(context.semantic_verses) > 2:
                score += 0.05
        
        # Translation variety
        translations = set(verse.get('translation_source', '') for verse in context.verses_data)
        if len(translations) > 1:
            score += 0.1
        
        return min(score, 1.0)

    def _get_data_sources_summary(self, context: AnalysisContext) -> Dict[str, Any]:
        """Get summary of data sources used"""
        return {
            "verses_count": len(context.verses_data),
            "strongs_entries": len(context.strongs_data),
            "morphology_entries": len(context.morphology_data),
            "cross_references": len(context.cross_refs_data),
            "semantic_matches": len(context.semantic_verses),
            "translations_used": list(set(verse.get('translation_source', '') for verse in context.verses_data))
        }

    def _generate_recommendations(self, context: AnalysisContext) -> List[str]:
        """Generate recommendations for further study"""
        recommendations = []
        
        if len(context.verses_data) < 5:
            recommendations.append("Consider expanding search to include more related verses")
        
        if not context.strongs_data:
            recommendations.append("Original language analysis would enhance understanding")
        
        if not context.cross_refs_data:
            recommendations.append("Cross-reference study would provide broader context")
        
        if len(set(verse.get('translation_source', '') for verse in context.verses_data)) < 2:
            recommendations.append("Compare across multiple translations for deeper insight")
        
        if context.analysis_type == AnalysisType.THEMATIC:
            recommendations.append("Consider studying this theme throughout biblical history")
        
        if context.analysis_type == AnalysisType.THEOLOGICAL:
            recommendations.append("Explore systematic theology connections")
        
        return recommendations

# Import existing data gathering methods from the original analyzer
# (These would need to be adapted from the original contextual_insights_api.py)

@enhanced_insights_bp.route('/enhanced-insights', methods=['POST'])
def get_enhanced_insights():
    """Get enhanced biblical insights with sophisticated analysis"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        print(f"Processing enhanced analysis for: {query}")
        
        # Initialize enhanced analyzer
        analyzer = EnhancedBibleAnalyzer()
        
        # Determine analysis type
        analysis_type = analyzer.determine_analysis_type(query)
        print(f"Analysis type: {analysis_type.value}")
        
        # TODO: Gather data using existing methods from contextual_insights_api.py
        # This would require importing and adapting the data gathering methods
        
        # For now, return a placeholder response
        return jsonify({
            "error": "Enhanced insights API is under development. Data gathering methods need to be integrated.",
            "analysis_type": analysis_type.value,
            "query": query
        })
        
    except Exception as e:
        return jsonify({'error': f'Enhanced insights error: {str(e)}'}), 500

@enhanced_insights_bp.route('/health')
def health():
    """Health check for enhanced insights API"""
    return jsonify({
        'status': 'healthy',
        'service': 'Enhanced Insights API',
        'version': '1.0.0',
        'features': [
            'Advanced prompt engineering',
            'Multi-stage analysis pipeline',
            'Confidence scoring',
            'Structured recommendations'
        ]
    })

if __name__ == '__main__':
    print("Enhanced Insights API - Development Version")
    print("This module provides improved biblical insights through:")
    print("- Advanced prompt engineering")
    print("- Multi-stage analysis pipeline")
    print("- Enhanced theological depth")
    print("- Structured output with confidence scoring")