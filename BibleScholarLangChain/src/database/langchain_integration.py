"""
LangChain Integration for BibleScholarLangChain

This module provides comprehensive integration with LangChain's PGVector store 
using the existing database structure and enhancing search capabilities.

Features:
- LangChain PGVector integration with existing tables
- Cross-referencing with versification mappings  
- Hebrew/Greek word analysis integration
- Multi-translation support
- Comprehensive result ranking
"""

import os
import logging
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# LangChain imports with fallback
try:
    from langchain_postgres import PGVector
    from langchain_core.embeddings import Embeddings
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("LangChain packages successfully imported")
except ImportError as e:
    logging.warning(f"LangChain packages not fully available: {e}")
    PGVector = None
    Embeddings = None
    Document = None
    LANGCHAIN_AVAILABLE = False

import psycopg
from psycopg.rows import dict_row

# Import with fallback for different execution contexts
try:
    from src.database.secure_connection import get_secure_connection
except ImportError:
    try:
        from BibleScholarLangChain.src.database.secure_connection import get_secure_connection
    except ImportError:
        # Last resort - add path and import
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from src.database.secure_connection import get_secure_connection

logger = logging.getLogger(__name__)

class BibleEmbeddings(Embeddings if LANGCHAIN_AVAILABLE else object):
    """Custom embeddings class for Bible search using LM Studio API."""
    
    def __init__(self, api_url: str = "http://localhost:1234/v1/embeddings"):
        self.api_url = api_url
        
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text using LM Studio."""
        try:
            import requests
            
            response = requests.post(
                self.api_url,
                json={
                    "model": "bge-m3",
                    "input": text
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["embedding"]
            
            logger.warning("Failed to get embedding from LM Studio API")
            return [0.0] * 1024  # Default BGE-M3 dimension
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return [0.0] * 1024
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents."""
        return [self._get_embedding(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query."""
        return self._get_embedding(text)

class BibleLangChainStore:
    """
    Comprehensive Bible search using LangChain integration.
    
    This class provides enhanced search capabilities by combining:
    - LangChain PGVector integration with existing tables
    - Cross-referencing with versification mappings  
    - Hebrew/Greek word analysis integration
    - Multi-translation support
    - Comprehensive result ranking and deduplication
    """
    
    def __init__(self, collection_name: str = "bible_comprehensive"):
        self.collection_name = collection_name
        self.embeddings = BibleEmbeddings()
        self.vector_store = None
        
        if LANGCHAIN_AVAILABLE:
            self._initialize_vector_store()
        else:
            logger.warning("LangChain not available - some features will be limited")
    
    def _initialize_vector_store(self):
        """Initialize LangChain PGVector store (MCP rules: use correct signature, no connection_string kwarg)."""
        try:
            # Build connection string from environment or defaults (MCP rules)
            conn_str = "postgresql://postgres:postgres@localhost:5432/bible_db"
            # For langchain_postgres 0.0.13, use 'connection' not 'connection_string'
            # See: https://github.com/langchain-ai/langchain-postgres/blob/main/langchain_postgres/vectorstores.py
            self.vector_store = PGVector(
                collection_name=self.collection_name,
                connection=conn_str,
                embeddings=self.embeddings,
                use_jsonb=True
            )
            logger.info("LangChain vector store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LangChain vector store: {e}")
            self.vector_store = None
    
    def comprehensive_search(self, 
                           query: str,
                           translation: str = "KJV",
                           k: int = 10,
                           include_cross_refs: bool = True,
                           include_word_analysis: bool = True) -> Dict[str, Any]:
        """
        Perform comprehensive Bible search using all available data sources.
        
        This method combines:
        1. LangChain vector similarity search (if available)
        2. Native pgvector search on bible.verse_embeddings
        3. Cross-references from versification mappings
        4. Hebrew/Greek word analysis
        5. Intelligent result ranking and deduplication
        """
        
        search_results = {
            "query": query,
            "translation": translation,
            "timestamp": datetime.now().isoformat(),
            "langchain_results": [],
            "native_vector_results": [],
            "cross_references": [],
            "word_analysis": [],
            "combined_results": [],
            "metadata": {
                "sources_used": [],
                "total_unique_verses": 0,
                "processing_time_ms": 0,
                "langchain_available": LANGCHAIN_AVAILABLE
            }
        }
        
        start_time = datetime.now()
        
        try:
            # 1. LangChain similarity search (if available)
            if self.vector_store:
                try:
                    langchain_docs = self.vector_store.similarity_search_with_score(
                        query,
                        k=k*2,  # Get more for ranking
                        filter={"translation_source": translation}
                    )
                    
                    search_results["langchain_results"] = [
                        {
                            "content": doc[0].page_content,
                            "metadata": doc[0].metadata,
                            "similarity_score": float(doc[1]),
                            "source": "langchain"
                        }
                        for doc in langchain_docs
                    ]
                    
                    search_results["metadata"]["sources_used"].append("langchain_vector")
                    logger.info(f"LangChain search returned {len(search_results['langchain_results'])} results")
                    
                except Exception as e:
                    logger.warning(f"LangChain search failed: {e}")
            
            # 2. Native vector search (always available)
            native_results = self._native_vector_search(query, translation, k*2)
            search_results["native_vector_results"] = native_results
            if native_results:
                search_results["metadata"]["sources_used"].append("native_vector")
                logger.info(f"Native vector search returned {len(native_results)} results")
            
            # 3. Get cross-references for top results
            if include_cross_refs:
                top_verses = self._extract_top_verses(
                    search_results["langchain_results"] + search_results["native_vector_results"],
                    limit=5
                )
                cross_refs = self._get_cross_references(top_verses)
                search_results["cross_references"] = cross_refs
                if cross_refs:
                    search_results["metadata"]["sources_used"].append("versification_mappings")
                    logger.info(f"Found {len(cross_refs)} cross-references")
            
            # 4. Get word analysis for top results  
            if include_word_analysis:
                word_analysis = self._get_word_analysis(
                    search_results["langchain_results"][:3] + search_results["native_vector_results"][:3]
                )
                search_results["word_analysis"] = word_analysis
                if word_analysis:
                    search_results["metadata"]["sources_used"].append("hebrew_greek_words")
                    logger.info(f"Found word analysis for {len(word_analysis)} verses")
            
            # 5. Combine and rank all results
            combined = self._combine_and_rank_results(
                search_results["langchain_results"],
                search_results["native_vector_results"],
                k
            )
            search_results["combined_results"] = combined
            search_results["metadata"]["total_unique_verses"] = len(combined)
            
            # Calculate processing time
            end_time = datetime.now()
            search_results["metadata"]["processing_time_ms"] = int(
                (end_time - start_time).total_seconds() * 1000
            )
            
            logger.info(f"Comprehensive search completed: {len(combined)} unique results in {search_results['metadata']['processing_time_ms']}ms")
            
        except Exception as e:
            logger.error(f"Error in comprehensive search: {e}")
            search_results["error"] = str(e)
        
        return search_results
    
    def _native_vector_search(self, query: str, translation: str, k: int) -> List[Dict[str, Any]]:
        """Search using native pgvector on bible.verse_embeddings."""
        try:
            # Get query embedding
            embedding = self.embeddings.embed_query(query)
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
            
            with get_secure_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT e.verse_id, e.book_name, e.chapter_num, e.verse_num,
                               v.text, e.translation_source,
                               1 - (e.embedding <=> %s::vector) as similarity
                        FROM bible.verse_embeddings e
                        JOIN bible.verses v ON e.verse_id = v.verse_id  
                        WHERE e.translation_source = %s
                        ORDER BY e.embedding <=> %s::vector
                        LIMIT %s
                    """, (embedding_str, translation, embedding_str, k))
                    
                    results = cursor.fetchall()
            
            return [
                {
                    "verse_id": r["verse_id"],
                    "content": r["text"],
                    "metadata": {
                        "verse_id": r["verse_id"],
                        "book_name": r["book_name"],
                        "chapter_num": r["chapter_num"],
                        "verse_num": r["verse_num"],
                        "translation_source": r["translation_source"],
                        "reference": f"{r['book_name']} {r['chapter_num']}:{r['verse_num']}"
                    },
                    "similarity_score": float(r["similarity"]),
                    "source": "native_vector"
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Error in native vector search: {e}")
            return []
    
    def _extract_top_verses(self, results: List[Dict], limit: int = 5) -> List[Dict]:
        """Extract top unique verses from mixed results."""
        seen_verses = set()
        top_verses = []
        
        # Sort by similarity score
        sorted_results = sorted(
            results, 
            key=lambda x: x.get("similarity_score", 0), 
            reverse=True
        )
        
        for result in sorted_results:
            metadata = result.get("metadata", {})
            verse_id = metadata.get("verse_id")
            
            if verse_id and verse_id not in seen_verses:
                seen_verses.add(verse_id)
                top_verses.append(metadata)
                
                if len(top_verses) >= limit:
                    break
        
        return top_verses
    
    def _get_cross_references(self, verses: List[Dict]) -> List[Dict[str, Any]]:
        """Get cross-references using versification mappings."""
        if not verses:
            return []
        
        try:
            cross_refs = []
            
            with get_secure_connection() as conn:
                with conn.cursor() as cursor:
                    for verse in verses:
                        book_name = verse.get("book_name")
                        chapter_num = verse.get("chapter_num") 
                        verse_num = verse.get("verse_num")
                        
                        if not all([book_name, chapter_num, verse_num]):
                            continue
                        
                        cursor.execute("""
                            SELECT target_book, target_chapter, target_verse,
                                   mapping_type, notes
                            FROM bible.versification_mappings
                            WHERE source_book = %s AND source_chapter = %s AND source_verse = %s
                            LIMIT 5
                        """, (book_name, chapter_num, verse_num))
                        
                        mappings = cursor.fetchall()
                        
                        if mappings:
                            cross_refs.append({
                                "source_reference": verse.get("reference", f"{book_name} {chapter_num}:{verse_num}"),
                                "mappings": [
                                    {
                                        "target_reference": f"{m['target_book']} {m['target_chapter']}:{m['target_verse']}",
                                        "mapping_type": m["mapping_type"],
                                        "notes": m["notes"]
                                    }
                                    for m in mappings
                                ]
                            })
            
            return cross_refs
            
        except Exception as e:
            logger.error(f"Error getting cross-references: {e}")
            return []
    
    def _get_word_analysis(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Get Hebrew/Greek word analysis for verses."""
        if not results:
            return []
        
        try:
            word_analysis = []
            processed_verses = set()
            
            with get_secure_connection() as conn:
                with conn.cursor() as cursor:
                    for result in results:
                        metadata = result.get("metadata", {})
                        verse_id = metadata.get("verse_id")
                        
                        if not verse_id or verse_id in processed_verses:
                            continue
                        
                        processed_verses.add(verse_id)
                        
                        # Hebrew words
                        cursor.execute("""
                            SELECT hw.word_text, hw.strongs_id, hw.transliteration, hw.gloss,
                                   he.definition, hmc.description as morphology
                            FROM bible.hebrew_ot_words hw
                            LEFT JOIN bible.hebrew_entries he ON hw.strongs_id = he.strongs_id
                            LEFT JOIN bible.hebrew_morphology_codes hmc ON hw.grammar_code = hmc.code
                            WHERE hw.verse_id = %s
                            ORDER BY hw.word_position
                        """, (verse_id,))
                        
                        hebrew_words = cursor.fetchall()
                        
                        # Greek words
                        cursor.execute("""
                            SELECT gw.word_text, gw.strongs_id, gw.transliteration, gw.gloss,
                                   ge.definition, gmc.description as morphology
                            FROM bible.greek_nt_words gw
                            LEFT JOIN bible.greek_entries ge ON gw.strongs_id = ge.strongs_id
                            LEFT JOIN bible.greek_morphology_codes gmc ON gw.grammar_code = gmc.code
                            WHERE gw.verse_id = %s
                            ORDER BY gw.word_position
                        """, (verse_id,))
                        
                        greek_words = cursor.fetchall()
                        
                        if hebrew_words or greek_words:
                            word_analysis.append({
                                "verse_id": verse_id,
                                "reference": metadata.get("reference", ""),
                                "hebrew_words": [
                                    {
                                        "word": w["word_text"],
                                        "strongs_id": w["strongs_id"],
                                        "transliteration": w["transliteration"],
                                        "gloss": w["gloss"],
                                        "definition": w["definition"],
                                        "morphology": w["morphology"]
                                    }
                                    for w in hebrew_words if w["word_text"]
                                ],
                                "greek_words": [
                                    {
                                        "word": w["word_text"],
                                        "strongs_id": w["strongs_id"], 
                                        "transliteration": w["transliteration"],
                                        "gloss": w["gloss"],
                                        "definition": w["definition"],
                                        "morphology": w["morphology"]
                                    }
                                    for w in greek_words if w["word_text"]
                                ]
                            })
            
            return word_analysis
            
        except Exception as e:
            logger.error(f"Error getting word analysis: {e}")
            return []
    
    def _combine_and_rank_results(self, 
                                 langchain_results: List[Dict],
                                 native_results: List[Dict],
                                 k: int) -> List[Dict[str, Any]]:
        """Combine and rank results from multiple sources."""
        try:
            verse_scores = {}
            
            # Process LangChain results
            for i, result in enumerate(langchain_results):
                metadata = result.get("metadata", {})
                verse_id = metadata.get("verse_id")
                
                if verse_id:
                    verse_scores[verse_id] = {
                        "verse_id": verse_id,
                        "content": result.get("content", ""),
                        "metadata": metadata,
                        "langchain_score": result.get("similarity_score", 0.0),
                        "langchain_rank": i + 1,
                        "native_score": 0.0,
                        "native_rank": None,
                        "sources": ["langchain"],
                        "combined_score": result.get("similarity_score", 0.0)
                    }
            
            # Process native results
            for i, result in enumerate(native_results):
                verse_id = result.get("verse_id")
                
                if verse_id:
                    if verse_id in verse_scores:
                        # Update existing entry
                        verse_scores[verse_id]["native_score"] = result.get("similarity_score", 0.0)
                        verse_scores[verse_id]["native_rank"] = i + 1
                        verse_scores[verse_id]["sources"].append("native")
                        # Average the scores
                        verse_scores[verse_id]["combined_score"] = (
                            verse_scores[verse_id]["langchain_score"] + 
                            result.get("similarity_score", 0.0)
                        ) / 2
                    else:
                        # New entry
                        verse_scores[verse_id] = {
                            "verse_id": verse_id,
                            "content": result.get("content", ""),
                            "metadata": result.get("metadata", {}),
                            "langchain_score": 0.0,
                            "langchain_rank": None,
                            "native_score": result.get("similarity_score", 0.0),
                            "native_rank": i + 1,
                            "sources": ["native"],
                            "combined_score": result.get("similarity_score", 0.0)
                        }
            
            # Sort by combined score and return top k
            ranked_results = sorted(
                verse_scores.values(),
                key=lambda x: x["combined_score"],
                reverse=True
            )
            
            return ranked_results[:k]
            
        except Exception as e:
            logger.error(f"Error combining results: {e}")
            return []
    
    def get_store_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the LangChain store and database resources."""
        try:
            with get_secure_connection() as conn:
                with conn.cursor() as cursor:
                    # LangChain store stats
                    cursor.execute("""
                        SELECT COUNT(*) as langchain_docs
                        FROM public.langchain_pg_embedding lpe
                        JOIN public.langchain_pg_collection lpc ON lpe.collection_id = lpc.uuid
                        WHERE lpc.name = %s
                    """, (self.collection_name,))
                    
                    langchain_count = cursor.fetchone()["langchain_docs"]
                    
                    # Native embeddings stats
                    cursor.execute("SELECT COUNT(*) as native_embeddings FROM bible.verse_embeddings")
                    native_count = cursor.fetchone()["native_embeddings"]
                    
                    # Total verses
                    cursor.execute("SELECT COUNT(*) as total_verses FROM bible.verses")
                    total_verses = cursor.fetchone()["total_verses"]
                    
                    # Cross-reference mappings
                    cursor.execute("SELECT COUNT(*) as mappings FROM bible.versification_mappings")
                    mappings_count = cursor.fetchone()["mappings"]
                    
                    # Word analysis coverage
                    cursor.execute("SELECT COUNT(DISTINCT verse_id) as hebrew_coverage FROM bible.hebrew_ot_words")
                    hebrew_coverage = cursor.fetchone()["hebrew_coverage"]
                    
                    cursor.execute("SELECT COUNT(DISTINCT verse_id) as greek_coverage FROM bible.greek_nt_words")
                    greek_coverage = cursor.fetchone()["greek_coverage"]
            
            return {
                "collection_name": self.collection_name,
                "langchain_available": LANGCHAIN_AVAILABLE,
                "vector_store_initialized": self.vector_store is not None,
                "statistics": {
                    "langchain_documents": langchain_count,
                    "native_embeddings": native_count,
                    "total_verses": total_verses,
                    "versification_mappings": mappings_count,
                    "hebrew_word_coverage": hebrew_coverage,
                    "greek_word_coverage": greek_coverage
                },
                "coverage": {
                    "langchain_percentage": (langchain_count / max(total_verses, 1)) * 100,
                    "native_embeddings_percentage": (native_count / max(total_verses, 1)) * 100,
                    "hebrew_analysis_percentage": (hebrew_coverage / max(total_verses, 1)) * 100,
                    "greek_analysis_percentage": (greek_coverage / max(total_verses, 1)) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting store status: {e}")
            return {"error": str(e)} 