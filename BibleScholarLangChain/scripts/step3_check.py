#!/usr/bin/env python3
"""
Check and fix psycopg2 vs psycopg3 conflicts for BibleScholarLangChain setup
"""
import os
import subprocess
import psycopg

def check_psycopg3():
    try:
        print(f"Psycopg version: {psycopg.__version__}")
        if not psycopg.__version__.startswith('3'):
            raise RuntimeError("psycopg3 not installed")
    except ImportError:
        raise RuntimeError("psycopg not installed")

def uninstall_psycopg2():
    subprocess.run([r"C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BSPclean\\Scripts\\pip.exe", "uninstall", "-y", "psycopg2", "psycopg2-binary"], capture_output=True, text=True)
    print("Uninstalled psycopg2")

def check_vector_store():
    conn = psycopg.connect("host=localhost port=5432 dbname=bible_db user=postgres password=postgres")
    cursor = conn.cursor()
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'bible' AND table_name = 'verse_embeddings')")
    exists = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return exists

if __name__ == "__main__":
    uninstall_psycopg2()
    check_psycopg3()
    if check_vector_store():
        print("Existing bible.verse_embeddings found; skipping new collection")
    else:
        print("No existing store; creating new collection") 