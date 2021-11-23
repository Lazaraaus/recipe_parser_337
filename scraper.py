import requests
import sys
import unicodedata
import re
import random
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
# Added: extra descriptors
# Concerns: Units like 'to taste' are going uncaught. Could check ingrs_dict['rest'] string for it but would rather it get caught as a unit. 

# 11/20
# Fixed: Issues w/ 'and' catch. 
# Added: Items to descriptors, items to tools, INGREDIENT_STOP_WORDS list
# Fixed: Bug in parseInstruction -- wasn't properly appending to ingredients list in instr_dict
# Fixed: Bug with parseIngredient matching shortest str and not longest match
# Added: Tokens list to instr_dict 
# Concerns: Need to rework how we're parsing tools. Victor mentioned that a lot of tools are two worders -> 'casserole dish', 'cookie sheet', 'waffle iron'.
#           Need to grab the prefix as well.
# Added: Corpora for Tool prefixes, suffixes, and one word tools
# Fixed: Bug w/ tools not recognized two-word tools properly
# Concerns: Do we need to parse temp info along with time info? I don't think its relevant for anything except doubling/halving recipe

###############
#    NEEDS    #
###############
# Need to add specific cuts to MEATS corpus -> pork tenderloin, chicken breast, flank steak, etc
# Add more items to fruit corpus
# Transformation Functions:
#   What does it mean to be healthy? Less sodium? trans-fat? more vegetables? 
#   For Vegetarian, can we just swap proteins for like Impossible Meat or Tofu? Swap Sauces like bolognese for marinara? 
# Generate Output Functions
#   Kept the original instruction string intact in the instr_dict so we can use that to build a good output. Definitely not larry's preference

# Corpora for types of Ingredients
MEATS = ['pork', 'pork tenderloin', 'pork chop', 'chicken', 'chicken breast', 'chicken wings', 'chicken thighs', 'beef', 'ground beef', 'sausage', 'turkey', 'ground turkey' 'ham', 'goat',
         'lamb', 'steak', 'veal', 'ground veal', 'ground lamb', 'veal chops', 'lamb chops', 'turkey breast', 'filet mignon', 'bacon', 'pastrami', 'roast beef', 'salami', 'corn beef', 'prosciutto', 'ribs', 'ground chuck', 'chicken cutlet', 'pork loin', 'bologna', 'drumsticks', 'ribeye', 'kebab', 'turkey bacon', 'pancetta', 'capicola']
