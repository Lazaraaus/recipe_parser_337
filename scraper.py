import requests
import sys
import unicodedata
# from parse_ingredients import parse_ingredient
# from recipe_scrapers import scrape_me

from bs4 import BeautifulSoup


###### FIRST PASS AT A HOMEMADE PARSER ######

#################
# Yjaden  Notes #
#################
# 11/18
# Added: corpora for ingredients, need to add more specific MEATS; steak, types of steak, etc
# Added: corpora for ACTIONS
# Added: corpora for INGREDIENT_DESCRIPTORS
# Added: parseIngredients - Function to work in tandem with parseIngredient to build ingredient_dict
# Added: parseIngredient - Removed the Break statement and rest construction in Units check. Added check for descriptors. Added ingredient matching. 
# Added: parseInstructions - Constructs a Dict of all steps in tandem with parseInstruction
# Added: parseInstruction - Constructs a dict of a specific step -> ingredient, actions, tools, time

# 11/19
# Added: 'and' catch to parseIngredient
# Concerns: Units like 'to taste' are going uncaught. Could check ingrs_dict['rest'] string for it but would rather it get caught as a unit. 

# Corpora for types of Ingredients
MEATS = ['pork', 'pork tenderloin','pork chop', 'chicken', 'chicken breast', 'chicken wings', 'chicken thighs', 'beef', 'ground beef', 'sausage', 'turkey', 'ground turkey' 'ham', 'goat', 'lamb'] # Need to add specific cuts -> pork tenderloin, chicken breast, etc
GAME_MEATS = ['pheasant', 'rabbit', 'bison', 'duck', 'goose', 'venison', 'quail']
FISH = ['tuna', 'catfish', 'trout', 'sardines', 'snapper', 'bass', 'cod', 'squid', 'blowfish', 'fugu', 'octopus', 'salmon', 'swordfish', 'mahi mahi', 'snapper', 'tilapia', 'red snapper', 'herring', 'anchovies', 'haddock', 'flounder', 'rainbow trout', 'alaskan pollock', 'pacific halibut', 'halibut', 'pike', 'atlantic mackerel', 'mackerel', 'branzino', 'fish']
SHELLFISH = ['lobster', 'clam', 'crab', 'oyster', 'shrimp', 'crawfish', 'mussel', 'scallop', 'shellfish']
FRUITS = ['apple', 'banana', 'cherry', 'blueberry', 'raspberry', 'berry', 'strawberry', 'pineapple', 'plum', 'grapes', 'lychee', 'passionfruit', 'blackberry', 'orange', 'lime', 'lemon', 'citrus', 'grapefruit', 'coconut', 'watermelon', 'peach', 'pear']
VEGETABLES = ['broccoli', 'onion', 'shallot', 'leek', 'fennel', 'green bean', 'bell pepper', 'spinach', 'cabbage', 'asparagus', 'greens', 'pea', 'green pea', 'tomato', 'potato', 'sweet potato', 'carrot', 'celery', 'mushroom', 'cucumber', 'pickles', 'vegetable']
GRAINS = ['rice', 'quinoa', 'maize', 'cornmeal', 'barley', 'wheat', 'oat', 'buckwheat', 'bulgur', 'millet', 'rye', 'amaranth']
SEEDS = ['sunflower seeds', 'flaxseeds', 'poppy seeds', 'pumpkin seeds', 'caraway seeds', 'chia seeds', 'sesame seeds', 'nigella seeds']
NUTS = ['almond', 'peanut', 'peanut butter', 'walnut', 'pecans', 'black walnut', 'chestnuts', 'cashews', 'hazelnuts', 'pistachios', 'brazil nuts', 'macadamia nuts', 'pine nuts', 'baru nuts', 'acorns', 'hickory nuts', 'pili nuts', 'sacha inchi', 'tiger nuts']
FLOURS = ['flour', 'wheat flour', 'pastry flour', 'cake flour', 'bread flour', 'gluten-free flour', 'gluten free flour', 'sprouted flour', 'rice flour', 'soy flour', 'noodle flour', 'corn flour']
CARBOHYDRATES = ['noodles', 'noodle', 'pasta', 'tortilla', 'tortillas', 'bread', 'breads', 'bread crumbs' 'loaves', 'loaf', 'macaroni', 'spaghetti', 'farfalle', 'angel hair', 'rotini', 'penne', 'lasagna', 'cannelloni', 'elbow macaroni', 'gnocchi', 'bow-tie', 'ravioli', 'tortellini']
BEANS = ['black beans', 'cannellini beans', 'kidney beans', 'garbanzo beans', 'navy beans', 'great northern beans', 'pinto beans', 'lima beans', 'fava beans', 'mung beans', 'red beans', 'soybeans', 'flageolet beans', 'black-eyed peas', 'lentils', 'chickpeas']
DAIRY = ['milk', 'yogurt', 'cheese', 'butter', 'cream', 'heavy cream', 'sour cream', 'whipped cream', 'egg', 'eggs', 'ice cream']
OILS = ['olive oil', 'vegetable oil', 'coconut oil', 'sesame oil', 'canola oil', 'cooking oil', 'amaranth oil', 'oil']
HERBS = ['basil', 'bay leaf', 'cilantro', 'chives', 'dill', 'lemongrass', 'lemon grass', 'lavender', 'marjoram', 'mint', 'rosemary', 'sage', 'oregano', 'parsley', 'thyme', 'tarragon', 'savory', 'rose', 'garlic']
SPICES = ['salt', 'black pepper', 'anise', 'caraway', 'cardamom', 'celery seed', 'chile', 'chili powder', 'cayenne', 'poppy seed', 'cinnamon', 'cloves', 'coriander', 'cumin', 'dill seed', 'fenugreek', 'ginger', 'ginger root', 'juniper berries', 'mace', 'nigella', 'nutmeg', 'peppercorns', 'saffron', 'star anise', 'sumac', 'turmeric', 'cajun', 'cajun blackened', 'shichimi', 'togarashi', 'ginger', 'sesame seed', 'curry powder', 'masala', 'five spice', 'jerk', 'baharat', 'zhug','paprika', 'chicken bouillon', 'beef bouillon', 'seasoning']
SWEETS = ['chocolate', 'cocoa', 'chocolate sauce', 'blueberry syrup', 'fruit caramel', 'caramel', 'syrup', 'raspberry preserves', 'peach preserves', 'grape preserves', 'blueberry preserves' 'mango preserves', 'pear preserves']
EXTRACTS = ['vanilla extract', 'orange extract', 'coffee extract', 'lemon extract', 'almond extract', 'peppermint extract', 'cherry extract', 'butter extract', 'maple extract', 'coconut extract', 'banana extract', 'rum extract']
SUGARS = ['powdered sugar', 'white sugar', 'sugar', 'brown sugar', 'confectioners sugar', 'coconut sugar', 'brown rice sugar', 'honey', 'agave', 'cane sugar', 'coarse sugar', 'pearl sugar', 'turbinado', 'muscovado sugar']
CONDIMENTS = ['ketchup', 'mustard', 'mayo', 'mayonnaise', 'vinegar']
SAUCES = ['enchilada sauce', 'chimichurri', 'tahini sauce', 'tahini', 'pesto', 'peanut sauce', 'roasted red pepper sauce', 'soy sauce', 'barbecue sauce', 'hot sauce', 'tomato sauce', 'romesco sauce', 'cashew sauce', 'teriyaki sauce', 'nuoc cham', 'charmoula', 'yangnyeom sauce', 'buffalo sauce', 'salsa', 'roja salsa', 'salsa roja', 'tomatillo salsa', 'salsa tomatillo', 'avocado salsa', 'tartar sauce', 'marinara', 'alfredo', 'alfredo sauce', 'romesco', 'hollandaise', 'vinaigrett', 'coulis', 'cheese sauce', 'duck sauce', 'salad dressing', 'gravy', 'mushroom gravy', 'worcestershire sauce', 'aioli', 'garlic sauce', 'remoulade', 'fish sauce', 'garum', 'bagna cáuda', 'sriracha sauce', 'tabasco sauce', 'tabasco', 'bolognese', 'carbonara', 'ragú', 'picadillo', 'pico de gallo', 'salsa verde', 'tkemali', 'tkemali sauce', 'cranberry sauce', 'mango sauce', 'peace sauce', 'plum sauce', 'mushroom sauce', 'ygourt sauce', 'tziki', 'tziki sauce', 'strawberry sauce', 'harissa', 'oyster sauce', 'mirin', 'wine sauce', 'sweet bean sauce', 'sauce', 'green goddess dressing', 'italian dressing', 'ranch dressing', 'caesar dressing' ,'balsamic vinaigrette', 'thousand island dressing', 'ginger sauce', 'beef broth', 'chicken broth']
MISC = ['gelatin', 'xantham gum', 'water']
# Mass Corpus of all ingredients
ALL_INGREDIENTS = MEATS + GAME_MEATS + FISH + SHELLFISH + FRUITS + VEGETABLES + GRAINS + SEEDS + NUTS + FLOURS + CARBOHYDRATES + BEANS + DAIRY + OILS + HERBS + SPICES + SWEETS + EXTRACTS + SUGARS + CONDIMENTS + SAUCES + MISC
# Unit Of Measurements
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
    "pinch", 
    "dash", 
    "cube",
    "pound"
]

