import unicodedata
import re

from corpus import *

# Parsing Functions
def parseIngredients(ingrs: list) -> dict:
    """ Function to parse list of ingredients into a dict"""
    # Create Dict to hold ingrs
    ingrs_dict = {}
    # Counter for ingrs_dict
    counter = 1
    # Loop through ingrs
    for ingr in ingrs:
        # Parse individual ingr
        quant, unit, descriptor_list, ingredient, rest = parseIngredient(ingr)
        # Assign ingr as key, ingr attribute list as value
        ingrs_dict[counter] = [quant, unit, descriptor_list, ingredient, rest]
        # Incr counter
        counter += 1

    # Return ingrs dict 
    return ingrs_dict

def parseIngredient(ingr: str) -> str:
    quant, unit, rest, descriptor_list, ingredient = None, None, None, [], ''
    # Find Ingr Match in whole str, splitting messes up matching. I.E., 'soy sauce' becomes 'soy', 'sauce'
    # Finding smallest matching str, need to find largest matching str
    # I think I can check for matches that have a larger length than the previous
    # Might not need too, recipes tend to only use the term 'pork' in instructions to refer to the ingredient 'pork tenderloin' 
    # Just add an additional value to the ingrs_dict[ingredient] -> alias_list

     # Remove commas
    ingr = ingr.replace(",", "")
    # Remove dashes
    ingr = ingr.replace("-", "")
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
                            if first_ingr in ALL_INGREDIENTS and second_ingr in ALL_INGREDIENTS:
                                ingredient = first_ingr + ' and ' +  second_ingr
                                break

                            # Otherwise continue normally, probably connecting and
                            else:
                                if len(pos_ingr) > len(ingredient):
                                    ingredient = pos_ingr
                else: 
                    # Set longest ingredient match as ingredient, break
                    if len(pos_ingr) > len(ingredient):
                        ingredient = pos_ingr
    
    # Split List into Tokens
    words = ingr.split()
    # Remove matched ingredient from tokens
    ingredient_split = ingredient.split()
    for ingr_part in ingredient_split:
        if ingr_part in words:
            words.remove(ingr_part)

    # Loop through ingr tokens
    for (i, w) in enumerate(words):
        word = w.lower()
        # Check if number
        if w.isnumeric():
            n = unicodedata.numeric(w) if len(w) == 1 else float(w)
            quant = quant + n if quant else n
        # Check unit
        elif (word in UNITS) or (word[-1] == "s" and word[:-1] in UNITS) or (word[-2] == "es" and word[:-2] in UNITS):
            unit = word
        # Check for descriptors
        elif word in INGREDIENT_DESCRIPTOR:
            descriptor_list.append(word)
        # Otherwise, extra info
        else:
            if rest == None:
                rest = word
            else:
                rest = rest + " " + word
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
    # Ignore words
    ignore_words = []
    # Add two-part ingredients to ignore_words as individual words
    for ingr in ingredients:
        # If you can split into more than 1 word
        ingr_split = ingr.split()
        if len(ingr_split) > 1:
            # add individuals to ignore words list
            for word in ingr_split:
                ignore_words.append(word)
    
    # Loop through tokens
    for i,v in enumerate(toks):
        # cleanup
        word = v.lower()
        word = re.sub(r'[^\w\s]', '', word)
        combo_word = toks[i - 1] + ' ' + word
        # Check for time
        if word in TIMES:
            # append v and instr[i - 1] -> '10 minutes'
            instr_dict['time'].append(toks[i - 1].lower() + ' ' + word)
            instr_dict['tokens'].append('time')
            # remove time prefix from tokens
            instr_dict['tokens'].remove(toks[i - 1])
        # Check for Tools
        elif word in SUFFIXES:
            if toks[i - 1] in PREFIXES or toks[i - 1] in ALL_INGREDIENTS:
                # append prefix + suffix
                instr_dict['tools'].append(toks[i - 1].lower() + ' ' + word)
                instr_dict['tokens'].append('tool')
                # remove prefix from tokens
                instr_dict['tokens'].remove(toks[i - 1])
            elif word in SIMPLE_TOOLS:
                # Simple Tool
                instr_dict['tools'].append(word)
                instr_dict['tokens'].append('tool')
        elif word in SIMPLE_TOOLS:
            instr_dict['tools'].append(word)
            instr_dict['tokens'].append('tool')
        # Check for Actions
        elif word in ACTIONS:
            instr_dict['action'].append(word)
            instr_dict['tokens'].append('action')
       
        # Check for ingredients
        elif word in ingredients:
            instr_dict['ingredients'].append(word)
            instr_dict['tokens'].append('ingredient')

        # Check for combo word
        elif combo_word in ingredients:
            instr_dict['ingredients'].append(combo_word)
            instr_dict['tokens'].append('ingredient')

        # If not any 
        else:
            # Make sure not a word we should ignore
            if v not in ignore_words:
                # Non critical info append to tokens
                instr_dict['tokens'].append(v)

    # Return Dict
    return instr_dict
