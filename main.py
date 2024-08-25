from flask import Flask, render_template, request, jsonify, redirect, url_for
import random
import requests, os
from replit import db

app = Flask(__name__)
app.secret_key = os.environ['secret_key']

def get_random_pokemon():
    pokemon_id = random.randint(1, 898)
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
    if response.status_code == 200:
        data = response.json()
        species_response = requests.get(data['species']['url'])
        species_data = species_response.json()
        description = next((entry['flavor_text'] for entry in species_data['flavor_text_entries'] if entry['language']['name'] == 'en'), "No description available.")
        types = ", ".join([t['type']['name'] for t in data['types']])
        return {
            "id": pokemon_id,
            "name": data["name"].upper(),
            "image": data["sprites"]["front_default"],
            "description": description.replace('\n', ' ').replace('\f', ' '),
            "types": types
        }
    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/encounter")
def encounter():
    pokemon = get_random_pokemon()
    if pokemon:
        db["current_pokemon"] = pokemon
        return jsonify(pokemon)
    return jsonify({"error": "Failed to fetch Pokémon"}), 500

@app.route("/catch", methods=["POST"])
def catch():
    chance = random.randint(1, 100)
    if chance <= 33:
        if "current_pokemon" in db:
            caught_pokemon = db["current_pokemon"]
            if "caught_pokemon" not in db:
                db["caught_pokemon"] = []
            db["caught_pokemon"].append(caught_pokemon)
        return jsonify({"success": True, "message": "You caught the Pokémon!"})
    return jsonify({"success": False, "message": "The Pokémon escaped!"})

@app.route("/pokedex")
def pokedex():
    pokedex_data = []
    if "caught_pokemon" in db:
        unique_pokemon = {pokemon['name']: pokemon for pokemon in db["caught_pokemon"]}.values()
        pokedex_data = list(unique_pokemon)

    return render_template("pokedex.html", pokedex=pokedex_data)


@app.route("/owned_pokemon")
def owned_pokemon():
    if "caught_pokemon" in db:
        return render_template("owned_pokemon.html", owned_pokemon=db["caught_pokemon"])
    return render_template("owned_pokemon.html", owned_pokemon=[])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
