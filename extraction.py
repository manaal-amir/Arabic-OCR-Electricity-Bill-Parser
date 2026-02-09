#Saudi Electricity Bill Parser
#Extracts invoice data from PDF bills using OCR.

#imports and dependencies
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import re
from datetime import datetime
import json
import os
import unicodedata

PDF_PATH = "bill.pdf"
pytesseract.pytesseract.tesseract_cmd = r"D:\\Tesseract\\tesseract.exe"


def normalize_arabic_digits(text):
    return text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))


def normalize_arabic(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("ـ", "")
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'(?<=[\u0600-\u06FF])\s+(?=[\u0600-\u06FF])', '', text)
    return text


def extract_text_from_pdf():
    extracted = ""

    try:
        with pdfplumber.open(PDF_PATH) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    extracted += t + "\n"
    except:
        pass

    if len(extracted.strip()) < 50:
        print("\n[INFO] Using OCR...\n")
        images = convert_from_path(PDF_PATH, dpi=300)
        for img in images:
            extracted += pytesseract.image_to_string(
                img, lang="ara+eng", config="--psm 6"
            ) + "\n"

    normalized = normalize_arabic(extracted)
    normalized = normalize_arabic_digits(normalized)

    with open("ocr_output_debug.txt", "w", encoding="utf-8") as f:
        f.write(normalized)

    print("\nNORMALIZED OCR DEBUG OUTPUT\n")
    print(normalized)

    return normalized


def extract_invoice_data(text):
    data = {}

    #OCR patterns from our bill
    TOTAL = ["بولطملاغلبملا", "المبلغالمطلوب", r"المبلغ\s*المطلوب"]
    CONS = ["كلاهتسلإاةيمك", "كميةالاستهلاك", r"كمية\s*الاستهلاك"]
    ACC = ["باسحلامقر", "رقمالحساب", r"رقم\s*الحساب"]
    METER = ["دادعلامقر", "رقمالعداد", r"رقم\s*العداد"]

    def OR(p):
        return "(" + "|".join(p) + ")"

    def extract_number(patterns, text, number_regex):
        #Try: label + number
        m = re.search(OR(patterns) + number_regex, text)
        if m:
            return m.group(m.lastindex)

        #Try: number + label
        m = re.search(number_regex + OR(patterns), text)
        if m:
            return m.group(1)

        return None

    #-----------------------------
    #TOTAL AMOUNT
    #-----------------------------
    data["Total Amount"] = extract_number(TOTAL, text, r"\s*(\d+\.\d+)")
    data["Currency"] = "SAR"

    #-----------------------------
    #CONSUMPTION 
    #-----------------------------
    cons_label = "كلاهتسلإاةيمك"

    #Pattern: number immediately followed by label
    m = re.search(r"(\d+)" + cons_label, text)

    if m:
        data["Consumption kWh"] = m.group(1)
    else:
        #Fallback: spaced or alternative forms
        m = re.search(r"(\d+)\s*(?:كميةالاستهلاك|كمية\s*الاستهلاك)", text)
        if m:
            data["Consumption kWh"] = m.group(1)

    #-----------------------------
    #ACCOUNT NUMBER
    #-----------------------------
    data["Account Number"] = extract_number(ACC, text, r"\s*(\d{8,15})")

    #-----------------------------
    #METER NUMBER
    #-----------------------------
    data["Meter Number"] = extract_number(METER, text, r"\s*(\d{4,10})")

    #-----------------------------
    #PRINTED DURATION (عدد الأيام)
    #-----------------------------
    m = re.search(r"(\d+)\s*مايلأاددع", text)
    if m:
        data["Duration"] = m.group(1)

    #-----------------------------
    #DATES 
    #-----------------------------
    dates = re.findall(r"(20\d{2}/\d{2}/\d{2})", text)
    if len(dates) >= 2:
        data["Start of Period"] = dates[0]
        data["End of Period"] = dates[1]

        #Only calculate if printed duration missing or cant be read due to noise
        if "Duration" not in data:
            d1 = datetime.strptime(dates[0], "%Y/%m/%d")
            d2 = datetime.strptime(dates[1], "%Y/%m/%d")
            data["Duration"] = str((d2 - d1).days)

    return data


def display_extraction_results(data):
    print("\n" + "-" * 60)
    print("EXTRACTED DATA")
    print("-" * 60)

    fields = [
        "Total Amount", "Currency", "Consumption kWh",
        "Start of Period", "End of Period", "Duration",
        "Account Number", "Meter Number"
    ]

    found = 0
    for f in fields:
        v = data.get(f)
        print(f"{f}: {v if v else 'Not found'}")
        if v:
            found += 1

    print("-" * 60)
    print(f"\nExtraction summary: {found}/8 fields found")
    return found


def save_results_to_files(data):
    clean = {k: v for k, v in data.items() if v}

    with open("extracted_invoice_data.json", "w", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False, indent=2)

    with open("extracted_invoice_data.txt", "w", encoding="utf-8") as f:
        for k, v in clean.items():
            f.write(f"{k}: {v}\n")

    print("\nSaved extracted data to JSON and TXT files.")


def main():
    print("-" * 60)
    print("SAUDI ELECTRICITY BILL PARSER")
    print("-" * 60)

    text = extract_text_from_pdf()
    data = extract_invoice_data(text)
    display_extraction_results(data)
    save_results_to_files(data)



if __name__ == "__main__":
    main()