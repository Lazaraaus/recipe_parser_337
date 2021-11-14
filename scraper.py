import requests
import sys
import unicodedata
from parse_ingredients import parse_ingredient

from bs4 import BeautifulSoup


###### FIRST PASS AT A HOMEMADE PARSER ######

UNITS = [
    "teaspoon",
    "tablespoon",
    "cup",
    "fluid ounce",
    "ounce",
    "gallon",
    "quart",
    "pint",
    "clove",
]


def parseIngredient(ingr: str):
    quant, unit, rest = None, None, None
    words = ingr.split()

    for (i, w) in enumerate(words):
        word = w.lower()
        if w.isnumeric():
            n = unicodedata.numeric(w) if len(w) == 1 else float(w)
            quant = quant + n if quant else n
        elif word in UNITS or (word[-1] == "s" and word[:-1] in UNITS):
            unit = word
            rest = " ".join(words[i + 1:])
            break
        else:
            rest = " ".join(words[i:])
            break
    return quant, unit, rest

##Alternative Ingredient Parser

#def parseIngredient(string: str):
#    result = parse_ingredient(string)
#    return result


###### SCRAPER ######


def clean_text(txt: str) -> str:
    """Replace all white space with single space."""
    return " ".join(txt.strip().split())


def scrape(url: str) -> tuple[list[str], list[str]]:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    ingr_class = "ingredients-item-name"
    ingr_tags = soup("span", class_=ingr_class)
    ingredients = [clean_text(ingr.text) for ingr in ingr_tags]

    instr_class = "subcontainer instructions-section-item"
    instr_tags = soup("li", class_=instr_class)
    instructions = [clean_text(instr.div.div.p.text) for instr in instr_tags]
    
    return ingredients, instructions


def main():
    url = sys.argv[1]
    ingredients, instructions = scrape(url)
    
    for ingr in ingredients:
        print(ingr)
    print()

    #Steps - Add parsed ingredients, tools, methods etc.
    steps = 1
    for instr in instructions:
        print("Step " + str(steps) + ":")
        print(instr)
        steps += 1


if __name__ == "__main__":
    main()