import requests
import sys
import unicodedata
from parse_ingredients import parse_ingredient
from recipe_scrapers import scrape_me

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

TOOLS = ['pan', 'bowl', 'baster', 'saucepan', 'knife', 'oven', 'beanpot', 'chip pan', 'cookie sheet', 'cooking pot', 'crepe pan', 'double boiler', 'doufeu',
         'dutch oven', 'food processor', 'frying pan', 'skillet', 'griddle', 'karahi', 'kettle', 'pan', 'pressure cooker', 'ramekin', 'roasting pan',
         'roasting rack', 'saucepansauciersaute pan', 'splayed saute pan', 'souffle dish', 'springform pan', 'stockpot', 'tajine', 'tube panwok',
         'wonder pot', 'pot', 'apple corer', 'apple cutter', 'baster', 'biscuit cutter', 'biscuit press', 'baking dish', 'bread knife', 'browning tray',
         'butter curler', 'cake and pie server', 'cheese knife', 'cheesecloth', 'knife', 'cherry pitter', 'chinoise', 'cleaver', 'corkscrew',
         'cutting board', 'dough scraper', 'egg poacher', 'egg separator', 'egg slicer', 'egg timer', 'fillet knife', 'fish scaler', 'fish slice',
         'flour sifter', 'food mill', 'funnel', 'garlic press', 'grapefruit knife', 'grater', 'gravy strainer', 'ladle', 'lame', 'lemon reamer',
         'lemon squeezer', 'mandoline', 'mated colander pot', 'measuring cup', 'measuring spoon', 'grinder', 'tenderiser', 'thermometer', 'melon baller',
         'mortar and pestle', 'nutcracker', 'nutmeg grater', 'oven glove', 'blender', 'fryer', 'pastry bush', 'pastry wheel', 'peeler', 'pepper mill',
         'pizza cutter', 'masher', 'potato ricer', 'pot-holder', 'rolling pin', 'salt shaker', 'sieve', 'spoon', 'fork', 'spatula', 'spider', 'tin opener',
         'tongs', 'whisk', 'wooden spoon', 'zester', 'microwave', 'cylinder', 'Aluminum foil', 'steamer', 'broiler rack', 'grate', 'shallow glass dish', 'wok',
         'dish', 'broiler tray', 'slow cooker']

ACTION_TO_TOOL = {'carve': 'carving knife', 'cut': 'knife', 'dice': 'knife',
                  'chop': 'knife', 'brush': 'brush', 'slice': 'knife', 'chopped': 'knife', 'peeled': 'peeler', 'melted': 'microwave'}


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

def parseTools(txt: str):
    recipe_tools = []
    words = txt.split()
    for tool in TOOLS:
        if tool not in recipe_tools:
            if tool in txt:
                recipe_tools.append(tool)
    for word in words:
        if word in ACTION_TO_TOOL:
            recipe_tools.append(ACTION_TO_TOOL[word])
    return recipe_tools

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
        tools = parseTools(ingr)
        print("Tools: ", tools)
    print()

    #Steps - Add parsed ingredients, tools, methods etc.
    steps = 1
    for instr in instructions:
        print("Step " + str(steps) + ":")
        print(instr)
        tools = parseTools(instr)
        print("Tools: ", tools)
        steps += 1

    #Test Alternative Scraper/Parser
    scraper = scrape_me(url)
    print(scraper.ingredients())
    print(scraper.instructions())


if __name__ == "__main__":
    main()