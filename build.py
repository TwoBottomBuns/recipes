#!/usr/bin/python3
from pathlib import Path
import subprocess
import argparse
import shutil
import shlex

# TODO: Add the chicken in pan sauce

RECIPE_DIR = Path('./recipes/').resolve()

HEADER = r"""% THIS IS AUTOMATICALLY GENERATED CONTENT! MAKING MODIFICATIONS COULD MESS SOMETHING UP!

\documentclass{article}
\title{Braedon's Fantastic Recipes to Get Your Dinner and Leftovers}
\author{Compliments to the chef: Ya Boi}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{enumitem}
\usepackage{hyperref}

\hypersetup{
    colorlinks,
    citecolor=black,
    filecolor=black,
    linkcolor=black,
    urlcolor=black
}

\setlength{\parindent}{0pt}
\setcounter{secnumdepth}{0}
\setcounter{tocdepth}{1}
\setlist[itemize]{label={--}, noitemsep, topsep=0pt}

\newcommand{\recipe}[1]{\newpage\include{recipes/#1}}

\begin{document}
\maketitle

\tableofcontents

"""

FOOTER = r"""
\end{document}
"""

def _find_recipes():
    recipes = []
    return [recipe for recipe in RECIPE_DIR.iterdir() if recipe.suffix == '.tex']

def _build_import_statements(recipes):
    output = ""
    for recipe in sorted(recipes):
        output += f'\\recipe{{{recipe.stem}}}\n'
    return output

def build():
    options = argparse.ArgumentParser()
    options.add_argument('-c', '--clean', help="Clean up the build directory", action='store_true', default=False)
    args = options.parse_args()

    base_path = Path('.').resolve()
    build_dir = base_path / 'output'
    recipes_out = build_dir / 'recipes'
    if not build_dir.exists():
        build_dir.mkdir()
    if not recipes_out.exists():
        recipes_out.mkdir()
    outfile = build_dir / 'recipes.tex'

    if args.clean:
        shutil.rmtree(build_dir)
        exit()

    recipes = _find_recipes()
    recipe_contents = _build_import_statements(recipes)
    contents = HEADER + recipe_contents + FOOTER

    with open(outfile, "w") as writer:
        writer.write(contents)

    args = shlex.split(f'lualatex -recorder -output-directory="{build_dir}" "{outfile}"')
    try:
        result = subprocess.run(args, check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print(result.stderr.decode())

    # It's possible that the first build couldn't really make the table of contents because the references were not yet
    # generated. In that case, we'll have to run the command a second time.
    if b'There were undefined references' in result.stdout:
        subprocess.run(args)

if __name__ == '__main__':
    build()
