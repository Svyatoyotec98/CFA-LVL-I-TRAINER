# CRITICAL INSTRUCTIONS

## PDF FILES - READ THIS FIRST
⚠️ NEVER use `Read`, `View`, or `cat` on PDF files directly.
PDF files will ALWAYS fail with "PDF too large" error.

### Correct way to read PDF:
1. First convert to text:
```bash
pdftotext "filename.pdf" "filename.txt"
```
2. Then read the .txt file

### If pdftotext is not installed:
```bash
pip install pdfplumber
python -c "import pdfplumber; pdf=pdfplumber.open('file.pdf'); print(''.join(p.extract_text() or '' for p in pdf.pages))"
```

## Project Documentation
Read CLAUDE_CODE_MANUAL.md for full project specifications.