# Time Words
TIMES = ['second', 'seconds', 'minute', 'minutes', 'hour', 'hours', 'overnight', 'over night']
# Tool Words
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
# Action2Tool dict
ACTION_TO_TOOL = {'carve': 'carving knife', 'cut': 'knife', 'dice': 'knife',
                  'chop': 'knife', 'brush': 'brush', 'slice': 'knife', 'chopped': 'knife', 'peeled': 'peeler', 'melted': 'microwave'}
# Action Words 
ACTIONS = ['mix', 'whisk', 'stir', 'toss', 'bake', 'shake', 'preheat', 'heat', 'saute' 'chop', 'slice', 'cut', 'mince', 'grate', 'crush', 'squeeze', 'blend', 'mash', 'fry', 'boil', 'roast', 'broil']
# Descriptor Words
INGREDIENT_DESCRIPTOR = ['fresh', 'good', 'heirloom', 'virgin', 'extra virgin', 'ripe', 'organic', 'seedless', 'chopped', 'minced', 'uncooked', 'grated', 'frozen', 'mixed', 'baby', 'sliced', 'cubed']


# Containers for replacement/generation 
# Healthy, Vegetarian, Cuisine, etc
# Maybe a dict of lists


# Parsing Functions
def parseIngredients(ingrs: list) -> dict:
    """ Function to parse list of ingredients into a dict"""
    # Create Dict to hold ingrs
    ingrs_dict = {}
    # Loop through ingrs
    for ingr in ingrs:
        # Parse individual ingr
        quant, unit, descriptor_list, ingredient, rest = parseIngredient(ingr)
        # Assign ingr as key, ingr attribute list as value
        ingrs_dict[ingredient] = [quant, unit, descriptor_list, rest]

    # Return ingrs dict 
    return ingrs_dict

