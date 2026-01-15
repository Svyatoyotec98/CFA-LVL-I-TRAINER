"""
Test what the API endpoint actually returns
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from backend.routers.glossary import load_all_glossary

print("=" * 60)
print("API RESPONSE TEST")
print("=" * 60)

# Simulate what /api/glossary endpoint returns
all_terms = load_all_glossary()

print(f"\nTotal terms: {len(all_terms)}")

# Check if terms have book_id
book_id_count = sum(1 for t in all_terms if 'book_id' in t)
print(f"Terms with book_id: {book_id_count}")

# Count by book_id
from collections import Counter
book_ids = [t.get('book_id', 'MISSING') for t in all_terms]
book_counts = Counter(book_ids)

print("\nTerms by book_id:")
for book_id in sorted([k for k in book_counts.keys() if isinstance(k, int)]):
    print(f"  book_id={book_id}: {book_counts[book_id]} terms")

if 'MISSING' in book_counts:
    print(f"  book_id=MISSING: {book_counts['MISSING']} terms ⚠️")

# Show first 3 Book 2 terms
book2_terms = [t for t in all_terms if t.get('book_id') == 2]
print(f"\n Book 2 (Economics) terms: {len(book2_terms)}")
print("\nFirst 3 Book 2 terms:")
for i, term in enumerate(book2_terms[:3], 1):
    print(f"  {i}. {term.get('term_en', 'N/A')}")
    print(f"     book_id: {term.get('book_id', 'MISSING')}")
    print(f"     module_id: {term.get('module_id', 'MISSING')}")

print("\n" + "=" * 60)
