import requests
import sys

from bs4 import BeautifulSoup


def clean_text(txt: str) -> str:
    """Replace all white space with single space."""
    return " ".join(txt.strip().split())


def getRecipe(url: str) -> tuple[list[str], list[str]]:
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
    getRecipe(url)
    ingredients, instructions = getRecipe(url)
    
    for ingr in ingredients:
        print(ingr)
    print()

    for instr in instructions:
        print(instr)


if __name__ == "__main__":
    main()