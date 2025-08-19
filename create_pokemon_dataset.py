# create_pokemon_data.py
import requests
import csv
import time

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
TOTAL_POKEMON = 1025

# A hardcoded list is the most reliable way to identify Paradox Pokémon
PARADOX_POKEMON_NAMES = {
    "great-tusk", "scream-tail", "brute-bonnet", "flutter-mane", "slither-wing", "sandy-shocks",
    "iron-treads", "iron-bundle", "iron-hands", "iron-jugulis", "iron-moth", "iron-thorns",
    "roaring-moon", "iron-valiant", "walking-wake", "iron-leaves", "gouging-fire", "raging-bolt",
    "iron-boulder", "iron-crown"
}


def get_api_data(url):
    """Fetches data from any given PokeAPI URL with error handling."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None


def parse_pokemon_details(details):
    """Parses the essential details from a Pokémon's API response."""
    if not details: return {}
    types = ','.join([t['type']['name'] for t in details['types']])
    abilities = ','.join([a['ability']['name'] for a in details['abilities']])
    stats = {s['stat']['name']: s['base_stat'] for s in details['stats']}
    sprite_url = details['sprites']['other']['official-artwork']['front_default'] or ''
    return {
        'name': details['name'], 'types': types, 'abilities': abilities, 'sprite_url': sprite_url,
        'hp': stats.get('hp', 0), 'attack': stats.get('attack', 0), 'defense': stats.get('defense', 0),
        'special-attack': stats.get('special-attack', 0), 'special-defense': stats.get('special-defense', 0),
        'speed': stats.get('speed', 0)
    }


def create_enhanced_dataset():
    """Creates a CSV with base, Mega, and Paradox information."""
    fieldnames = [
        'id', 'name', 'types', 'abilities', 'sprite_url',
        'hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed',
        'is_paradox',
        'has_mega', 'mega_name', 'mega_sprite_url', 'mega_types', 'mega_abilities',
        'mega_hp', 'mega_attack', 'mega_defense', 'mega_special-attack',
        'mega_special-defense', 'mega_speed',
        'has_mega_2', 'mega_2_name', 'mega_2_sprite_url', 'mega_2_types', 'mega_2_abilities',
        'mega_2_hp', 'mega_2_attack', 'mega_2_defense', 'mega_2_special-attack',
        'mega_2_special-defense', 'mega_2_speed'
    ]

    with open('pokemon_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, TOTAL_POKEMON + 1):
            base_details = get_api_data(f"{POKEAPI_BASE_URL}/pokemon/{i}")
            if not base_details:
                print(f"Failed to process Pokémon #{i}. Skipping.")
                continue
            base_data = parse_pokemon_details(base_details)

            pokemon_row = {field: '' for field in fieldnames}
            pokemon_row.update({
                'id': base_details['id'], 'name': base_data['name'], 'types': base_data['types'],
                'abilities': base_data['abilities'], 'sprite_url': base_data['sprite_url'],
                'hp': base_data['hp'], 'attack': base_data['attack'], 'defense': base_data['defense'],
                'special-attack': base_data['special-attack'], 'special-defense': base_data['special-defense'],
                'speed': base_data['speed'],
                'is_paradox': 'TRUE' if base_data['name'] in PARADOX_POKEMON_NAMES else 'FALSE',
                'has_mega': 'FALSE', 'has_mega_2': 'FALSE'
            })

            species_details = get_api_data(f"{POKEAPI_BASE_URL}/pokemon-species/{i}")
            if species_details:
                mega_forms = [v for v in species_details.get('varieties', []) if
                              "mega" in v['pokemon']['name'] and not v['is_default']]

                if len(mega_forms) >= 1:
                    mega_1_details = get_api_data(mega_forms[0]['pokemon']['url'])
                    if mega_1_details:
                        mega_1_data = parse_pokemon_details(mega_1_details)
                        pokemon_row.update({
                            'has_mega': 'TRUE', 'mega_name': mega_1_data['name'],
                            'mega_sprite_url': mega_1_data['sprite_url'],
                            'mega_types': mega_1_data['types'], 'mega_abilities': mega_1_data['abilities'],
                            'mega_hp': mega_1_data['hp'], 'mega_attack': mega_1_data['attack'],
                            'mega_defense': mega_1_data['defense'],
                            'mega_special-attack': mega_1_data['special-attack'],
                            'mega_special-defense': mega_1_data['special-defense'],
                            'mega_speed': mega_1_data['speed']
                        })
                        print(f"---> Found Mega form 1 for {base_data['name'].title()}: {mega_1_data['name']}")

                if len(mega_forms) >= 2:
                    mega_2_details = get_api_data(mega_forms[1]['pokemon']['url'])
                    if mega_2_details:
                        mega_2_data = parse_pokemon_details(mega_2_details)
                        pokemon_row.update({
                            'has_mega_2': 'TRUE', 'mega_2_name': mega_2_data['name'],
                            'mega_2_sprite_url': mega_2_data['sprite_url'],
                            'mega_2_types': mega_2_data['types'], 'mega_2_abilities': mega_2_data['abilities'],
                            'mega_2_hp': mega_2_data['hp'], 'mega_2_attack': mega_2_data['attack'],
                            'mega_2_defense': mega_2_data['defense'],
                            'mega_2_special-attack': mega_2_data['special-attack'],
                            'mega_2_special-defense': mega_2_data['special-defense'],
                            'mega_2_speed': mega_2_data['speed']
                        })
                        print(f"---> Found Mega form 2 for {base_data['name'].title()}: {mega_2_data['name']}")

            writer.writerow(pokemon_row)
            print(f"Successfully processed Pokémon #{i}: {base_data['name'].title()}")
            time.sleep(0.1)

    print(f"\nFinished! pokemon_data.csv has been created with {TOTAL_POKEMON} Pokémon and their Mega/Paradox data.")


if __name__ == "__main__":
    create_enhanced_dataset()