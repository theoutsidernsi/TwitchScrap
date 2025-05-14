from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import datetime
import re
from selenium.webdriver.chrome.options import Options
import os

# Heure du scraping
scrape_jour = datetime.now().strftime("%d-%m-%Y")
scrape_heure = datetime.now().strftime("%H-%M")

# Lancement du navigateur
options = Options()
options.add_argument('--headless')  # important
options.add_argument("--window-size=1920,1080")  # Taille simulée
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get("https://www.twitch.tv/?lang=fr")
driver.set_window_size(1920, 1080)

time.sleep(1)

# Clique sur Parcourir
browse_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-a-target='browse-link'][data-test-selector='top-nav__browse-link']"))
)
browse_btn.click()
time.sleep(1)

# Tri par spectateurs
menu_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "browse-sort-drop-down")))
menu_btn.click()

options_box = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "browse-sort-drop-down-list")))
options = options_box.find_elements(By.CSS_SELECTOR, "[role='option']")
for opt in options:
    if "Spectateurs" in opt.text:
        opt.click()
        break
time.sleep(1)

# Fonction de conversion
def convert_viewers(viewer_text):
    viewer_text = viewer_text.lower().replace("spectateurs", "").replace("spectateur", "").strip()
    viewer_text = viewer_text.replace(',', '.').replace(' ', '')

    try:
        if 'k' in viewer_text:
            return int(float(viewer_text.replace('k', '')) * 1_000)
        elif 'm' in viewer_text:
            return int(float(viewer_text.replace('m', '')) * 1_000_000)
        else:
            return int(float(viewer_text))
    except ValueError:
        return 0
    
# Création du dossier
nom_dossier = f"Scrapping du {scrape_jour} fait le {scrape_heure}"
os.makedirs(nom_dossier, exist_ok=True)

# Chemin complet du fichier CSV à créer
nom_fichier = f"Catégories les plus vues {scrape_jour} {scrape_heure}.csv"
chemin_complet = os.path.join(nom_dossier, nom_fichier)

# Ouverture du CSV
with open(chemin_complet, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Nom", "Spectateurs","Tags","Jour","Heure"])

    cards = driver.find_elements(By.CSS_SELECTOR, "div.game-card")

    # étape utile pour faire le scrapping sur chaque catégorie
    links = [card.find_element(By.TAG_NAME, "a").get_attribute("href") for card in cards]
    print(links)

    for card in cards[:10]:
        try:
            title = card.find_element(By.CSS_SELECTOR, "div[data-test-selector='tw-card-title'] h2").text
            aria_label = card.find_element(By.CSS_SELECTOR, "[aria-label*='spectateurs']").get_attribute("aria-label")
            viewers_text = aria_label.lower().split("spectateurs")[0].strip()
            viewers = convert_viewers(viewers_text)
            tag_buttons = card.find_elements(By.CLASS_NAME, "tw-tag")
            tags = [btn.text for btn in tag_buttons]
            tags_str = " - ".join(tags)
            writer.writerow([title, viewers, tags_str,scrape_jour,scrape_heure])
            print(f"{title} — {viewers} — {tags_str}")
        except Exception as e:
            print(f"Erreur sur une carte : {e}")

def scrapK(lien):
    driver.get(lien)
    time.sleep(1)
    # Tri par spectateurs
    menu_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "browse-sort-drop-down")))
    menu_btn.click()

    options_box = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "browse-sort-drop-down-list")))
    options = options_box.find_elements(By.CSS_SELECTOR, "[role='option']")
    for opt in options:
        if "Spectateurs (décroissant)" in opt.text:
            opt.click()
            break
    time.sleep(1)
    # Cliquer sur le bouton "Langue"
    langue_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[.//div[text()='Langue']]")))
    langue_btn.click()
    time.sleep(1)
    checkbox_label = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//label[.//div[text()='Français']]")))
    checkbox = driver.find_element(By.XPATH, "//label[div[text()='Français']]/preceding-sibling::input")
    # On vérifie si elle est cochée
    if checkbox.is_selected():
        print("✅ La case 'Français' est cochée.")
        time.sleep(2)
    else:
        print("❌ La case 'Français' n'est pas cochée.")
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_label)
        checkbox_label.click()
        time.sleep(2)

    # Création du dossier
    nom_dossier = f"Scrapping du {scrape_jour} fait le {scrape_heure}"
    os.makedirs(nom_dossier, exist_ok=True)

    # Chemin complet du fichier CSV à créer
    nom_propre = re.sub(r'[\\/:*?"<>|]', '-', driver.title)
    nom_fichier = f'{nom_propre} {scrape_jour} {scrape_heure}.csv'
    chemin_complet = os.path.join(nom_dossier, nom_fichier)

    with open(chemin_complet, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Nom du streamer", "Spectateurs", "Tags","Jour","Heure"])
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-a-target^='card-']")))
            cards = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-a-target^='card-']")))

            if not cards:
                print(f"⚠️ Aucun stream trouvé pour {driver.title}. Ligne vide ajoutée.")
                writer.writerow(["", "", "", scrape_jour, scrape_heure])
                driver.back()
                return

            for card in cards[:10]:
                try:
                    # Nom de la chaîne
                    name = card.find_element(By.CSS_SELECTOR, "p[title]").text.strip()

                    # Nombre de spectateurs
                    viewers_text = card.find_element(By.CSS_SELECTOR, "div.tw-media-card-stat").text
                    viewers = convert_viewers(viewers_text)

                    # Tags
                    tag_elements = card.find_elements(By.CLASS_NAME, "tw-tag")
                    tags = [tag.text.strip() for tag in tag_elements]
                    tags_str = " - ".join(tags)

                    writer.writerow([name, viewers, tags_str, scrape_jour, scrape_heure])
                    print(f"{name} — {viewers} — {tags_str}")

                except Exception as e:
                    print(f"Erreur sur une carte : {e}")

        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des cartes pour {driver.title} : {e}")
            writer.writerow(["", "", "", scrape_jour, scrape_heure])
    driver.back()


for link in links[:10]:
    scrapK(link)

driver.quit()
