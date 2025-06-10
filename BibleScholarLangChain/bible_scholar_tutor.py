#!/usr/bin/env python3
"""
BibleScholar Modular Tutor System
CLI-based interface for Bible study with LM Studio integration
"""
import sys
import os
import requests
import json
from typing import List, Dict, Any
from colorama import Fore, Style, init

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.secure_connection import get_secure_connection
from scripts.db_config import load_config

init(autoreset=True)

class LMStudioEmbedding:
    def __init__(self, base_url="http://localhost:1234/v1", model="text-embedding-bge-m3"):
        self.base_url = base_url
        self.model = model
        self.embeddings_url = f"{base_url}/embeddings"
    
    def get_embedding(self, text: str) -> List[float]:
        try:
            response = requests.post(
                self.embeddings_url,
                json={"input": text, "model": self.model},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["data"][0]["embedding"]
            else:
                raise Exception(f"Embedding API error: {response.text}")
        except Exception as e:
            print(Fore.RED + f"Embedding failed: {e}")
            return []

class BibleScholarTutor:
    def __init__(self):
        self.config = load_config()
        self.embedding_model = LMStudioEmbedding()
        self.llm_url = "http://localhost:1234/v1/chat/completions"
    
    def search_verses(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for verses using semantic similarity"""
        try:
            embedding = self.embedding_model.get_embedding(query)
            if not embedding:
                return []
            
            with get_secure_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT book, chapter, verse, text, "
                        "embedding <=> %s::vector AS distance "
                        "FROM bible.verse_embeddings "
                        "ORDER BY distance LIMIT %s",
                        (embedding, limit)
                    )
                    return cursor.fetchall()
        except Exception as e:
            print(Fore.RED + f"Search failed: {e}")
            return []
    
    def get_insights(self, query: str, verses: List[Dict]) -> str:
        """Get contextual insights from LM Studio"""
        try:
            context = "\n".join([f"{v['book']} {v['chapter']}:{v['verse']} - {v['text']}" for v in verses])
            prompt = f"""Provide biblical insights for the query: "{query}"
            
            Relevant verses:
            {context}
            
            Please provide theological commentary and practical applications."""
            
            response = requests.post(
                self.llm_url,
                json={
                    "model": "meta-llama-3.1-8b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error getting insights: {response.text}"
        except Exception as e:
            return f"Insights failed: {e}"
    
    def interactive_session(self):
        """Start interactive CLI session"""
        print(Fore.CYAN + Style.BRIGHT + "Welcome to BibleScholar Tutor!")
        print("Enter your Bible study questions or 'quit' to exit.\n")
        
        while True:
            query = input(Fore.GREEN + "Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print(Fore.YELLOW + "Goodbye!")
                break
            
            if not query:
                continue
            
            print(Fore.BLUE + "Searching for relevant verses...")
            verses = self.search_verses(query)
            
            if verses:
                print(Fore.CYAN + "\nRelevant verses:")
                for i, verse in enumerate(verses, 1):
                    print(f"{i}. {verse['book']} {verse['chapter']}:{verse['verse']}")
                    print(f"   {verse['text']}\n")
                
                print(Fore.BLUE + "Getting biblical insights...")
                insights = self.get_insights(query, verses)
                print(Fore.MAGENTA + "\nInsights:")
                print(insights)
                print("\n" + "-"*50 + "\n")
            else:
                print(Fore.RED + "No relevant verses found. Try a different query.\n")

def main():
    tutor = BibleScholarTutor()
    tutor.interactive_session()

if __name__ == "__main__":
    main() 