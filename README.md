# Arabic-OCR-Electricity-Bill-Parser
A Python tool that automatically extracts structured billing data from Saudi Electricity Company (SEC) invoices using Arabic OCR, text normalization, and pattern‑based parsing.  
It reads PDF bills (including scanned or image‑based ones), performs OCR on Arabic text, cleans and normalizes the output, and extracts key fields such as total amount, consumption, billing period, duration, account number, and meter number, exactly as printed on the bill.  

## Python Libraries  
- pdfplumber – Reads embedded text from PDF files when available.  
- pytesseract – Performs OCR on scanned or image‑based PDFs using Arabic and English language models.   
- pdf2image – Converts PDF pages into high‑resolution images for OCR processing.  
- unicodedata – Normalizes Arabic characters and removes presentation forms.  
- re (Regular Expressions) – Pattern matching for extracting structured fields from noisy OCR output.  
- datetime – Calculates billing periods and fallback durations.  
- json & os – Saving extracted results and handling file operations.  

## Core Techniques
- Arabic OCR Processing  
Uses Tesseract with ara+eng models to read mixed‑language text from SEC bills.  
- Unicode Normalization (NFKC)  
Converts Arabic presentation forms (ﻝ, ﻡ, ﻊ, etc.) into standard characters to improve regex matching.  
- Digit Normalization  
Converts Arabic‑Indic digits (٠١٢٣٤٥٦٧٨٩) into Western digits (0123456789).  
- Noise Removal & Cleanup  
Removes tatweel (ـ), diacritics, and random spacing between Arabic letters.  
- Pattern‑Based Field Extraction  
Uses robust regex patterns that match:  
- spaced Arabic labels   
- glued labels 
- reversed patterns (number before label)

## Output in terminal:  
<img width="948" height="822" alt="image" src="https://github.com/user-attachments/assets/1940c8eb-4bba-49c0-b3a3-135dde724b77" />  


## Limitations  
- OCR accuracy depends on the quality of the scanned PDF.
- Some Arabic text may appear “glued” together due to OCR quirks.
- Older or differently formatted SEC bills may require updated patterns.
- Only top‑level fields are extracted (no tariff tables yet).
- Handwritten notes, stamps, or low‑contrast text cannot be processed.  

## Note  
AI tools were used throughout this project to help debug issues, explain unfamiliar technical concepts, and translate Arabic text when needed, as the developer is not a native Arabic speaker.  

