import sys
import json
from parse import *
from output import *
from scrape import *
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

# 11/23
# Changed parseIngredients to use 1-index as keys and store the ingredient as a value
# Fixed double time bug --> added case to remove time prefix from tokens
# Fixed missing tool bug --> added case to properly handle simple tools that are also suffixes
# Added func to get list of ingrs from ingrs_dict
# Fixed not handling punc properly in parseIngredient
# Fixed issue w/ outputting None in ingredients
# Fixed issue w/ outputting in wrong order
# Removed unused code: ParseTools, scraper library
# Added: Healthy Transform, Unhealthy Transform, Vegetarian Transform, Unveg Transform
# Cleaned up code
# Fixed bug w/ parsing conjuctive and
# Fixed bug w/ trailing ands in output
# Test w/ lots of recipes. Looks good


###Aaron 11/21
#Just jotting of ideas here for healthy transformations
#Just delete any occurence of oil, frying -> baking/air frying
#Less carbs -> more vegetables



# Macey 11/21
# Humpty Dumpty the instructions back together again
# Added halving/doubling transformation in this `write_out` function
# Things to fix: "30 30 minutes" for the mac and cheese recipe (saving time inconsistently)
# Things to fix: changing units when going out of range


# Helper Func to get ingrs list from ingrs dict
def get_ingredients_from_ingrs_dict(ingr_dict):
    # Create empty list
    ingrs_list = []
    # Loop through values of ingr_dict
    for ingr_dict_values in ingr_dict.values():
        # Get 2nd to last item (ingredient) from value list
        ingrs_list.append(ingr_dict_values[-2])
    return ingrs_list


# MACEY NOTE 12/7: Do we want to maybe split the instructions into smaller steps by sentences?
# Also we should pull the title of the recipe?

def main():
    transformation, out, url = sys.argv[1:4]
    if url == "test":
        url = "https://www.allrecipes.com/recipe/229088/apple-crisp-with-oat-topping/"
        #"https://www.allrecipes.com/recipe/23439/perfect-pumpkin-pie/"
        #"https://www.allrecipes.com/recipe/149586/spicy-chicken-and-sweet-potato-stew/" 

    # Scrape URL
    title, ingredients, instructions = scrape(url)
    # Parse Ingredients
    ingr_dict = parseIngredients(ingredients)
    # Get ingredients from ingr_dict
    ingrs_list = get_ingredients_from_ingrs_dict(ingr_dict)
    # Parse Instructions
    instr_dict = parseInstructions(instructions, ingrs_list)
    # Output
    if out == "cmd":
        print(title)
        print()
        print(json.dumps(ingr_dict, indent=4))
        print()
        print(json.dumps(instr_dict, indent=4))
    else:
        write_out(title, ingr_dict, instr_dict, transformation, out)


if __name__ == "__main__":
    main()