GAME_MEATS = ['pheasant', 'rabbit', 'bison', 'duck', 'goose', 'venison', 'quail']
FISH = ['tuna', 'catfish', 'trout', 'sardines', 'snapper', 'bass', 'cod', 'blowfish', 'fugu', 'salmon', 'swordfish', 'mahi mahi', 'snapper', 'tilapia', 'red snapper', 'herring', 'anchovies', 'haddock', 'flounder', 'rainbow trout', 'alaskan pollock', 'pacific halibut', 'halibut', 'pike', 'atlantic mackerel', 'mackerel', 'branzino', 'fish']
SHELLFISH = ['lobster', 'clam', 'crab', 'oyster', 'shrimp', 'crawfish', 'mussel', 'scallop', 'shellfish', 'octopus', 'squid']
FRUITS = ['apple', 'banana', 'cherry', 'blueberry', 'raspberry', 'berry', 'strawberry', 'pineapple', 'plum', 'grapes', 'lychee', 'passion fruit', 'blackberry', 'orange', 'lime', 'lemon', 'citrus', 'grapefruit', 'coconut', 'watermelon', 'peach', 'pear', 'pumpkin', 'currant', 'nectarine', 'gooseberry', 'boysenberry', 'huckleberry', 'kiwi', 'fig', 'mango', 'apricot', 'tangerine', 'clementine', 'date', 'guava', 'papaya', 'persimmon', 'pomegranate', 'melon', 'cantaloupe', 'honeydew', 'dragonfruit', 'starfruit']
VEGETABLES = ['broccoli', 'onion', 'shallot', 'leek', 'fennel', 'green bean', 'bell pepper', 'spinach', 'cabbage', 'asparagus', 'greens', 'pea', 'green pea', 'tomato', 'potato', 'sweet potato', 'carrot', 'celery', 'mushroom', 'cucumber', 'pickles', 'vegetable']
GRAINS = ['rice', 'quinoa', 'maize', 'cornmeal', 'barley', 'wheat', 'oat', 'buckwheat', 'bulgur', 'millet', 'rye', 'amaranth']
SEEDS = ['sunflower seeds', 'flaxseeds', 'poppy seeds', 'pumpkin seeds', 'caraway seeds', 'chia seeds', 'sesame seeds', 'nigella seeds']
NUTS = ['almond', 'peanut', 'peanut butter', 'walnut', 'pecans', 'black walnut', 'chestnuts', 'cashews', 'hazelnuts', 'pistachios', 'brazil nuts', 'macadamia nuts', 'pine nuts', 'baru nuts', 'acorns', 'hickory nuts', 'pili nuts', 'sacha inchi', 'tiger nuts']
FLOURS = ['flour', 'wheat flour', 'pastry flour', 'cake flour', 'bread flour', 'gluten-free flour', 'gluten free flour', 'sprouted flour', 'rice flour', 'soy flour', 'noodle flour', 'corn flour', 'chestnut flower']
CARBOHYDRATES = ['noodles', 'noodle', 'pasta', 'tortilla', 'tortillas', 'bread', 'breads', 'bread crumbs', 'loaves', 'loaf', 'macaroni', 'spaghetti', 'farfalle', 'angel hair', 'rotini', 'penne', 'lasagna', 'cannelloni', 'elbow macaroni', 'gnocchi', 'bow-tie', 'ravioli', 'tortellini', 'soba noodles', 'udon noodles']
BEANS = ['black beans', 'cannellini beans', 'kidney beans', 'garbanzo beans', 'navy beans', 'great northern beans', 'pinto beans', 'lima beans', 'fava beans', 'mung beans', 'red beans', 'soybeans', 'flageolet beans', 'black-eyed peas', 'lentils', 'chickpeas']
DAIRY = ['milk', 'yogurt', 'cheese', 'butter', 'margarine', 'cream', 'heavy cream', 'sour cream', 'whipped cream', 'egg', 'eggs', 'ice cream']
OILS = ['olive oil', 'vegetable oil', 'coconut oil', 'sesame oil', 'canola oil', 'cooking oil', 'amaranth oil', 'oil']
HERBS = ['basil', 'bay leaf', 'cilantro', 'chives', 'dill', 'lemongrass', 'lemon grass', 'lavender', 'marjoram', 'mint', 'rosemary', 'sage', 'oregano', 'parsley', 'thyme', 'tarragon', 'savory', 'rose']
SPICES = ['salt', 'black pepper', 'anise', 'caraway', 'cardamom', 'celery seed', 'chile', 'chili powder', 'cayenne', 'poppy seed', 'cinnamon', 'cloves', 'coriander', 'cumin', 'dill seed', 'fenugreek', 'ginger', 'ginger root', 'juniper berries', 'mace', 'nigella', 'nutmeg', 'peppercorns', 'saffron', 'star anise', 'sumac', 'turmeric', 'cajun', 'cajun blackened', 'shichimi', 'togarashi', 'ginger', 'sesame seed', 'curry powder', 'masala', 'five spice', 'jerk', 'baharat', 'zhug','paprika', 'chicken bouillon', 'beef bouillon', 'seasoning', 'garlic']
SWEETS = ['chocolate', 'cocoa', 'chocolate sauce', 'blueberry syrup', 'fruit caramel', 'caramel', 'syrup', 'raspberry preserves', 'peach preserves', 'grape preserves', 'blueberry preserves' 'mango preserves', 'pear preserves']
EXTRACTS = ['vanilla extract', 'orange extract', 'coffee extract', 'lemon extract', 'almond extract', 'peppermint extract', 'cherry extract', 'butter extract', 'maple extract', 'coconut extract', 'banana extract', 'rum extract']
SUGARS = ['powdered sugar', 'white sugar', 'sugar', 'brown sugar', 'confectioners sugar', 'coconut sugar', 'brown rice sugar', 'honey', 'agave', 'cane sugar', 'coarse sugar', 'pearl sugar', 'turbinado', 'muscovado sugar']
CONDIMENTS = ['ketchup', 'mustard', 'mayo', 'mayonnaise', 'vinegar']
SAUCES = ['enchilada sauce', 'chimichurri', 'tahini sauce', 'tahini', 'pesto', 'peanut sauce', 'roasted red pepper sauce', 'soy sauce', 'barbecue sauce', 'hot sauce', 'tomato sauce', 'romesco sauce', 'cashew sauce', 'teriyaki sauce', 'nuoc cham', 'charmoula', 'yangnyeom sauce', 'buffalo sauce', 'salsa', 'roja salsa', 'salsa roja', 'tomatillo salsa', 'salsa tomatillo', 'avocado salsa', 'tartar sauce', 'marinara', 'alfredo', 'alfredo sauce', 'romesco', 'hollandaise', 'vinaigrette', 'coulis', 'cheese sauce', 'duck sauce', 'salad dressing', 'gravy', 'mushroom gravy', 'worcestershire sauce', 'aioli', 'garlic sauce', 'remoulade', 'fish sauce', 'garum', 'bagna cáuda', 'sriracha sauce', 'tabasco sauce', 'tabasco', 'bolognese', 'carbonara', 'ragú', 'picadillo', 'pico de gallo', 'salsa verde', 'tkemali', 'tkemali sauce', 'cranberry sauce', 'mango sauce', 'peace sauce', 'plum sauce', 'mushroom sauce', 'ygourt sauce', 'tziki', 'tziki sauce', 'strawberry sauce', 'harissa', 'oyster sauce', 'mirin', 'wine sauce', 'sweet bean sauce', 'sauce', 'green goddess dressing', 'italian dressing', 'ranch dressing', 'caesar dressing' ,'balsamic vinaigrette', 'thousand island dressing', 'ginger sauce', 'beef broth', 'chicken broth']
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
         'dish', 'broiler tray', 'slow cooker', 'saucepan', 'peeler', 'pin', 'frying', 'board', 'foil']

