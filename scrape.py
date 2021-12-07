import requests
from bs4 import BeautifulSoup
import sys

###### SCRAPER ######
def clean_text(txt: str) -> str:
    """Replace all white space with single space."""
    return " ".join(txt.strip().split())

def scrape(url: str) -> 'tuple[list[str], list[str]]':
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    title = soup("h1")[0].text

    ingr_class = "ingredients-item-name"
    ingr_tags = soup("span", class_=ingr_class)
    ingredients = [clean_text(ingr.text) for ingr in ingr_tags]

    instr_class = "subcontainer instructions-section-item"
    instr_tags = soup("li", class_=instr_class)
    instructions = [clean_text(instr.div.div.p.text) for instr in instr_tags]
    
    return title, ingredients, instructions