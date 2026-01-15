"""
Test script to check glossary loading
Run this on your local machine to debug
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.routers.glossary import load_glossary_data, load_all_glossary, DATA_PATH

print("=" * 60)
print("GLOSSARY LOADING TEST")
print("=" * 60)

print(f"\n1. DATA_PATH: {DATA_PATH}")
print(f"   Exists: {os.path.exists(DATA_PATH)}")

if os.path.exists(DATA_PATH):
    print(f"\n   Contents:")
    for item in os.listdir(DATA_PATH):
        item_path = os.path.join(DATA_PATH, item)
        if os.path.isdir(item_path):
            print(f"     - {item}/")

print("\n" + "=" * 60)
print("2. Loading Book 2 (Economics)")
print("=" * 60)

data = load_glossary_data(2)
print(f"   Book ID: {data.get('book_id')}")
print(f"   Book Name: {data.get('book_name')}")
print(f"   Total Modules: {data.get('total_modules')}")
print(f"   Total Terms: {len(data.get('terms', []))}")

print("\n   Modules:")
for mod in data.get('modules', []):
    print(f"     Module {mod['module_id']}: {mod['module_name']} ({mod['term_count']} terms)")

print("\n" + "=" * 60)
print("3. Loading All Glossary")
print("=" * 60)

all_terms = load_all_glossary()
print(f"   Total terms across all books: {len(all_terms)}")

# Count by book
book_counts = {}
for term in all_terms:
    book_id = term.get('book_id', 'unknown')
    book_counts[book_id] = book_counts.get(book_id, 0) + 1

print("\n   Terms by book:")
for book_id in sorted([k for k in book_counts.keys() if isinstance(k, int)]):
    print(f"     Book {book_id}: {book_counts[book_id]} terms")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
