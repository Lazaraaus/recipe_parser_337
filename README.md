# Assignment 2: Recipe Parser & Interactive Cookbook
#### Written by: Aaron Cooper, Macey Goldstein, & Yjaden Wood

## How to Run This Project
In order to run the project, you need to download and navigate to the project directory. From there, optionally activate a virtual environment and then install the necessary libraries by running `pip install -r requirements.txt` or `pip3 install -r requirements.txt`.

## Project Parameters
To run the project in the project directory, run the `python3 parser.py [transformation] [output] [url]` command. Below are more details about each of the parameters.
- `transformation`: Describes what transformation to perform on the input recipe. The options for this parameter are:
    - `none`: Outputs the parsed recipe with no transformations.
    - `vegetarian`: Outputs a vegetarian version of the recipe.
    - `italian`: Outputs an Italian-cuisine version of the recipe.
    - `halved`: Outputs a version of the recipe that yields half the amount.
    - `doubled`: Outputs a version of the recipe that yields twice the amount.
    - `unvegetarian`: Outputs a non-vegetarian version of the recipe
    - `unhealthy`: Outputs an unhealthier version of the recipe
    - `healthy`: Outputs a healthier version of the recipe

- `output`: Lists the path to an output file to which the human-readable recipe will be written. If you would like a look at the internal representation of the parsed recipe (before transformations) instead, you may use `cmd` as the value for this parameter and it will print that internal representation to the command line.
- `url`: The URL of the input recipe from www.allrecipes.com.