def parseIngredient(ingr: str) -> str:
    quant, unit, rest, descriptor_list, ingredient = None, None, None, [], None
    # Find Ingr Match in whole str, splitting messes up matching. I.E., 'soy sauce' becomes 'soy', 'sauce'
    # Loop through all ingredients
    # Finding smallest matching str, need to find largest matching str
    # I think I can check for matches that have a larger length than the previous
    # Might not need too, recipes tend to only use the term 'pork' in instructions to refer to the ingredient 'pork tenderloin' 
    # Just add an additional value to the ingrs_dict[ingredient] -> alias_list
    for pos_ingr in ALL_INGREDIENTS:
        # if any match
            if pos_ingr in ingr:
                # Catch 'and' in ingr. Has to be a better way to do this. 
                if 'and' in ingr:
                    # Split into list w idxs
                    split_ingrs = ingr.split()
                    split_ingr_w_index = enumerate(split_ingrs)
                    for i,v in split_ingr_w_index:
                        if v == 'and':
                            # Get preceding and anteceding elements
                            first_ingr = split_ingrs[i - 1]
                            second_ingr = split_ingrs[i + 1]
                            # Concat to ingredient
                            ingredient = first_ingr + ' and ' +  second_ingr
                            break 
                else: 
                    # Set as ingredient, break
                    ingredient = pos_ingr
                    break
        
    # Split List into Tokens
    words = ingr.split()
    for (i, w) in enumerate(words):
        word = w.lower()
        if w.isnumeric():
            n = unicodedata.numeric(w) if len(w) == 1 else float(w)
            quant = quant + n if quant else n
        elif word in UNITS or (word[-1] == "s" and word[:-1] in UNITS):
            unit = word
            #rest = " ".join(words[i + 1:])
            #break
        # Check for descriptors
        elif word in INGREDIENT_DESCRIPTOR:
            descriptor_list.append(word)
        else:
            rest = " ".join(words[i:])
            break
    return quant, unit, descriptor_list, ingredient, rest

def parseInstructions(instructions: str) -> dict:
    # I think I have to add ingredients strs, definitely have to. I'm a dunce. Can add keys from ingr_dict 
    """ Function for Parsing Instructions"""
    # Create dict to hold instruction
    instruction_dict = {}
    for i,v in enumerate(instructions):
        instruction_dict[i + 1] = parseInstruction(v)

    # Return Dict
    return instruction_dict

def parseInstruction(instr: str) -> dict:
    # Needs ingredients for recipe as input
    """ Function for parsing individual instructions"""
    # Create dict for instruction
    instr_dict = {}
    # Create keys for necessary data
    instr_dict['ingredients'] = []
    instr_dict['tools'] = []
    instr_dict['action'] = []
    instr_dict['time'] = []
    # Split instruction into tokens, should we use Spacy to tokenize AND tag? 
    # Verbs == Actions, Tools == Nouns
    # Could also mutate an entity ruler and do entity recognition
    # String search for now
    toks = instr.split()
    # Loop through tokens
    for i,v in enumerate(instr):
        # Check for time
        if v in TIMES:
            # append v and instr[i - 1] -> '10 minutes'
            instr_dict['time'].append(v + ' ' + instr[i - 1])
        # Check for Tools
        # Check for Actions
        # Check for ingredients

    # Return Dict
    pass


def parseTools(txt: str) -> list:
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


def scrape(url: str) -> 'tuple[list[str], list[str]]':
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
    url = 'https://www.allrecipes.com/recipe/55151/ravioli-soup/'
    #'https://www.allrecipes.com/recipe/11679/homemade-mac-and-cheese/'
    #'https://www.allrecipes.com/recipe/237335/spicy-sweet-pork-tenderloin/' #sys.argv[1]
    ingredients, instructions = scrape(url)

    # Parse Ingredients Test
    ingr_dict = parseIngredients(ingredients)
    
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
    # scraper = scrape_me(url)
    # print(scraper.ingredients())
    # print(scraper.instructions())


if __name__ == "__main__":
    main()