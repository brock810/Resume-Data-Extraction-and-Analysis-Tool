import spacy
import zipfile
import os
import pdfplumber
import re
import json

nlp = spacy.load("en_core_web_sm")

dataset_zip_path = r'C:\Users\Brock\ResumeP.zip'

extraction_dir = r'C:\Users\Brock\ansel'  

os.makedirs(extraction_dir, exist_ok=True)

with zipfile.ZipFile(dataset_zip_path, 'r') as zip_ref:
    zip_ref.extractall(extraction_dir)

resume_files = os.listdir(extraction_dir)

all_resumes_data = []

def preprocess_resume_text(text):
    text = ' '.join(text.split())

    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    text = text.lower()
    
    return text

def extract_phone_numbers(text):
    phone_numbers = re.findall(r'\b(?:\d{3}[-.]?)?\d{3}[-.]?\d{4}\b', text)
    return phone_numbers

def extract_skills(text):
    doc = nlp(text)
    extracted_skills = []

    skill_keywords = [
        "python", "java", "c#", "javascript", "html", "css", "php",
        "ruby", "go", "matlab", "typescript", "objective-c", "kotlin",
        "swift", "sql", "rust", "perl", "scala", "dart", "r", "lua",
        "haskell", "cobol", "fortran", "assembly", "vba", "groovy",
        "shell scripting", "bash", "powershell", "elixir", "clojure",
        "vb.net", "groovy", "pl/sql", "abap", "scratch", "solidity",
        "verilog", "vhdl", "labview", "pascal", "scheme", "cobol", "rpg",
        "lisp", "prolog", "f#", "dart", "actionscript", "perl"
    ]

    skill_section_start = re.search(r'(?i)\b(?:SKILLS?)\b', text)
    if skill_section_start:
        skill_text = text[skill_section_start.end():].strip()
        for keyword in skill_keywords:
            if keyword in skill_text.lower():
                extracted_skills.append(keyword.capitalize())

    return list(set(extracted_skills))


def extract_education(text):
    education_entries = []
    lines = text.split('\n')
    current_education = {"Bachelor": "", "Diploma": "", "Date": ""}

    inside_education_section = False

    for line in lines:
        if re.search(r'(?i)\b(?:SKILLS)\b', line):
            break

        if re.search(r'(?i)\b(?:EDUCATION)\b', line):
            inside_education_section = True
        elif inside_education_section:
            if re.search(r'Bachelor', line):
                current_education["Bachelor"] = re.sub(r'Bachelor', '', line).strip()
            elif re.search(r'Diploma', line):
                current_education["Diploma"] = re.sub(r'Diploma', '', line).strip()
            elif re.search(r'\[\d{4}-\d{4}\]', line):
                current_education["Date"] = re.search(r'\[\d{4}-\d{4}\]', line).group()
                
                education_entries.append(current_education)
                current_education = {"Bachelor": "", "Diploma": "", "Date": ""}
                inside_education_section = False

    
    if inside_education_section and any(current_education.values()):
        education_entries.append(current_education)

    return education_entries

for resume_file in resume_files:
    print("\n" + "="*40)  
    resume_file_path = os.path.join(extraction_dir, resume_file)

    try:
        if resume_file.endswith(".pdf"):
            resume_data = {
                "Resume File": resume_file,
                "Email Addresses": [],
                "Phone Numbers": [],
                "Skills": [], 
                "Education": []
            }
                     
            with pdfplumber.open(resume_file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()          
                    resume_data["Email Addresses"].extend(re.findall(r'\S+@\S+\.\S+', page_text))
                    resume_data["Phone Numbers"].extend(extract_phone_numbers(page_text))
                    resume_data["Skills"].extend(extract_skills(page_text))             
                    resume_data["Education"].extend(extract_education(page_text))  
                           
            all_resumes_data.append(resume_data)

    except Exception as e:
        print(f"Error processing file {resume_file_path}: {e}")

output_json_path = r'C:\Users\Brock\.Origin\resumes_data.json'

with open(output_json_path, 'w') as json_file:
    json.dump(all_resumes_data, json_file, indent=4)

print("\nInformation extraction and storage as JSON completed. Data saved to:", output_json_path)
