# create_pokemon_data.py
import requests
import csv
import time

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
TOTAL_POKEMON = 1025  # Podes ajustar este número se saírem mais Pokémon oficiais

# --- [NOVO] DADOS DOS POKÉMON PERSONALIZADOS ---
# Todos os teus Pokémon personalizados estão definidos aqui.
# Se quiseres adicionar mais, basta seguir o mesmo formato.
CUSTOM_POKEMON_DATA = [
    {'id': 1496, 'name': 'iron-redundancy', 'types': 'electric,psychic', 'abilities': 'quark drive',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 80, 'attack': 122, 'defense': 84, 'special-attack': 100, 'special-defense': 84, 'speed': 100,
     'special_category': 'Paradox'},
    {'id': 1497, 'name': 'iron-bastion', 'types': 'poison,ground', 'abilities': 'quark drive',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 82, 'attack': 96, 'defense': 74, 'special-attack': 130, 'special-defense': 88, 'speed': 100,
     'special_category': 'Paradox'},
    {'id': 1498, 'name': 'anticore', 'types': 'bug,dragon', 'abilities': 'adaptability,chimeric',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 95, 'attack': 105, 'defense': 85, 'special-attack': 105, 'special-defense': 85, 'speed': 95,
     'special_category': 'Mercurial'},
    {'id': 1499, 'name': 'oniki', 'types': 'dark', 'abilities': 'prankster,run-away',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 50, 'attack': 65, 'defense': 40, 'special-attack': 30, 'special-defense': 40, 'speed': 75,
     'special_category': ''},
    {'id': 1500, 'name': 'hionishi', 'types': 'dark,fighting', 'abilities': 'spirit-scavenger',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 80, 'attack': 70, 'defense': 95, 'special-attack': 135, 'special-defense': 120, 'speed': 100,
     'special_category': ''},
    {'id': 1501, 'name': 'iron-stratus', 'types': 'ghost,electric', 'abilities': 'quark-drive',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 82, 'attack': 60, 'defense': 70, 'special-attack': 116, 'special-defense': 124, 'speed': 118,
     'special_category': 'Paradox'},
    {'id': 1502, 'name': 'iron-lullaby', 'types': 'normal,steel', 'abilities': 'quark-drive',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 64, 'attack': 86, 'defense': 91, 'special-attack': 109, 'special-defense': 102, 'speed': 118,
     'special_category': 'Paradox'},
    {'id': 1503, 'name': 'iron-grinder', 'types': 'ground,fairy', 'abilities': 'quark-drive',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 72, 'attack': 146, 'defense': 134, 'special-attack': 58, 'special-defense': 96, 'speed': 64,
     'special_category': 'Paradox'},
    {'id': 1504, 'name': 'sunfauna', 'types': 'dragon,grass', 'abilities': 'thick-fat,contrary,chlorophyll',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 95, 'attack': 115, 'defense': 100, 'special-attack': 65, 'special-defense': 85, 'speed': 42,
     'special_category': ''},
    {'id': 1505, 'name': 'horridge', 'types': 'dark,steel', 'abilities': 'sharpness,levitate',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 30, 'attack': 70, 'defense': 30, 'special-attack': 70, 'special-defense': 30, 'speed': 95,
     'special_category': ''},
    {'id': 1506, 'name': 'doomblade', 'types': 'dark,steel', 'abilities': 'sharpness,levitate',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 50, 'attack': 91, 'defense': 50, 'special-attack': 91, 'special-defense': 50, 'speed': 116,
     'special_category': ''},
    {'id': 1507, 'name': 'grimslash', 'types': 'dark,steel', 'abilities': 'sharpness,levitate,fear-the-reaper',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 55, 'attack': 108, 'defense': 52, 'special-attack': 108, 'special-defense': 52, 'speed': 125,
     'special_category': ''},
    {'id': 1508, 'name': 'smogging', 'types': 'fire,rock', 'abilities': 'white-smoke,levitate,flame-body',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 50, 'attack': 45, 'defense': 60, 'special-attack': 90, 'special-defense': 40, 'speed': 55,
     'special_category': ''},
    {'id': 1509, 'name': 'smouldering', 'types': 'fire,rock', 'abilities': 'choke-smoke,levitate,drought',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 65, 'attack': 70, 'defense': 65, 'special-attack': 120, 'special-defense': 90, 'speed': 80,
     'special_category': ''},
    {'id': 1510, 'name': 'unilite', 'types': 'fairy,normal', 'abilities': 'clear-body,stamina,dazzling',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 40, 'attack': 42, 'defense': 42, 'special-attack': 62, 'special-defense': 58, 'speed': 66,
     'special_category': ''},
    {'id': 1511, 'name': 'qilinasus', 'types': 'fairy,flying', 'abilities': 'clear-body,wind-rider,gale-wings',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 72, 'attack': 105, 'defense': 81, 'special-attack': 80, 'special-defense': 90, 'speed': 115,
     'special_category': ''},
    {'id': 1512, 'name': 'ignivarg', 'types': 'fire,ice', 'abilities': 'fur-coat,prankster,quick-feet',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 47, 'attack': 64, 'defense': 45, 'special-attack': 34, 'special-defense': 65, 'speed': 55,
     'special_category': ''},
    {'id': 1513, 'name': 'skoldurn', 'types': 'fire,ice', 'abilities': 'fur-coat,snow-warning,slush-rush',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 90, 'attack': 115, 'defense': 70, 'special-attack': 93, 'special-defense': 125, 'speed': 80,
     'special_category': ''},
    {'id': 1514, 'name': 'orinari', 'types': 'psychic,normal', 'abilities': 'fluffy,storm-chaser',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 76, 'attack': 58, 'defense': 51, 'special-attack': 29, 'special-defense': 55, 'speed': 51,
     'special_category': ''},
    {'id': 1515, 'name': 'kachoron', 'types': 'psychic,normal', 'abilities': 'fluffy,storm-chaser',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 128, 'attack': 106, 'defense': 87, 'special-attack': 65, 'special-defense': 83, 'speed': 76,
     'special_category': ''},
    {'id': 1516, 'name': 'shemurai', 'types': 'ghost,steel', 'abilities': 'wonder-guard',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 1, 'attack': 107, 'defense': 48, 'special-attack': 90, 'special-defense': 48, 'speed': 75,
     'special_category': ''},
    {'id': 1517, 'name': 'skelaymore', 'types': 'ground', 'abilities': 'rock-head,sharpness,skull-splinter',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 95, 'attack': 85, 'defense': 120, 'special-attack': 60, 'special-defense': 110, 'speed': 45,
     'special_category': ''},
    {'id': 1518, 'name': 'buneerie', 'types': 'dark,ghost', 'abilities': 'infiltrator,moody,aura-break',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 65, 'attack': 66, 'defense': 44, 'special-attack': 44, 'special-defense': 56, 'speed': 85,
     'special_category': ''},
    {'id': 1519, 'name': 'loplushie', 'types': 'dark,ghost', 'abilities': 'infiltrator,moody,aura-break',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 70, 'attack': 39, 'defense': 86, 'special-attack': 91, 'special-defense': 89, 'speed': 105,
     'special_category': ''},
    {'id': 1520, 'name': 'p0rygone', 'types': 'normal,poison', 'abilities': 'regenerator,corrosion,analytic',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 95, 'attack': 90, 'defense': 110, 'special-attack': 60, 'special-defense': 100, 'speed': 70,
     'special_category': ''},
    {'id': 1521, 'name': 'rapidusk', 'types': 'fire,ghost', 'abilities': 'chilling-neigh,grim-neigh,defiant',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 66, 'attack': 95, 'defense': 61, 'special-attack': 95, 'special-defense': 63, 'speed': 120,
     'special_category': ''},
    {'id': 1522, 'name': 'valpixie', 'types': 'normal,fairy', 'abilities': 'steely-spirit,mirror-armor,levitate',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 50, 'attack': 60, 'defense': 55, 'special-attack': 50, 'special-defense': 50, 'speed': 80,
     'special_category': ''},
    {'id': 1523, 'name': 'valkaiden', 'types': 'normal,fairy', 'abilities': 'steely-spirit,mirror-armor,levitate',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 55, 'attack': 75, 'defense': 60, 'special-attack': 60, 'special-defense': 55, 'speed': 95,
     'special_category': ''},
    {'id': 1524, 'name': 'valkhalla', 'types': 'normal,fairy', 'abilities': 'steely-spirit,mirror-armor,levitate',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 60, 'attack': 130, 'defense': 60, 'special-attack': 80, 'special-defense': 55, 'speed': 120,
     'special_category': ''},
    {'id': 1525, 'name': 'ninjinsen', 'types': 'bug,flying', 'abilities': 'speed-boost,sharpness',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 61, 'attack': 105, 'defense': 50, 'special-attack': 75, 'special-defense': 55, 'speed': 160,
     'special_category': ''},
    {'id': 1526, 'name': 'crustherm', 'types': 'fire,water', 'abilities': 'water-absorb,long-reach,sheer-force',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 65, 'attack': 110, 'defense': 55, 'special-attack': 100, 'special-defense': 65, 'speed': 80,
     'special_category': ''},
    {'id': 1527, 'name': 'geshi', 'types': 'fire,dark', 'abilities': 'levitate,flash-fire',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 35, 'attack': 100, 'defense': 35, 'special-attack': 40, 'special-defense': 25, 'speed': 75,
     'special_category': ''},
    {'id': 1528, 'name': 'haenshi', 'types': 'fire,dark', 'abilities': 'levitate,tough-claws',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 55, 'attack': 115, 'defense': 55, 'special-attack': 50, 'special-defense': 40, 'speed': 90,
     'special_category': ''},
    {'id': 1529, 'name': 'blazegor', 'types': 'fire,dark', 'abilities': 'defiant,tough-claws',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 65, 'attack': 130, 'defense': 80, 'special-attack': 65, 'special-defense': 60, 'speed': 100,
     'special_category': ''},
    {'id': 1530, 'name': 'tricky-gems', 'types': 'dark,ground', 'abilities': 'protosynthesis',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 90, 'attack': 95, 'defense': 92, 'special-attack': 90, 'special-defense': 138, 'speed': 65,
     'special_category': ''},
    {'id': 1531, 'name': 'lotuzen', 'types': 'grass,fairy', 'abilities': 'flower-veil,natural-cure,misty-surge',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 80, 'attack': 25, 'defense': 73, 'special-attack': 89, 'special-defense': 81, 'speed': 112,
     'special_category': ''},
    {'id': 1532, 'name': 'charring-fangs', 'types': 'fire,dragon', 'abilities': 'protosynthesis',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 117, 'attack': 139, 'defense': 89, 'special-attack': 110, 'special-defense': 70, 'speed': 45,
     'special_category': ''},
    {'id': 1533, 'name': 'obsolisc', 'types': 'rock,ghost', 'abilities': 'sturdy,perish-body,magic-guard',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 85, 'attack': 104, 'defense': 105, 'special-attack': 79, 'special-defense': 135, 'speed': 47,
     'special_category': ''},
    {'id': 1534, 'name': 'ragank', 'types': 'dark', 'abilities': 'gluttony,pickpocket,scarf-down',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 35, 'attack': 35, 'defense': 35, 'special-attack': 55, 'special-defense': 45, 'speed': 45,
     'special_category': ''},
    {'id': 1535, 'name': 'raglutton', 'types': 'dark', 'abilities': 'gluttony,pickpocket,scarf-down',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 60, 'attack': 65, 'defense': 65, 'special-attack': 90, 'special-defense': 90, 'speed': 90,
     'special_category': ''},
    {'id': 1536, 'name': 'mortapult', 'types': 'ice,ground', 'abilities': 'snow-warning,rocky-payload',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 81, 'attack': 105, 'defense': 85, 'special-attack': 125, 'special-defense': 70, 'speed': 134,
     'special_category': ''},
    {'id': 1537, 'name': 'akulbore', 'types': 'ice,fire', 'abilities': 'ice-body,refrigerate,unsettle',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 110, 'attack': 98, 'defense': 105, 'special-attack': 30, 'special-defense': 125, 'speed': 82,
     'special_category': ''},
    {'id': 1538, 'name': 'mentamite', 'types': 'rock,psychic', 'abilities': 'power-spot,sturdy,regenerator',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 80, 'attack': 70, 'defense': 90, 'special-attack': 120, 'special-defense': 115, 'speed': 60,
     'special_category': ''},
    {'id': 1539, 'name': 'mentrattel', 'types': 'rock,psychic', 'abilities': 'power-spot,intimidate,multiscale',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 80, 'attack': 70, 'defense': 110, 'special-attack': 130, 'special-defense': 115, 'speed': 95,
     'special_category': ''},
    {'id': 1540, 'name': 'cherug', 'types': 'flying', 'abilities': 'wonder-skin,dazzling',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 70, 'attack': 25, 'defense': 55, 'special-attack': 45, 'special-defense': 55, 'speed': 70,
     'special_category': ''},
    {'id': 1541, 'name': 'shabluraphim', 'types': 'flying', 'abilities': 'wonder-skin,dazzling',
     'sprite_url': 'https://cdn.craftingstore.net/rPPmDHlLQ1/57d7680d54f4e5c75d016e6271238592/3ubzigwawvtjyw8u3zoa.gif',
     'hp': 105, 'attack': 40, 'defense': 70, 'special-attack': 65, 'special-defense': 70, 'speed': 105,
     'special_category': ''},
]
# Listas hardcoded para classificações que a API não cobre ou para garantir precisão
PARADOX_POKEMON_NAMES = {
    "great-tusk", "scream-tail", "brute-bonnet", "flutter-mane", "slither-wing", "sandy-shocks",
    "iron-treads", "iron-bundle", "iron-hands", "iron-jugulis", "iron-moth", "iron-thorns",
    "roaring-moon", "iron-valiant", "walking-wake", "iron-leaves", "gouging-fire", "raging-bolt",
    "iron-boulder", "iron-crown"
}
ULTRA_BEAST_POKEMON_NAMES = {
    "nihilego", "buzzwole", "pheromosa", "xurkitree", "celesteela", "kartana", "guzzlord",
    "poipole", "naganadel", "stakataka", "blacephalon"
}
SUB_LEGENDARY_POKEMON_NAMES = {
    "articuno", "zapdos", "moltres", "raikou", "entei", "suicune", "regirock", "regice", "registeel",
    "latias", "latios", "uxie", "mesprit", "azelf", "heatran", "regigigas", "cresselia",
    "cobalion", "terrakion", "virizion", "tornadus", "thundurus", "landorus", "type-null", "silvally",
    "tapu-koko", "tapu-lele", "tapu-bulu", "tapu-fini", "kubfu", "urshifu",
    "regieleki", "regidrago", "glastrier", "spectrier", "enamorus",
    "wo-chien", "chien-pao", "ting-lu", "chi-yu", "okidogi", "munkidori", "fezandipiti",
    "ogerpon"
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
    """Creates a CSV with base, Mega, and special category information, then adds custom Pokémon."""
    fieldnames = [
        'id', 'name', 'types', 'abilities', 'sprite_url',
        'hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed',
        'special_category',
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

        # --- PARTE 1: BUSCAR POKÉMON OFICIAIS DA API ---
        print("--- Fetching Official Pokémon Data from PokéAPI ---")
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
                'has_mega': 'FALSE', 'has_mega_2': 'FALSE'
            })

            # Determinar a Categoria Especial com uma hierarquia
            category = ''  # Default é vazio
            species_details = get_api_data(base_details['species']['url'])
            if species_details:
                if species_details.get('is_legendary', False):
                    category = 'Legendary'
                if species_details.get('is_mythical', False):
                    category = 'Mythical'
                if base_data['name'] in PARADOX_POKEMON_NAMES:
                    category = 'Paradox'
                if base_data['name'] in SUB_LEGENDARY_POKEMON_NAMES:
                    category = 'Sub-Legendary'
                if base_data['name'] in ULTRA_BEAST_POKEMON_NAMES:
                    category = 'Ultra Beast'

            pokemon_row['special_category'] = category

            # Lógica para as formas Mega
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

            writer.writerow(pokemon_row)
            print(f"Successfully processed Official Pokémon #{i}: {base_data['name'].title()}")
            time.sleep(0.05)  # Pequena pausa para não sobrecarregar a API

        # --- PARTE 2: ADICIONAR POKÉMON PERSONALIZADOS ---
        print("\n--- Appending Custom Pokémon Data ---")
        for custom_poke in CUSTOM_POKEMON_DATA:
            # Preenche uma linha completa com valores padrão para garantir que todas as colunas existem
            full_row = {field: '' for field in fieldnames}
            full_row['has_mega'] = 'FALSE'
            full_row['has_mega_2'] = 'FALSE'

            # Atualiza a linha com os dados do Pokémon personalizado
            full_row.update(custom_poke)

            writer.writerow(full_row)
            print(f"Successfully added Custom Pokémon #{full_row['id']}: {full_row['name'].title()}")

    total_pokemon_count = TOTAL_POKEMON + len(CUSTOM_POKEMON_DATA)
    print(f"\nFinished! pokemon_data.csv has been created with {total_pokemon_count} Pokémon.")


if __name__ == "__main__":
    create_enhanced_dataset()