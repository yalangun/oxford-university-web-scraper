import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE = "https://www.cs.ox.ac.uk"

# 1) Tüm ders linklerini çek
listing_url = "https://www.cs.ox.ac.uk/teaching/courses/"
r = requests.get(listing_url)
soup = BeautifulSoup(r.text, "html.parser")

course_links = []

# Tüm <a> etiketlerini al, teaching/courses içerenleri filtrele
for a in soup.find_all("a"):
    href = a.get("href")
    name = a.text.strip()
    if href and "teaching/courses" in href and len(name) > 1:
        if not href.startswith("http"):
            href = BASE + href
        course_links.append((name, href))

print(f"{len(course_links)} ders bulundu.")


# 2) İstenen başlıklar
TARGET_SECTIONS = [
    "Overview",
    "Learning outcomes",
    "Prerequisites",
    "Synopsis"
]

def extract_section(soup, header_text):
    """
    h2 başlığını bul ve bir sonraki h2 gelene kadar paragraf ve listeleri topla.
    """
    header = soup.find("h2", string=lambda s: s and header_text.lower() in s.lower())
    if not header:
        return ""

    contents = []
    for sibling in header.find_next_siblings():
        # Bir sonraki h2 başlığında dur
        if sibling.name == "h2":
            break

        # Paragrafları al
        if sibling.name == "p":
            contents.append(sibling.get_text(" ", strip=True))

        # Listeleri al
        if sibling.name == "ul":
            for li in sibling.find_all("li"):
                contents.append("- " + li.get_text(" ", strip=True))

    return "\n".join(contents)


# 3) Dersleri gez ve içerik topla
records = []

for name, url in course_links:
    print("Scraping:", name)

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        print("Hata:", name)
        continue

    data = {
        "Course Name": name,
        "URL": url
    }

    # Her başlık için içerik çek
    for section in TARGET_SECTIONS:
        data[section] = extract_section(soup, section)

    records.append(data)


# 4) Excel'e yaz
df = pd.DataFrame(records)
df.to_excel("oxford_cs_courses.xlsx", index=False)

print("Bitti! Dosya oluşturuldu: oxford_cs_courses.xlsx")
