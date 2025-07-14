# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 10:12:15 2025

@author: laiab
""" 
#------------------------------------------------------

import os
import sys
import re
import json
from string import punctuation
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from docx import Document
import fitz
from nltk import download
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import time
import shutil
from datetime import date
#------------------------------------------------------
global text
with open("languages/catalan.json", encoding="utf-8") as f:  # language by default
    text = json.load(f)
#------------------------------------------------------
download("punkt")
first_welcome = True
#------------------------------------------------------

#------------------------------------------------------
# main menu
#------------------------------------------------------

def welcome(): # opens the main menu
    global first_welcome
    if first_welcome:
        print(text["hello"])
        first_welcome = False  # so the introduction appears only the first time
    
    while True:        
        print(text["options"])    
        print(text["mainmenu"])      
        try:
            ans = int(input())
            if ans == 1: # budget calculator
                print(text["go_calculator"])
                calculator()
            elif ans == 2: # info menu
                info_menu()           
            elif ans == 3: # languages menu
                change_lang()
            elif ans == 4: # exit
                print(text["bye"])               
                sys.exit(0)   
        except ValueError:  # handle invalid input
            print(text["wrong_answer"])
            
#------------------------------------------------------
# info menu
#------------------------------------------------------

def info_menu():
    while True:     
        print(text["info_intro"])      
        print(text["info_list"])      
        try:
            ans = int(input())
            if ans == 1: # information about botsy
                print(text["info_botsy"])
                continue 
            elif ans == 2: # tariffs and language combination
                print(text["info_tariffs"])        
                break
            elif ans == 3: # info about data management
                print(text["info_processing"])  
                break
            elif ans == 4: # languages menu
                print(text["info_botsy_lang"])
                break
            elif ans == 5: # go back to main menu
                return welcome()     
        except ValueError:  # handle invalid input
            print(text["options"])
               
#------------------------------------------------------
# change language
#------------------------------------------------------
def change_lang():
    global text
    print(text["change_language"])
    print(text["change_lang_list"].format(text["ca"].capitalize(),
    text["es"].capitalize(), text["en"].capitalize() ))

    while True:
        try:
            ans = int(input())
            
            if ans == 1:
                with open("languages/catalan.json", encoding="utf-8") as f:
                    return json.load(f)
            elif ans == 2:
                with open("languages/spanish.json", encoding="utf-8") as f:
                    return json.load(f)
            elif ans == 3:
                with open("languages/english.json", encoding="utf-8") as f:
                    return json.load(f)
            elif ans == 4:
                return None  
        except ValueError:
            print(text["wrong_answer"])

#------------------------------------------------------
# Calculator
#------------------------------------------------------
# ask what is the source language 
                
def ask_lang_og():
    global og_name, og_code
    print(text["og_lang"])
    print(text["ask_lang"])
    while True:
        print(text["og_options"])
        try:
            lang = int(input())            
            if lang == 1: # catalan
                og_name, og_code = text["ca"] , "ca"
                return og_name , og_code # Returns both display name and language code
            if lang == 2: # spanish
                og_name, og_code = text["es"] , "es"
                return og_name , og_code
            if lang == 3: # english
                og_name, og_code = text["en"] , "en"
                return og_name , og_code
            if lang == 4: # french
                og_name, og_code = text["fr"] , "fr"
                return og_name , og_code
            if lang == 5: # italian
                og_name, og_code = text["it"] , "it"
                return og_name , og_code
            if lang == 6: # german
                og_name, og_code = text["de"] , "de"
                return og_name , og_code
            if lang == 7: # portuguese
                og_name, og_code = text["pt"] , "pt"
                return og_name , og_code
            if lang == 8: # return to main menu
                return welcome() 
            else:
                raise ValueError() 
        except ValueError:  
            print(text["wrong_answer"])
            
#------------------------------------------------------
# ask target language and validate it's notthe same as source language    
        
def ask_lang_to():
    global og_name, og_code, to_name, to_code
    
    print(text["og_lang_comp"].format(text[og_code]))
    print(text["to_lang"])
    print(text["ask_lang"])
    while True:
        print(text["to_options"])
        try:
            lang = int(input())
            if lang == 1: # catalan
                if og_code == "ca": # comprovation to prevent transtaling from catalan to catalan
                    print(text["lang_to_error"].format(text[og_code], text["ca"]))
                else:
                    return text["ca"], "ca"
            if lang == 2: # spanish
                if og_code == "es":
                    print(text["lang_to_error"].format(text[og_code], text["es"]))
                else:
                    return text["es"], "es"
            if lang == 3: # change source language
                og_name, og_code = ask_lang_og()
                return ask_lang_to()
            if lang == 4: # return to main menu
                return welcome() 
            else:
                raise ValueError()
        except ValueError:
            print(text["ask_lang"])

#------------------------------------------------------
# The language confirmation

def lang_collect():
    global og_name, og_code, to_name, to_code

    while True:
        og_name, og_code = ask_lang_og()
        if og_name is None:
            print(text["go_back"])
            continue

        to_name, to_code = ask_lang_to()
        if to_name is None:
            print(text["go_back"])
            continue

        while True: # loop to confirm language combination
            print(text["lang_confirmation"].format(og_name, to_name))
            print(text["yes_no"])  # yes, no, main menu
            try:
                ans = int(input())
                if ans == 1:
                    return  # yes --> out
                elif ans == 2:
                    print(text["go_back"])
                    break  # no --> asks language combination again
                elif ans == 3:
                    welcome()
                    return None, None
            except ValueError:
                print(text["ask_lang"])  # invalid option

            
            
#------------------------------------------------------
# File import

# gets the file path so it can be processed later
def find_file():
    print(text["format_intro"])
    time.sleep(1) # this way user can read the print before the gui is open
    # load supported formats and connector 
    with open("modifiables/formats.json", encoding="utf-8") as f:
        formats = json.load(f)

    supported_formats = formats["supported_formats"]
    connector = text["connector"]
    
    # build format string, so it prints "suported formats: 1, 2 and 3 and if more formats there's no need to modify
    if len(supported_formats) > 1: # if there are at least two formats
        formats_str = ", ".join(supported_formats[:-1]) + f" {connector} " + supported_formats[-1]
    else:
        formats_str = supported_formats[0] # in case there's only one format
            
    while True:
        
        print(text["formats_supported"].format(formats_str)) 
        
        root = Tk()
        root.withdraw()

        root.call('wm', 'attributes', '.', '-topmost', True)
        root.after(0, root.lift)  # makes window appear in the front
        root.after(0, root.focus_force)  
    
        path = askopenfilename(  # open file explorer that only shows supported formats
            filetypes=[("Documents", " ".join(f"*{ext}" for ext in supported_formats))],
            title=text["ask_file"]
        )
        
        root.destroy()  # close secret window
        
        if path:
            print(text["chosen_file"].format(os.path.basename(path))) #if the file is correct, checks
            print(text["confirm_file"]) 
            print(text["yes_no_file"]) 
            while True:
                try:
                    ans = int(input())
                    if ans == 1: # if yes, code continues
                        return path
                    elif ans == 2: # if no, opens the file explorer again
                        print(text["repeat_select"])    
                        break 
                    elif ans == 3: # in case user wants go go back to main menu
                        welcome()
                        return None
                    else:
                        print(text["wrong_answer"])
                        print(text["yes_no_file"]) 
                except ValueError:
                    print(text["wrong_answer"])
        else:
            print(text["no_file"])
            while True:
                print(text["file_options"])  # new file, go  back to main menu
                try:
                    ans = int(input())
                    if ans == 1: # chose new file
                        print(text["repeat_select"])
                        break  
                    elif ans == 2: # goes back to main menu
                        welcome()
                        return None
                    else:
                        print(text["wrong_answer"])
                except ValueError:
                    print(text["wrong_answer"])
#------------------------------------------------------

def tokenize_txt(path):
    with open(path, encoding='utf-8') as f:
       raw_text = f.read()
    return word_tokenize(raw_text)
#------------------------------------------------------
# functions to process .pdf and .docx
def pdf_to_text(path): # in case user imports a pdf
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def docx_to_text(path): #in case user imports a docx
    doc = Document(path)
    return " ".join([p.text for p in doc.paragraphs])
#------------------------------------------------------
# actually opens the file
def open_file(path): 
    try:
        if path.endswith(".pdf"):
            return pdf_to_text(path)
        elif path.endswith(".docx"):
            return docx_to_text(path)
        elif path.endswith(".txt"): # python can work with txt 
            return open(path, encoding="utf-8").read()
        else:
            print(text["invalid_format"])
            return None
    except Exception as e:
        print(text["file_read_error"].format(str(e)))
        return None
#------------------------------------------------------
# tokenizes maintaining wordds with - or '
def text_tokenizer(text): 
    pattern = r"\b[\w'-]+\b"
    raw_tokens = re.findall(pattern, text)
    return [t for t in raw_tokens if re.search(r"\w", t)]
#------------------------------------------------------
# loads stopwords so later there can be la language check
def load_stopwords(): 
    stopw_dict = {
        "ca": tokenize_txt("stopwords/ca_stopwords.txt"), # there's no official catalan stopwords list in nltk, so one from github is used
        "es": stopwords.words("spanish"),
        "en": stopwords.words("english"),
        "fr": stopwords.words("french"),
        "it": stopwords.words("italian"),
        "pt": stopwords.words("portuguese"),
        "de": stopwords.words("german"),
    }
    return stopw_dict
#------------------------------------------------------
# stopwords are typical words from every language. Counting them, the language of the file can be checked
def stopword_lang_count(tokens, stopw_dict):
    lang_counts = {
        lang: sum(1 for t in tokens if t.lower() in stops)
        for lang, stops in stopw_dict.items()  # counts how many stopwords of each kind are there.
    }
    detected = max(lang_counts, key=lang_counts.get) # the one that has most stopwords is the language of the file
    return detected, lang_counts
#------------------------------------------------------
# unites functions above so opens, reads, tokenizes and detects language
def mod_file(path): 
    text_raw = open_file(path)
    if text_raw is None:
        return None, None
    tokens = text_tokenizer(text_raw)
    stopw_dict = load_stopwords()
    detected_lang, counts = stopword_lang_count(tokens, stopw_dict)
    return tokens, detected_lang
#------------------------------------------------------
 # checks if the language given by user is the same as the one detected
def lang_check(tokens, detected_lang):
    global og_code, og_name

    if detected_lang != og_code: # triggered in case they don't match (if everything is okay nothing happens)
        detected_lang_name = text[detected_lang]
        og_lang_name = text[og_code]
        to_lang_name = text[to_code]

        print(text["lang_mismatch"].format(detected_lang_name, detected_lang_name, to_lang_name))
        print(text["yes_change_back"])

        while True:
            try:
                ans = int(input())
                if ans == 1: # updates the language variables
                    og_code = detected_lang
                    og_name = detected_lang_name
                    break
                elif ans == 2:
                    return find_file()  # repeats import process
                elif ans == 3:
                    return welcome()  # goes back to main menu
                else:
                    print(text["wrong_answer"])
                    print(text["yes_change_back"])
            except ValueError:
                print(text["wrong_answer"])
                print(text["yes_change_back"])
    
#------------------------------------------------------
# deletes punctuation marks, since the program would also count them as words 
def no_punctuation (file): 
    only_p = [word for word in file if word not in punctuation] 
    return only_p

#------------------------------------------------------
# time and tariffs

def trad_time(length, prod_trad, prod_rev):
    # Time = translation time + revision time + buffer
    t = (length / prod_trad) + (length / prod_rev) + 2
    if t != int(t):
        t += 1
    return round(t)
#------------------------------------------------------
def pe_time(length, prod_pe, prod_rev):
    # Time = postedition time + revision time + buffer
    t = (length / prod_pe) + (length / prod_rev) + 2
    if t != int(t):
        t += 1
    return round(t)
#------------------------------------------------------
def time_tariff(og_code, to_code, length, text):
    # Load tariff and productivity data from json file
    import json
    with open("modifiables/tariffs.json", encoding="utf-8") as f:
        data = json.load(f)

    tariffs = data["tariffs"]
    prod = data["productivity"]
    prod_trad = prod["translation"]
    prod_pe = prod["postedition"]
    prod_rev = prod["revision"]

    # Search for a valid language pair in tariffs
    for item in tariffs:
        sources = item["combination"]
        targets = item.get("target", sources)
        if og_code in sources and to_code in targets:
            return {
                "translation": {
                    "price": round(item["translation"] * length, 2),
                    "days": trad_time(length, prod_trad, prod_rev)
                },
                "postedition": {
                    "price": round(item["postedition"] * length, 2),
                    "days": pe_time(length, prod_pe, prod_rev)
                },
                "currency": text["currency"]
            }

    return None  # no match found
#------------------------------------------------------

def ask_service(results, text):
    trad_price = results["translation"]["price"]
    trad_days = results["translation"]["days"]
    pe_price = results["postedition"]["price"]
    pe_days = results["postedition"]["days"]
    currency = text["currency"]
    time.sleep(1)
    print(text["tariffs"].format( trad_price, currency, trad_days, pe_price, pe_days))

    while True:
        print(text["service_ask"])
        print(text["service_choice"])
        try:
            ans = int(input())
            if ans == 1:
                return "translation"
            elif ans == 2:
                return "postedition"
            elif ans == 3:
                welcome()
                return None
        except ValueError:
            print(text["wrong_answer"])
#------------------------------------------------------
def get_info():
    while True:
        print(text["ask_info"])

        while True:
            name = input(text["name"]).strip()
            if re.match(r"^[A-Za-zÀ-ÿ\u00f1\u00d1\s'-]+$", name):
                break
            else:
                print(text["name_invalid"])
        
        while True:
            surname = input(text["surname"]).strip()
            if re.match(r"^[A-Za-zÀ-ÿ\u00f1\u00d1\s'-]+$", surname):
                break
            else:
                print(text["surname_invalid"])
        
        while True:
            email = input(text["email"]).strip()
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                break
            else:
                print(text["email_invalid"])
        
        while True:
            phone = input(text["phone"]).strip()
            if re.match(r"^\+?\d[\d\s]{8,20}$", phone):
                break
            else:
                print(text["phone_invalid"])


        print("\n--- " + text["info_summary"] + " ---")
        print(f"{text['name']} {name}")
        print(f"{text['surname']} {surname}")
        print(f"{text['email']} {email}")
        print(f"{text['phone']} {phone}")
        print(text["confirm_data"])

        try:
            ans = int(input())
            if ans == 1:
                return {
                    "name": name,
                    "surname": surname,
                    "email": email,
                    "phone": phone
                }
            elif ans == 2:
                print(text["repeat_info"])
                continue
            elif ans == 3:
                return None
            else:
                print(text["wrong_answer"])
        except ValueError:
            print(text["wrong_answer"])

#------------------------------------------------------
def create_client_folder(info, filename, lang_combo, word_count, service, days, price, original_path):


    base_dir = "client_orders"
    os.makedirs(base_dir, exist_ok=True)

    # client id
    existing = [d for d in os.listdir(base_dir) if d.startswith("client_") and os.path.isdir(os.path.join(base_dir, d))]
    numbers = [int(d.split("_")[1]) for d in existing if d.split("_")[1].isdigit()]
    next_num = max(numbers, default=0) + 1

    folder_name = f"client_{next_num}"
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path)

    # creates client_X.txt
    info_filename = f"client_{next_num}.txt"
    info_path = os.path.join(folder_path, info_filename)
    today = date.today().isoformat()
    currency = text["currency"]

    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"{text['client_name']} {info['name']} {info['surname']}\n")
        f.write(f"{text['client_email']} {info['email']}\n")
        f.write(f"{text['client_phone']} {info['phone']}\n\n")
        f.write(f"{text['file_name']} {filename}\n")
        f.write(f"{text['lang_pair']} {lang_combo}\n")
        f.write(f"{text['word_count']} {word_count}\n")
        f.write(f"{text['service_type']} {service}\n")
        f.write(f"{text['delivery_days']} {days}\n")
        f.write(f"{text['total_price']} {price} {currency}\n")
        f.write(f"{text['date']} {today}\n")

    # copies original file to folder
    try:
        shutil.copyfile(original_path, os.path.join(folder_path, filename))
    except Exception:
        print(text["file_copy_error"].format(filename))


#------------------------------------------------------
# calls all of the functions for the assessment process
def calculator():
    global og_name, og_code, to_name, to_code

    lang_collect() # gets language combination

    file = find_file() # gets file
    if not file:
        return  # in case user goes back

    tokens, detected_lang = mod_file(file) # opens file and tokenizes 
    if tokens is None:
        return

    lang_check(tokens, detected_lang) # using stopwords checks if og_lang is correct

    clean = no_punctuation(tokens) # removes punctuation so word count is accurate
    word_count = len(clean) # word count
    print(text["processing_done"]) 
    results = time_tariff(og_code, to_code, word_count, text)
    if not results:
        print(text["no_tariff_found"])
        return

    # Ask user which service they want
    service = ask_service(results, text)
    
    if not service:
        return
    
    client_info = get_info()
    if not client_info:
        return
    
    price = results[service]["price"]
    
    create_client_folder(
        info=client_info,
        filename=os.path.basename(file),
        lang_combo=f"{og_name} > {to_name}",
        word_count=word_count,
        service="traducció" if service == "translation" else "postedició",
        days=results[service]["days"],
        price=price,
        original_path=file
    )
    
    # Després de crear la carpeta
    print(text["invoice_notice"])
    print(text["thanks_message"])
    print(text["thanks_options"])
    
    while True:
        try:
            opt = int(input())
            if opt == 1:
                print(text["bye"])
                sys.exit(0)
            elif opt == 2:
                return welcome()
            else:
                print(text["wrong_answer"])
        except ValueError:
            print(text["wrong_answer"])


if __name__ == "__main__":
    welcome()