# Tool Prefixes
PREFIXES = ['casserole', 'cookie', 'baking', 'frying', 'rolling', 'souffle', 'sauce', 'saute', 'roasting', 'pastry', 'cutting', 'dutch', 'crepe', 'food', 
            'pressure', 'wonder', 'biscuit', 'measuring', 'pastry', 'pizza', 'broiler', 'slow']
# Tool Suffixes
SUFFIXES = ['dish', 'pan', 'peeler', 'grater', 'timer', 'slicer', 'knife', 'mill', 'tray', 'board', 'boiler', 'pot', 'scraper', 'spoon', 'cup', 'pitter', 
            'baller', 'sifter', 'wheel', 'press', 'oven', 'rack', 'processor', 'cooker', 'pot', 'baller', 'grater', 'brush', 'cutter', 'baster']
# Simple Tools --> one word
SIMPLE_TOOLS = ['bowl', 'saucepan', 'knife', 'oven', 'funnel', 'griddle', 'skillet', 'cheesecloth', 'karahi', 'kettle', 'grinder', 'ramekin',
                 'tajine', 'chinoise', 'cleaver', 'corkscrew', 'mandoline', 'colander', 'tenderiser', 'thermometer', 'nutcracker', 'blender', 'fryer', 
                'masher', 'sieve', 'spatula', 'tongs', 'whisk', 'zester', 'microwave', 'cylinder', 'foil', 'steamer', 'fork', 'wok']
# Action2Tool dict
ACTION_TO_TOOL = {'carve': 'carving knife', 'cut': 'knife', 'dice': 'knife',
                  'chop': 'knife', 'brush': 'brush', 'slice': 'knife', 'chopped': 'knife', 'peeled': 'peeler', 'melted': 'microwave', 'diced':'knife'}
# Action Words 
ACTIONS = ['mix', 'whisk', 'stir', 'toss', 'bake', 'shake', 'preheat', 'heat', 'saute' 'chop', 'slice', 'cut', 'mince', 'grate', 'crush', 'squeeze', 'blend', 'mash', 'fry', 'boil', 'roast', 'broil', 'cook', 'melt', 'sprinkle', 'press', 'tenderize']
ACTIONS = ACTIONS + list(ACTION_TO_TOOL.values())

