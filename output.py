from corpus import *
import random
# Fraction Conv Function
def float_to_frac(n: float):
    num = int(n // 1)
    dec = round(n % 1, 3)
    if dec == 0.000:
        dec = ""
    elif dec == 0.062:
        dec = "1/16"
    elif dec == 0.125:
        dec = "\u215b"
    elif dec == 0.188:
        dec = "3/16"
    elif dec == 0.2500:
        dec = "\u00bc"
    elif dec == 0.312:
        dec = "5/16"
    elif dec == 0.333:
        dec = "\u2153"
    elif dec == 0.375:
        dec = "\u215c"
    elif dec == 0.438:
        dec = "7/16"
    elif dec == 0.500:
        dec = "\u00bd"
    elif dec == 0.562:
        dec = "9/16"
    elif dec == 0.625:
        dec = "\u215d"
    elif dec == 0.667:
        dec = "\u2154"
    elif dec == 0.688:
        dec = "11/16"
    elif dec == 0.750:
        dec = "\u00be"
    elif dec == 0.812:
        dec = "13/16"
    elif dec == 0.875:
        dec = "\u215e"
    elif dec == 0.938:
        dec = "15/16"
    return dec if num == 0 else str(num) + dec if isinstance(dec, str) else str(num + dec)

# Conversion Dict
CONVERSIONS = {
    "teaspoon": {
        "min": [],
        "max": [2.9999, "tablespoon", 0.3333]
    },
    "tablespoon": {
        "min": [0.3334, "teaspoon", 3],
        "max": [3.9999, "cup", 0.0625]
    },
    "cup": {
        "min": [0.2409, "tablespoon", 16],
        "max": [3.9999, "quart", 0.25]
    },
    "pint": {
        "min": [0.9999, "cup", 2],
        "max": [1.0001, "quart", 0.5]
    },
    "quart": {
        "min": [0.9999, "cup", 4],
        "max": [1.0001, "gallon", 0.25]
    },
    "gallon": {
        "min": [0.2501, "quart", 4],
        "max": []
    },
    "ounce": {
        "min": [],
        "max": [15.9999, "pound", 0.0625]
    },
    "pound": {
        "min": [0.9999, "ounce", 16],
        "max": []
    }
}

# Output and Transform
def write_out(title: str, ingr_dict: dict, instr_dict: dict, transformation: str, file: str):
    old_to_new = {}
    lines = [title, "", "", "Ingredients", ""]
    ingr_transform_dict = {}
    for ingr_lst in list(ingr_dict.values()):
        ingr_phrase = ["\t-"]
        quant, unit = ingr_lst[:2]
        if quant and (transformation == "halved" or transformation == "doubled"):
            if transformation == "halved":
                quant /= 2
            elif transformation == "doubled":
                quant *= 2
            if unit and ((unit in CONVERSIONS) or (unit[-1] == "s" and unit[:-1] in CONVERSIONS) or (unit[-2] == "es" and unit[:-2] in CONVERSIONS)):
                if unit[-2] == "es":
                    unit = unit[:-2]
                elif unit[-1] == "s":
                    unit = unit[:-1]
                min_conv = CONVERSIONS[unit]["min"]
                max_conv = CONVERSIONS[unit]["max"]
                if min_conv and quant < min_conv[0]:
                    unit = min_conv[1]
                    quant *= min_conv[2]
                elif max_conv and quant > max_conv[0]:
                    unit = max_conv[1]
                    quant *= max_conv[2]
        if quant:
            ingr_phrase.append(float_to_frac(quant))
        if unit:
            ingr_phrase.append(unit)
        for ingr_part in ingr_lst[2:]:
            ingr_phrase_add = None
            if isinstance(ingr_part, list):
                if len(ingr_part) > 0:
                    ingr_phrase_add = " ".join([str(subpart) for subpart in ingr_part])
            else:
                if ingr_part != None:
                    ingr_phrase_add = str(ingr_part)
            if transformation == "italian":
                if ingr_phrase_add and ingr_phrase_add.lower() not in ITALIAN and ingr_phrase_add.lower() not in ALL_CUISINE:
                    item = ingr_phrase_add.lower()
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
                        ingr_phrase_add = matched_items[random_index]
            
            # Vegetarian transform
            if transformation == "vegetarian":
                # Check if current ingr has any Meats
                if ingr_phrase_add in MEATS:
                    # Check if ground beef, ground turkey, etc
                    if 'ground' in ingr_phrase_add:
                        # If so, use tempeh
                        old_to_new[ingr_phrase_add] = VEGETARIAN['meat_subs'][2]
                        ingr_phrase_add = old_to_new[ingr_phrase_add]
                    else:
                        # Otherwise can use any meat sub
                        random_index = random.randrange(len(VEGETARIAN['meat_subs']))
                        # Set old ingr as key to new ingr
                        old_to_new[ingr_phrase_add] = VEGETARIAN["meat_subs"][random_index]
                        # Set old ingr to new ingr
                        ingr_phrase_add = old_to_new[ingr_phrase_add]

                # Check if in Sauces
                if ingr_phrase_add in SAUCES:
                    # Check if in meat sauces
                    if ingr_phrase_add in VEGETARIAN['meat_sauces']:
                        # If so, use any non meat sauce
                        random_index = random.randrange(len(VEGETARIAN['meat_sauce_subs']))
                        # Set old ingr as key to new ingr
                        old_to_new[ingr_phrase_add] = VEGETARIAN["meat_sauce_subs"][random_index]
                        # Set old ingr to new ingr
                        ingr_phrase_add = old_to_new[ingr_phrase_add]

                    # Check if meat broth
                    elif ingr_phrase_add == "beef broth" or ingr_phrase_add == "chicken broth":
                        # Set old ingr as key to new ingr
                        old_to_new[ingr_phrase_add] = VEGETARIAN["meat_broth_subs"][0]
                        # Set old ingr to new ingr
                        ingr_phrase_add = old_to_new[ingr_phrase_add]

                # Check if meat based fat
                if ingr_phrase_add == 'lard':
                    # If so, sub vegetable shortening
                    # Set old ingr as key to new ingr
                    old_to_new[ingr_phrase_add] = VEGETARIAN['meat_fat_subs'][0]
                    # Set old ingr to new ingr
                    ingr_phrase_add = old_to_new[ingr_phrase_add]

            # Un vegetarian transform
            if transformation == "unvegetarian":
                # Check if in meat_subs
                if ingr_phrase_add in VEGETARIAN['meat_subs']:
                    # Sub w/ a meat
                    if ingr_phrase_add == 'tempeh':
                        # If tempeh, sub w/ ground beef, ground turkey, etc
                        old_to_new[ingr_phrase_add] = 'ground beef'
                        # set old ingr to new ingr
                        ingr_phrase_add = 'ground beef'
                    else:
                        # Otherwise sub w/ chicke, veal, lamb, etc
                        old_to_new[ingr_phrase_add] = 'chicken'
                        # set old ingr to new ingr
                        ingr_phrase_add = 'chicken'

                # Check if in meat_sauce_subs 
                if ingr_phrase_add in VEGETARIAN['meat_sauce_subs']:
                    # Sub w/ any meat sauce
                    random_index = random.randrange(len(VEGETARIAN['meat_sauces']))
                    # Set old ingr as key to new ingr
                    old_to_new[ingr_phrase_add] = VEGETARIAN["meat_sauces"][random_index]
                    # Set old ingr to new ingr
                    ingr_phrase_add = old_to_new[ingr_phrase_add]

            # Healthy Transformation
            if transformation == "healthy":
                if ingr_phrase_add in UNHEALTHY_TO_HEALTHY.keys():
                    # Sub w/ healthy alternative
                    old_to_new[ingr_phrase_add] = UNHEALTHY_TO_HEALTHY[ingr_phrase_add]
                    ingr_phrase_add = old_to_new[ingr_phrase_add]

            # Unhealthy Transformation
            if transformation == "unhealthy":
                if ingr_phrase_add in HEALTHY_TO_UNHEALTHY.keys():
                    # Sub w/ unhealthy alternative
                    old_to_new[ingr_phrase_add] = HEALTHY_TO_UNHEALTHY[ingr_phrase_add]
                    ingr_phrase_add = old_to_new[ingr_phrase_add]

            # Catch trailing ands 
            if ingr_phrase_add == 'and' and ingr_phrase_add == ingr_lst[-1]:
                continue
            ingr_phrase.append(ingr_phrase_add)
        lines.append(" ".join([p for p in ingr_phrase if p is not None]))
    
    lines.extend(["", "", "Instructions", ""])
    for i in range(1, len(instr_dict) + 1):
        instr_phrase = ["\t" + str(i) + "."]
        ingredients, tools, action, time = instr_dict[i]["ingredients"], instr_dict[i]["tools"], instr_dict[i]["action"], instr_dict[i]["time"]
        i_ingr, i_tool, i_act, i_time = 0, 0, 0, 0
        for word in instr_dict[i]["tokens"]:
            if word == "ingredient":
                # Check if word in old_to_new
                if ingredients[i_ingr] in old_to_new.keys():
                    # If so, append transformed ingredient
                    instr_phrase.append(old_to_new[ingredients[i_ingr]])
                    i_ingr += 1
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
