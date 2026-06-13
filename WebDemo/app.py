from flask import Flask, render_template, request
import pandas as pd
import ast

app = Flask(__name__)

rules_df = pd.read_csv('ingredient_rules.csv')
recipes_df = pd.read_csv('clean_recipes.csv')

recipes_df['ingredients'] = recipes_df['ingredients'].apply(ast.literal_eval)
recipes_df['ingredient_set'] = recipes_df['ingredients'].apply(set)

def get_recipe_suggestions(user_input, rules_df, recipes_df, top_n=5):
    input_words = [i.strip().lower() for i in user_input.split(',')]
    valid_combos = []
    
    for index, row in rules_df.iterrows():
        antecedents = set(ast.literal_eval(row['antecedents']))
        match = False
        
        for inp in input_words:
            for ant in antecedents:
                if inp in ant.lower():
                    match = True
                    break
            if match:
                break
                
        if match:
            consequents = set(ast.literal_eval(row['consequents']))
            full_combo = antecedents | consequents
            if full_combo not in valid_combos:
                valid_combos.append(full_combo)

    results = []
    for combo in valid_combos:
        if len(results) >= top_n:
            break
            
        mask = recipes_df['ingredient_set'].apply(lambda x: combo.issubset(x))
        matched_recipes = recipes_df[mask]
        
        if not matched_recipes.empty:
            recipe = matched_recipes.iloc[0]
            if not any(r['name'] == recipe['name'] for r in results):
                results.append({
                    'name': recipe['name'],
                    'combo': list(combo),
                    'full_ingredients': recipe['ingredients']
                })
                
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    user_input = ""
    if request.method == 'POST':
        user_input = request.form['ingredients']
        results = get_recipe_suggestions(user_input, rules_df, recipes_df, 5)
    return render_template('index.html', results=results, user_input=user_input)

if __name__ == '__main__':
    app.run(debug=True)