# Descriptor Words
INGREDIENT_DESCRIPTOR = ['fresh', 'good', 'heirloom', 'virgin', 'extra virgin', 'ripe', 'organic', 'seedless', 'chopped', 'minced', 'uncooked', 'grated', 'frozen', 'mixed', 'baby', 'sliced', 'cubed', 'small', 'large', 'shredded', 'ground', 'finely', 'salted', 'unsalted', 'diced']
# Stop Words for Ingredient parsing
INGREDIENT_STOP_WORDS = ['ground', 'black']

# Containers for replacement/generation 
# Healthy, Vegetarian, Cuisine, etc
# Maybe a dict of lists

###Aaron 11/21
#Just jotting of ideas here for healthy transformations
#Just delete any occurence of oil, frying -> baking/air frying
#Less carbs -> more vegetables
HEALTHY_TO_UNHEALTHY = {'beef': 'turkey', 'fry': 'bake', 'bacon': 'turkey bacon', 'pasta': 'whole-grain pasta', 'sour cream': 'greek yogurt', 'rice': 'quinoa', 'lamb': 'turkey'}

#Ingredients indicative of a cuisine 
#Tempura as a frying technique
ALL_CUISINE = ['milk', 'butter', 'salt', 'black pepper', 'eggs', 'sugar', 'flour', 'all-purpose flour']
JAPANESE = ['soy sauce', 'tuna', 'ahi tuna', 'rice', 'tamago', 'daikon', 'tempura chicken', 'tempura', 'salmon', 'octopus', 'squid', 'natto', 'sesame oil', 'sesame seeds', 'sake', 'mirin', 'rice vinegar', 'miso', 'dashi', 'tonkatsu sauce', 'soba noodles', 'udon noodles', 'ramen noodles', 'panko breadcrumbs', 'corn starch', 'togarashi', 'nori', 'ginger', 'scallion', 'tofu', 'shiitake mushroom', 'shimeji mushroom', 'ume', 'shiso', 'teriyaki sauce', 'eggs', 'wasabi', 'red bean paste', 'matcha', 'mochi', 'beef']
ITALIAN = {'pasta': 'carb', 'tomato': 'vegetable', 'basil': 'herb', 'oregano': 'herb', 'garlic': 'spice', 'olive oil': 'oil', 'balsamic vinegar': 'sauce', 'caper': 'vegetable', 'veal':'meat', 'beef':'meat', 'chicken':'meat', 'pork':'meat', 'prosciutto':'meat', 'bolognese sauce':'sauce', 'pomodoro sauce':'sauce', 'pesto':'sauce', 'pancetta':'meat', 'porcini mushrooms':'vegetable', 'romano cheese':'cheese', 'mozzarella cheese':'cheese', 'parmigiano cheese':'cheese', 'parmigiano-reggiano':'cheese', 'wine':'sauce', 'polenta':'carb', 'swordfish':'fish', 'artichokes':'vegetable', 'risotto':'carb', 'ricotta cheese':'cheese', 'zucchini':'vegetbale', 'eggplants':'vegetable', 'onion':'vegetable', 'peppers':'vegetable', 'penne pasta':'pasta', 'spaghetti':'pasta', 'linguine':'pasta', 'fusili':'pasta', 'lasgane':'pasta', 'rigatoni':'pasta', 'gnocchi':'carb', 'ravioli':'pasta', 'tortellini':'pasta', 'pizza':'carb', 'fontina':'cheese', 'salami':'meat', 'panna cotta':'sweet', 'tiramisu':'sweet', 'pistachio':'nut', 'cannoli':'sweet', 'thyme':'herb', 'rosemary':'herb', 'red pepper flake':'spice', 'sage':'herb', 'lemon':'fruit', 'pine nuts':'nut', 'anchovies':'fish', 'sardines':'fish', 'bread crumbs':'carb', 'bay leaf':'herb', 'capicola':'meat', 'burrata':'cheese', 'parmesan cheese': 'cheese', 'macaroni': 'pasta', 'elbow macaroni': 'pasta'}



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
    quant, unit, rest, descriptor_list, ingredient = None, None, None, [], ''
    # Find Ingr Match in whole str, splitting messes up matching. I.E., 'soy sauce' becomes 'soy', 'sauce'
    # Finding smallest matching str, need to find largest matching str
    # I think I can check for matches that have a larger length than the previous
    # Might not need too, recipes tend to only use the term 'pork' in instructions to refer to the ingredient 'pork tenderloin' 
    # Just add an additional value to the ingrs_dict[ingredient] -> alias_list

    # Loop through all ingredients
    for pos_ingr in ALL_INGREDIENTS:
        # if any match
            if pos_ingr in ingr:
                # Catch 'and' in ingr. Has to be a better way to do this. 
                # 'salt and black pepper' --> 'salt and black'  |   'salt and ground black pepper' --> 'salt and ground' 
                if 'and' in ingr:
                    # Split into list w idxs
                    split_ingrs = ingr.split()
                    split_ingr_w_index = enumerate(split_ingrs)
                    for i,v in split_ingr_w_index:
                        if v == 'and':
                            # Get preceding and anteceding elements
                            first_ingr = split_ingrs[i - 1]
                            second_ingr = split_ingrs[i + 1]
                            # Check for bad parse of 2nd ingredient
                            if second_ingr in INGREDIENT_STOP_WORDS:
                                second_ingr = second_ingr + ' ' + split_ingrs[i + 2]
                                if split_ingrs[i + 2] in INGREDIENT_STOP_WORDS:
                                    second_ingr = second_ingr + ' ' + split_ingrs[i + 3]
                            # Concat to ingredient
                            ingredient = first_ingr + ' and ' +  second_ingr
                            break 
                else: 
                    # Set as ingredient, break
                    ingredient = max(pos_ingr, ingredient)
        
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

