# Wikipedia Game Bot - gra polegająca na dotarciu do docelowego artykułu poprzez klikanie linków
# Bot używa Google Gemini AI do inteligentnego wyboru najlepszej ścieżki

import requests
from bs4 import BeautifulSoup
import time
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Konfiguracja Google Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Brak klucza API! Utwórz plik .env i dodaj GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def ask_gemini(prompt):
    """Wysyła zapytanie do Gemini AI i zwraca odpowiedź"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Blad API: {e}")
        raise

def get_page_content(url):
    """Pobiera zawartość strony Wikipedii"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Błąd pobierania strony: {e}")
        return None

def extract_links(html, current_url):
    """Wyciąga linki z HTML strony Wikipedii"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Pobierz tytuł strony
    title_tag = soup.find('h1', class_='firstHeading')
    title = title_tag.text if title_tag else "Nieznany tytuł"
    
    # Znajdź główną treść artykułu
    content = soup.find('div', id='mw-content-text')
    if not content:
        return title, []
    
    candidates = []
    links = content.find_all('a', href=True)
    
    for link in links:
        href = link.get('href')
        text = link.text.strip()
        
        if not href or not text:
            continue
        if text.startswith('[') and text.endswith(']'):  # Pomiń [1], [2], [a]
            continue
        if len(text) <= 2:  # Pomiń bardzo krótkie teksty
            continue
        
        # Sprawdź czy to link do artykułu Wikipedii
        if href.startswith('/wiki/') and ':' not in href.split('/wiki/')[1]:
            full_url = f"https://pl.wikipedia.org{href}"
            if full_url != current_url:
                candidates.append((text, full_url))
    
    return title, candidates

target = input("Podaj haslo do wyszukania: ")

# Start z losowego artykułu
current_url = "https://pl.wikipedia.org/wiki/Special:Random"
response = requests.get(current_url, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
current_url = response.url  # Pobierz URL po przekierowaniu

MAX_STEPS = 30  # Maksymalna liczba kroków
visited = set()  # Zbiór odwiedzonych URL (zapobiega zapętleniom)
path = []  # Ścieżka przejścia (lista tytułów)

# Główna pętla gry
for step in range(MAX_STEPS):
    time.sleep(0.5)  # Krótka przerwa, aby nie obciążać serwera
    
    # Pobierz zawartość strony
    html = get_page_content(current_url)
    if not html:
        print("Nie udało się pobrać strony!")
        break
    
    # Wyciągnij tytuł i linki
    title, candidates = extract_links(html, current_url)
    print(f"Krok {step+1}: {title}")
    path.append(title)
    
    # Sprawdź czy to strona docelowa
    if target.lower() in title.lower():
        print(f"Znaleziono stronę docelową: {title}")
        break
    
    visited.add(current_url)
    
    # Filtruj linki - usuń już odwiedzone
    candidates = [(text, url) for text, url in candidates if url not in visited]
    
    if not candidates:
        print(f"Brak dalszych linków!")
        break
    print(f"Znaleziono {len(candidates)} kandydatów.")
    
    # Sprawdź czy jest bezpośredni link do celu
    found_direct = False
    for text, url in candidates:
        if target.lower() in text.lower():
            print(f"Znaleziono bezposredni link do celu: {text}")
            current_url = url
            found_direct = True
            break
    
    if not found_direct:
        # Ogranicz do 50 linków dla AI (oszczędność kosztów API)
        candidates_limited = candidates[:50]
        num_links = len(candidates_limited)
        
        # Zbuduj prompt dla AI
        prompt = f"""You are playing the Wikipedia Game - a popular educational puzzle where the goal is to navigate from one Wikipedia article to another by clicking links. This is a legitimate game played by millions to learn about connections between topics.

Current article: '{title}'
Target article: '{target}'

Choose the NUMBER (1-{num_links}) of the link that would best help reach the target article. Consider semantic connections, geographical proximity, or categorical relationships.

Available links:
"""
        for i, (text, url) in enumerate(candidates_limited, 1):
            prompt += f"{i}. {text}\n"
        prompt += f"\nRespond with ONLY the number (1-{num_links}). If no link seems related, choose the most general or geographical one."
        
        answer = ask_gemini(prompt)
        print("Gemini wybral:", answer)
        
        # Parsowanie odpowiedzi AI i przejście do wybranego linku
        try:
            digits_str = ''.join([ch for ch in answer if ch.isdigit()])
            if digits_str:
                num = int(digits_str)
                if 1 <= num <= len(candidates_limited):
                    idx = num - 1
                    text, url = candidates_limited[idx]
                    print(f"Wybieram link #{num}: {text}")
                    current_url = url
                else:
                    print(f"Numer {num} spoza zakresu, wybieram pierwszy link.")
                    current_url = candidates_limited[0][1]
            else:
                print("Brak numeru w odpowiedzi, wybieram pierwszy link.")
                current_url = candidates_limited[0][1]
        except Exception as e:
            print(f"Blad parsowania: {e}, wybieram pierwszy link.")
            current_url = candidates_limited[0][1]

# Podsumowanie
print("\nSciezka:")
for i, t in enumerate(path, 1):
    print(f"{i}. {t}")