def parseInstructions(instructions: str, ingredients: list) -> dict:
    # I think I have to add ingredients strs, definitely have to. I'm a dunce. Can add keys from ingr_dict 
    """ Function for Parsing Instructions"""
    # Create dict to hold instruction
    instruction_dict = {}
    for i,v in enumerate(instructions):
        instruction_dict[i + 1] = parseInstruction(v, ingredients)

    # Return Dict
    return instruction_dict

def parseInstruction(instr: str, ingredients: list) -> dict:
    # Needs ingredients for recipe as input
    """ Function for parsing individual instructions"""
    # Create dict for instruction
    instr_dict = {}
    # Split instr str into tokens
    toks = instr.split()
    # Create keys for necessary data
    instr_dict['ingredients'] = []
    instr_dict['tools'] = []
    instr_dict['action'] = []
    instr_dict['time'] = []
    instr_dict['tokens'] = []
    # Split instruction into tokens, should we use Spacy to tokenize AND tag? 
    # Verbs == Actions, Tools == Nouns
    # Could also mutate an entity ruler and do entity recognition
    # String search for now
    # Loop through tokens
    for i,v in enumerate(toks):
        word = v.lower()
        word = re.sub(r'[^\w\s]', '', word)
        # Check for time
        if word in TIMES:
            # append v and instr[i - 1] -> '10 minutes'
            instr_dict['time'].append(toks[i - 1].lower() + ' ' + word)
            instr_dict['tokens'].append('time')
        # Check for Tools
        elif word in SUFFIXES:
            if toks[i - 1] in PREFIXES or toks[i - 1] in ALL_INGREDIENTS:
                # append prefix + suffix
                instr_dict['tools'].append(toks[i - 1].lower() + ' ' + word)
                instr_dict['tokens'].append('tool')
        elif word in SIMPLE_TOOLS:
            instr_dict['tools'].append(word)
            instr_dict['tokens'].append('tool')
        # Check for Actions
        elif word in ACTIONS:
            instr_dict['action'].append(word)
            instr_dict['tokens'].append('action')
            # Check if action maps to tool
            if word in ACTION_TO_TOOL.keys():
                instr_dict['tools'].append(ACTION_TO_TOOL[word])
                instr_dict['tokens'].append('tool')
        # Check for ingredients
        elif word in ingredients:
            instr_dict['ingredients'].append(word)
            instr_dict['tokens'].append('ingredient')
        # If not any 
        else:
            # Keep structure for string sub
            instr_dict['tokens'].append(v)

    # Return Dict
    return instr_dict

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

# Macey 11/21
# Humpty Dumpty the instructions back together again
# Added halving/doubling transformation in this `write_out` function
# Things to fix: "30 30 minutes" for the mac and cheese recipe (saving time inconsistently)
# Things to fix: changing units when going out of range
def write_out(ingr_dict: dict, instr_dict: dict, transformation: str, file: str):
    """`transformation` can be "none", "halved", "doubled". Will eventually be able to be substitutions. """
    lines = ["Ingredients", ""]
    ingr_transform_dict = {}
    for ingr_lst in list(ingr_dict.values()):
        ingr_phrase = ["\t-"]
        if transformation == "halved":
            ingr_phrase.append(str(ingr_lst[0] / 2))
        elif transformation == "doubled":
            ingr_phrase.append(str(ingr_lst[0] * 2))
        elif transformation == "italian":
            if ingr_lst[3].lower() not in ITALIAN and ingr_lst[3].lower() not in ALL_CUISINE:
                item = ingr_lst[3].lower()
                category = ""
                if "pasta" in item:
                    category = "pasta"
                elif "cheese" in item:
                    category = "cheese"
                elif item in CARBOHYDRATES:
                    category = "carb"
                elif item in VEGETABLES:
                    category = "vegetable"
                elif item in SPICES:
                    category = "spice"
                elif item in OILS:
                    category = "oil"
                elif item in HERBS:
                    category = "herb"
                elif item in SAUCES:
                    category = "sauce"
                elif item in MEATS:
                    category = "meat"
                elif item in FISH:
                    category = "fish"
                elif item in NUTS:
                    category = "nut"
                if category != "":
                    matched_items = []
                    for key, value in ITALIAN.items():
                        if category == value:
                            matched_items.append(key)
                    random_index = random.randrange(len(matched_items))
                    ingr_transform_dict[item] = matched_items[random_index]
                    ingr_lst[3] = matched_items[random_index]
        for ingr_part in ingr_lst[(1 if transformation in ["halved", "doubled"] else 0):]:
            if isinstance(ingr_part, list):
                if len(ingr_part) > 0:
                    ingr_phrase.append(" ".join([str(subpart) for subpart in ingr_part]))
            else:
                ingr_phrase.append(str(ingr_part))
        lines.append(" ".join(ingr_phrase))
    
    lines.extend(["", "", "Instructions", ""])
    for i in range(1, len(instr_dict) + 1):
        instr_phrase = ["\t" + str(i) + "."]
        ingredients, tools, action, time = instr_dict[i]["ingredients"], instr_dict[i]["tools"], instr_dict[i]["action"], instr_dict[i]["time"]
        i_ingr, i_tool, i_act, i_time = 0, 0, 0, 0
        for word in instr_dict[i]["tokens"]:
            if word == "ingredient":
                if ingredients[i_ingr] in ingr_transform_dict:
                    instr_phrase.append(
                        ingr_transform_dict[ingredients[i_ingr]])
                else:
                    instr_phrase.append(ingredients[i_ingr])
                i_ingr += 1
            elif word == "tool":
                instr_phrase.append(tools[i_tool])
                i_tool += 1
            elif word == "action":
                instr_phrase.append(action[i_act])
                i_act += 1
            elif word == "time":
                instr_phrase.append(time[i_time])
                i_time += 1
            else:
                instr_phrase.append(word)
        lines.append(" ".join(instr_phrase))


    with open(file, "w") as f:
        f.writelines("\n".join(lines))


def main():
    url = 'https://www.allrecipes.com/recipe/11679/homemade-mac-and-cheese/'
    #'https://www.allrecipes.com/recipe/55151/ravioli-soup/'
    #'https://www.allrecipes.com/recipe/281710/pumpkin-ravioli-with-sage-brown-butter-sauce/'
    
    #'https://www.allrecipes.com/recipe/237335/spicy-sweet-pork-tenderloin/' #sys.argv[1]
    ingredients, instructions = scrape(url)

    # Parse Ingredients Test
    ingr_dict = parseIngredients(ingredients)
    ingr_dict_keys = ingr_dict.keys() 
    instr_dict = parseInstructions(instructions, list(ingr_dict_keys))

    write_out(ingr_dict, instr_dict, "italian", "out.txt")

    cmd_output = """
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
    """

    #Test Alternative Scraper/Parser
    # scraper = scrape_me(url)
    # print(scraper.ingredients())
    # print(scraper.instructions())


if __name__ == "__main__":
    main()