# -*- coding: utf-8 -*-
import time
import os
import discord
import asyncio
import csv
import re
import requests
from discord.ext import tasks, commands
from datetime import datetime, timezone

# =================================================================================
# --- USER PROFILES & DYNAMIC CONFIGURATION ---
# =================================================================================

USER_PROFILES = {
    "LazySan": {
        "discord_id": 379261623803707405,
        "log_path_type": "APPDATA",
        "log_path_value": os.path.join("ModrinthApp", "profiles", "Cobblemon Dystoria 3.0.4", "logs", "latest.log")
    },
    "TheNepia": {
        "discord_id": 285901101029392385,
        "log_path_type": "ABSOLUTE",
        "log_path_value": r"C:\Users\andre\curseforge\minecraft\Instances\Cobblemon Dystoria\logs\latest.log"
    },
    "Kimachi00": {
        "discord_id": 593562868323057676,
        "log_path_type": "APPDATA",
        "log_path_value": os.path.join("ModrinthApp", "profiles", "Cobblemon Dystoria LazySan 1.0.0", "logs",
                                       "latest.log")
    },
    "guidobaldo": {
        "discord_id": 326301121809481728,
        "log_path_type": "APPDATA",
        "log_path_value": os.path.join("ModrinthApp", "profiles", "Cobblemon Dystoria", "logs", "latest.log")
    }
}


def verify_log_file_path():
    if not os.path.exists(Config.MINECRAFT.LOG_FILE_PATH):
        print("\n" + "=" * 60);
        print("!!! CRITICAL ERROR: Log file not found !!!");
        print(f"    Path checked: {Config.MINECRAFT.LOG_FILE_PATH}");
        print("\nPossible Causes:");
        print("  1. The profile name or path in USER_PROFILES is incorrect.");
        print("  2. Minecraft (with this profile) has never been run, so 'latest.log' does not exist yet.");
        print("\nPlease verify the path and run the game at least once.");
        print("Bot cannot continue. Exiting...");
        print("=" * 60)
        return False
    return True


def select_user_and_configure():
    print("=" * 46);
    print("=== Cobblemon Dystoria Bot - Profile Selection ===");
    print("=" * 46)
    players = list(USER_PROFILES.keys())
    for i, player in enumerate(players): print(f"  [{i + 1}] OTÁRIO DO IURI {player}")
    print("  [0] Exit")
    while True:
        try:
            choice = int(input("\nWho is running the bot? Please select a number: "))
            if 0 <= choice <= len(players):
                break
            else:
                print(f"Invalid choice. Please enter a number between 0 and {len(players)}.")
        except ValueError:
            print("Invalid input. Please enter a number only.")
    if choice == 0:
        print("Exiting bot. Goodbye!");
        return False
    selected_player_name = players[choice - 1]
    selected_profile = USER_PROFILES[selected_player_name]
    Config.DISCORD.ADMIN_ID = selected_profile["discord_id"]
    if selected_profile["log_path_type"] == "APPDATA":
        Config.MINECRAFT.LOG_FILE_PATH = os.path.join(os.getenv("APPDATA"), selected_profile["log_path_value"])
    elif selected_profile["log_path_type"] == "ABSOLUTE":
        Config.MINECRAFT.LOG_FILE_PATH = selected_profile["log_path_value"]
    else:
        print(
            f"CRITICAL ERROR: Invalid 'log_path_type' for user {selected_player_name}. Must be 'APPDATA' or 'ABSOLUTE'.");
        return False
    print("\n--- Configuration Applied ---");
    print(f"Active User: {selected_player_name}");
    print(f"Admin ID Set To: {Config.DISCORD.ADMIN_ID}");
    print(f"Log Path Set To: {Config.MINECRAFT.LOG_FILE_PATH}");
    print("---------------------------\n")
    if not verify_log_file_path(): return False
    print("Log path verified successfully. Starting the bot...")
    return True


# =================================================================================
# --- CENTRALIZED CONFIGURATION ---
# =================================================================================
class Config:
    class DISCORD:
        try:
            from config_local import DISCORD_TOKEN
            TOKEN = DISCORD_TOKEN
        except ImportError:
            TOKEN = None
        CHANNEL_ID = 1403568094063890533;
        ADMIN_ID = None;
        COMMAND_PREFIX = '!'
        PLAYER_DISCORD_MAP = {name.lower(): profile["discord_id"] for name, profile in USER_PROFILES.items()}

    class MINECRAFT:
        LOG_FILE_PATH = None;
        LOG_CHAT_PREFIX = "[Render thread/INFO]: [CHAT] ";
        IDLE_TIME_UNTIL_WARNING_SEC = 120

    class FILTERS:
        PLAYER_NAMES = list(USER_PROFILES.keys())

    class BEHAVIOR:
        CLEAR_CHANNEL_ON_STARTUP = True;
        DEBUG_MSG_LIFETIME_SEC = 20;
        WONDER_TRADE_COOLDOWN_SEC = 600
        RAID_TIER_TIMERS_SEC = {"Mega": 180, "Paradox": 180, "S": 120, "A": 120, "B": 120, "C": 120, "D": 120,
                                "default": 120}
        RAID_TIMER_FIGHT_SEC = 300;
        AFK_KICK_TIME_SEC = 1800;
        AFK_WARNING_BEFORE_KICK_SEC = 300

    class COLORS:
        DEFAULT = discord.Color.blue();
        SUCCESS = discord.Color.green();
        ERROR = discord.Color.red()
        RAID = discord.Color.dark_red();
        BOSS = discord.Color.purple();
        SHINY = discord.Color.gold()
        LEGENDARY = discord.Color.from_rgb(255, 85, 255);
        INFO = discord.Color.orange()

    class NTFY:
        ENABLED = True;
        TOPIC = "lazysan-dystoria-cobblemon";
        SERVER = "https://ntfy.sh"


# =================================================================================
# --- GLOBAL BOT STATE & SETUP ---
# =================================================================================
pokemon_db = {};
subscribed_users = set();
log_inactivity_warning_sent = False;
RAID_LOG_FILE = "raid_log.csv";
afk_timers = {}
intents = discord.Intents.default();
intents.message_content = True
bot = commands.Bot(command_prefix=Config.DISCORD.COMMAND_PREFIX, intents=intents, help_command=None)
target_channel = None

# =================================================================================
# --- DATA AND HELPER LOGIC ---
# =================================================================================
TYPE_CHART = {
    'normal': {'weak': ['fighting'], 'resist': [], 'immune': ['ghost']},
    'fire': {'weak': ['water', 'ground', 'rock'], 'resist': ['fire', 'grass', 'ice', 'bug', 'steel', 'fairy'],
             'immune': []},
    'water': {'weak': ['electric', 'grass'], 'resist': ['fire', 'water', 'ice', 'steel'], 'immune': []},
    'electric': {'weak': ['ground'], 'resist': ['electric', 'flying', 'steel'], 'immune': []},
    'grass': {'weak': ['fire', 'ice', 'poison', 'flying', 'bug'], 'resist': ['water', 'electric', 'grass', 'ground'],
              'immune': []}, 'ice': {'weak': ['fire', 'fighting', 'rock', 'steel'], 'resist': ['ice'], 'immune': []},
    'fighting': {'weak': ['flying', 'psychic', 'fairy'], 'resist': ['bug', 'rock', 'dark'], 'immune': []},
    'poison': {'weak': ['ground', 'psychic'], 'resist': ['grass', 'fighting', 'poison', 'bug', 'fairy'], 'immune': []},
    'ground': {'weak': ['water', 'grass', 'ice'], 'resist': ['poison', 'rock'], 'immune': ['electric']},
    'flying': {'weak': ['electric', 'ice', 'rock'], 'resist': ['grass', 'fighting', 'bug'], 'immune': ['ground']},
    'psychic': {'weak': ['bug', 'ghost', 'dark'], 'resist': ['fighting', 'psychic'], 'immune': []},
    'bug': {'weak': ['fire', 'flying', 'rock'], 'resist': ['grass', 'fighting', 'ground'], 'immune': []},
    'rock': {'weak': ['water', 'grass', 'fighting', 'ground', 'steel'],
             'resist': ['normal', 'fire', 'poison', 'flying'], 'immune': []},
    'ghost': {'weak': ['ghost', 'dark'], 'resist': ['poison', 'bug'], 'immune': ['normal', 'fighting']},
    'dragon': {'weak': ['ice', 'dragon', 'fairy'], 'resist': ['fire', 'water', 'electric', 'grass'], 'immune': []},
    'dark': {'weak': ['fighting', 'bug', 'fairy'], 'resist': ['ghost', 'dark'], 'immune': ['psychic']},
    'steel': {'weak': ['fire', 'fighting', 'ground'],
              'resist': ['normal', 'grass', 'ice', 'flying', 'psychic', 'bug', 'rock', 'dragon', 'steel', 'fairy'],
              'immune': ['poison']},
    'fairy': {'weak': ['poison', 'steel'], 'resist': ['fighting', 'bug', 'dark'], 'immune': ['dragon']}
}
TYPE_EMOJIS = {
    'normal': '⚪', 'fire': '🔥', 'water': '💧', 'electric': '⚡', 'grass': '🌿', 'ice': '❄️', 'fighting': '🥊',
    'poison': '☠️', 'ground': '🌍', 'flying': '🐦', 'psychic': '🔮', 'bug': '🐛', 'rock': '🗿', 'ghost': '👻', 'dragon': '🐲',
    'dark': '🌙', 'steel': '⚙️', 'fairy': '💖'
}


def load_pokemon_data():
    global pokemon_db
    try:
        with open('pokemon_data.csv', mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            pokemon_db = {row['name'].lower(): row for row in reader}
        print(f"Pokémon database loaded with {len(pokemon_db)} entries.")
    except FileNotFoundError:
        print("WARNING: 'pokemon_data.csv' not found. Advanced features will be disabled.")
        pokemon_db = {}


def normalize_pokemon_name(name: str) -> str:
    return name.strip().lower().replace(' ', '-')


def calculate_effectiveness(pokemon_types: list[str]) -> dict:
    from collections import defaultdict
    effectiveness = defaultdict(lambda: 1.0)
    all_types = TYPE_CHART.keys()
    for p_type in pokemon_types:
        if p_type not in TYPE_CHART: continue
        for attack_type in all_types:
            if attack_type in TYPE_CHART[p_type]['weak']:
                effectiveness[attack_type] *= 2
            elif attack_type in TYPE_CHART[p_type]['resist']:
                effectiveness[attack_type] *= 0.5
            elif attack_type in TYPE_CHART[p_type]['immune']:
                effectiveness[attack_type] *= 0
    weaknesses, resistances, immunities = {'x4': [], 'x2': []}, [], []
    for attack_type, multiplier in effectiveness.items():
        if multiplier >= 4:
            weaknesses['x4'].append(attack_type.title())
        elif multiplier >= 2:
            weaknesses['x2'].append(attack_type.title())
        elif multiplier == 0:
            immunities.append(attack_type.title())
        elif multiplier < 1:
            resistances.append(attack_type.title())
    return {"weaknesses": weaknesses, "resistances": resistances, "immunities": immunities}


def answer_trivia(question_text: str) -> str | None:
    if not pokemon_db: return None
    question_text_lower = question_text.lower()
    if "unscramble this pokemon's name:" in question_text_lower:
        scrambled_part = question_text_lower.split("unscramble this pokemon's name:")[1].strip()
        scrambled_sorted = sorted(scrambled_part)
        for name in pokemon_db:
            if sorted(name) == scrambled_sorted: return f"Answer: **{name.title()}**"
    type_match = re.search(r"what type is (.+?)\?", question_text_lower)
    if type_match:
        pokemon_name = type_match.group(1).strip()
        normalized_name = normalize_pokemon_name(pokemon_name)
        if pokemon_info := pokemon_db.get(normalized_name):
            if types := pokemon_info.get("types"):
                parts = [f"**{part.strip().title()}**" for part in types.split(',')]
                return f"Answer: {' or '.join(parts)}"
    ability_match = re.search(r"what ability does (.+?) have\?", question_text_lower)
    if ability_match:
        pokemon_name = ability_match.group(1).strip()
        normalized_name = normalize_pokemon_name(pokemon_name)
        if pokemon_info := pokemon_db.get(normalized_name):
            if abilities := pokemon_info.get("abilities"):
                parts = [f"**{part.strip().title()}**" for part in abilities.split(',')]
                return f"Answer: {' or '.join(parts)}"
    return None


def determine_raid_tier(pokemon_data: dict, is_mega: bool) -> str:
    if not pokemon_data: return "Unknown"
    if is_mega: return "Mega"
    if pokemon_data.get('is_paradox') == 'TRUE': return "Paradox"
    stats_to_sum = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
    try:
        bst = sum(int(pokemon_data.get(stat, 0)) for stat in stats_to_sum)
    except (ValueError, TypeError):
        bst = 0
    if bst >= 500: return "S"
    if 450 <= bst <= 499: return "A"
    if 380 <= bst <= 449: return "B"
    if 300 <= bst <= 379: return "C"
    if bst < 300: return "D"
    return "Unknown"


async def create_pokemon_embed(pokemon_name: str, title: str, color: discord.Color, is_full_analysis: bool = False,
                               description_override: str = None, force_mega: int = 0) -> discord.Embed | None:
    normalized_name = normalize_pokemon_name(pokemon_name)
    pokemon_data = pokemon_db.get(normalized_name)
    if not pokemon_data:
        print("=" * 60);
        print(f"DEBUG: EMBED CREATION FAILED");
        print(f"  - Pokémon Name from Log: '{pokemon_name}'");
        print(f"  - Searched in Database as: '{normalized_name}'");
        print(f"  - Reason: Name not found in the 'pokemon_data.csv' database.");
        print(f"  - ACTION: Please verify that an entry for '{normalized_name}' exists in your CSV.");
        print("=" * 60)
        return None
    is_mega = force_mega > 0 and pokemon_data.get('has_mega') == 'TRUE'
    if is_mega and force_mega == 2 and pokemon_data.get('has_mega_2') == 'TRUE':
        prefix = "mega_2_"
    else:
        prefix = "mega_"
    if is_mega:
        display_name = pokemon_data.get(f'{prefix}name') or f"Mega {pokemon_data['name'].title()}"
        sprite_url = pokemon_data.get(f'{prefix}sprite_url') or pokemon_data['sprite_url']
        types = [t.strip() for t in (pokemon_data.get(f'{prefix}types') or pokemon_data['types']).split(',')]
        abilities = [a.strip().title() for a in
                     (pokemon_data.get(f'{prefix}abilities') or pokemon_data['abilities']).split(',')]
        stats = {
            'hp': pokemon_data.get(f'{prefix}hp') or pokemon_data['hp'],
            'attack': pokemon_data.get(f'{prefix}attack') or pokemon_data['attack'],
            'defense': pokemon_data.get(f'{prefix}defense') or pokemon_data['defense'],
            'special-attack': pokemon_data.get(f'{prefix}special-attack') or pokemon_data['special-attack'],
            'special-defense': pokemon_data.get(f'{prefix}special-defense') or pokemon_data['special-defense'],
            'speed': pokemon_data.get(f'{prefix}speed') or pokemon_data['speed']
        }
    else:
        display_name = pokemon_data['name'].title()
        sprite_url = pokemon_data['sprite_url']
        types = [t.strip() for t in pokemon_data['types'].split(',')]
        abilities = [a.strip().title() for a in pokemon_data['abilities'].split(',')]
        stats = {
            'hp': pokemon_data['hp'], 'attack': pokemon_data['attack'], 'defense': pokemon_data['defense'],
            'special-attack': pokemon_data['special-attack'], 'special-defense': pokemon_data['special-defense'],
            'speed': pokemon_data['speed']
        }
    description = description_override if description_override is not None else f"Strategic analysis for **{display_name}**"
    embed = discord.Embed(title=title, description=description, color=color)
    if sprite_url: embed.set_image(url=sprite_url)
    if is_full_analysis:
        fields = []
        fields.append(("Type(s)", ' '.join([f"{TYPE_EMOJIS.get(t, '')} {t.title()}" for t in types]), False))
        effectiveness = calculate_effectiveness(types)
        weak_str = ""
        if effectiveness['weaknesses'][
            'x4']: weak_str += f"**Extremely Weak (x4) to:** {', '.join(effectiveness['weaknesses']['x4'])}\n"
        if effectiveness['weaknesses'][
            'x2']: weak_str += f"**Weak (x2) to:** {', '.join(effectiveness['weaknesses']['x2'])}\n"
        fields.append(("⚠️ Weaknesses", weak_str if weak_str else "None", False))
        resist_str = ""
        if effectiveness['resistances']: resist_str += f"**Resists:** {', '.join(effectiveness['resistances'])}\n"
        if effectiveness['immunities']: resist_str += f"**Immune to:** {', '.join(effectiveness['immunities'])}\n"
        fields.append(("🛡️ Resistances & Immunities", resist_str if resist_str else "None", False))
        fields.append(("Abilities", ', '.join(abilities), False))
        stats_str = (
            f"**HP:** {stats['hp']} | **Atk:** {stats['attack']} | **Def:** {stats['defense']} | " f"**SpA:** {stats['special-attack']} | **SpD:** {stats['special-defense']} | **Spe:** {stats['speed']}")
        fields.append(("Base Stats", stats_str, False))
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    else:
        embed.add_field(name="Type(s)", value=' '.join([f"{TYPE_EMOJIS.get(t, '')} {t.title()}" for t in types]),
                        inline=False)
    embed.set_footer(text=f"Pokémon: {pokemon_data['name']} | Good luck!")
    return embed


async def send_push_notification(title: str, message: str, tags: str = "bell", icon_url: str = None):
    if not Config.NTFY.ENABLED: return
    headers = {"Title": title.encode('utf-8'), "Tags": tags}
    if icon_url: headers["Attach"] = icon_url
    try:
        await asyncio.to_thread(requests.post, f"{Config.NTFY.SERVER}/{Config.NTFY.TOPIC}",
                                data=message.encode('utf-8'), headers=headers)
    except Exception as e:
        print(f"ERROR: Failed to send push notification: {e}")


# ### MODIFIED ### - Now returns a tuple (message, icon_url) and has a `full_detail` flag
async def get_push_message_details(pokemon_name: str, message: str, force_mega: int = 0, full_detail: bool = True) -> \
tuple[str, str | None]:
    normalized_name = normalize_pokemon_name(pokemon_name)
    pokemon_data = pokemon_db.get(normalized_name)
    if not pokemon_data:
        return message, None

    is_mega = force_mega > 0 and pokemon_data.get('has_mega') == 'TRUE'
    prefix = "mega_2_" if is_mega and force_mega == 2 and pokemon_data.get('has_mega_2') == 'TRUE' else "mega_"

    if is_mega:
        sprite_url = pokemon_data.get(f'{prefix}sprite_url') or pokemon_data['sprite_url']
        types = [t.strip() for t in (pokemon_data.get(f'{prefix}types') or pokemon_data['types']).split(',')]
        abilities = [a.strip().title() for a in
                     (pokemon_data.get(f'{prefix}abilities') or pokemon_data['abilities']).split(',')]
        stats = {
            'hp': pokemon_data.get(f'{prefix}hp') or pokemon_data['hp'],
            'attack': pokemon_data.get(f'{prefix}attack') or pokemon_data['attack'],
            'defense': pokemon_data.get(f'{prefix}defense') or pokemon_data['defense'],
            'special-attack': pokemon_data.get(f'{prefix}special-attack') or pokemon_data['special-attack'],
            'special-defense': pokemon_data.get(f'{prefix}special-defense') or pokemon_data['special-defense'],
            'speed': pokemon_data.get(f'{prefix}speed') or pokemon_data['speed']
        }
    else:
        sprite_url = pokemon_data['sprite_url']
        types = [t.strip() for t in pokemon_data['types'].split(',')]
        abilities = [a.strip().title() for a in pokemon_data['abilities'].split(',')]
        stats = {
            'hp': pokemon_data['hp'], 'attack': pokemon_data['attack'], 'defense': pokemon_data['defense'],
            'special-attack': pokemon_data['special-attack'], 'special-defense': pokemon_data['special-defense'],
            'speed': pokemon_data['speed']
        }

    effectiveness = calculate_effectiveness(types)
    body_parts = [message, ""]
    body_parts.append(' '.join([f"{TYPE_EMOJIS.get(t, '')} {t.title()}" for t in types]))
    body_parts.append("\n⚠️ **Weaknesses:**")
    if effectiveness['weaknesses']['x4']: body_parts.append(f"  • x4: {', '.join(effectiveness['weaknesses']['x4'])}")
    if effectiveness['weaknesses']['x2']: body_parts.append(f"  • x2: {', '.join(effectiveness['weaknesses']['x2'])}")
    if not effectiveness['weaknesses']['x4'] and not effectiveness['weaknesses']['x2']: body_parts.append("  • None")

    # Only add full details if requested
    if full_detail:
        body_parts.append("\n🛡️ **Resistances & Immunities:**")
        if effectiveness['resistances']: body_parts.append(f"  • Resists: {', '.join(effectiveness['resistances'])}")
        if effectiveness['immunities']: body_parts.append(f"  • Immune to: {', '.join(effectiveness['immunities'])}")
        if not effectiveness['resistances'] and not effectiveness['immunities']: body_parts.append("  • None")
        body_parts.append(f"\n**Abilities:**\n  • {', '.join(abilities)}")
        stats_str = f"HP: {stats['hp']} | Atk: {stats['attack']} | Def: {stats['defense']} | SpA: {stats['special-attack']} | SpD: {stats['special-defense']} | Spe: {stats['speed']}"
        body_parts.append(f"\n**Base Stats:**\n  • {stats_str}")

    return "\n".join(body_parts), sprite_url


def get_player_specific_mention(player_name: str) -> str:
    discord_id = Config.DISCORD.PLAYER_DISCORD_MAP.get(player_name.lower())
    if discord_id and discord_id in subscribed_users:
        return f"<@{discord_id}>"
    return ""


async def schedule_wondertrade_reminder(player_name: str, pokemon_name: str):
    await asyncio.sleep(Config.BEHAVIOR.WONDER_TRADE_COOLDOWN_SEC)
    normalized_name = normalize_pokemon_name(pokemon_name)
    pokemon_data = pokemon_db.get(normalized_name)
    icon_url = pokemon_data.get('sprite_url') if pokemon_data else None
    await send_push_notification("🎁 Wonder Trade Ready!", f"{player_name}, you can Wonder Trade again!", tags="gift",
                                 icon_url=icon_url)
    mention_string = get_player_specific_mention(player_name)
    embed = discord.Embed(title="🎁 Wonder Trade Ready!",
                          description=f"Hey **{player_name}**, your Wonder Trade cooldown has ended. You can trade again!",
                          color=Config.COLORS.INFO)
    embed.add_field(name="Last Trade", value=f"You received a **{pokemon_name.title()}**.")
    embed.set_footer(text="Time to try your luck again!")
    await target_channel.send(content=mention_string, embed=embed)


async def raid_timer_task(message: discord.Message, setup_duration: int):
    try:
        await asyncio.sleep(setup_duration)
        if not message.embeds: return
        ongoing_embed = message.embeds[0].copy()
        ongoing_embed.set_field_at(0, name="⏳ Phase", value="**Fight**", inline=False)
        await message.edit(embed=ongoing_embed)
        await asyncio.sleep(Config.BEHAVIOR.RAID_TIMER_FIGHT_SEC)
        message = await message.channel.fetch_message(message.id)
        if not message.embeds: return
        ended_embed = message.embeds[0].copy()
        ended_embed.set_field_at(0, name="⏳ Phase", value="**Ended**", inline=False)
        await message.edit(embed=ended_embed)
    except discord.NotFound:
        print(f"Raid message {message.id} was deleted before timer could end. Ignoring.")
    except Exception as e:
        print(f"An error occurred in raid_timer_task for message {message.id}: {e}")


async def afk_warning_task(player_name: str):
    try:
        warning_delay = Config.BEHAVIOR.AFK_KICK_TIME_SEC - Config.BEHAVIOR.AFK_WARNING_BEFORE_KICK_SEC
        if warning_delay < 0: warning_delay = 0
        await asyncio.sleep(warning_delay)
        print(f"Sending AFK kick warning for {player_name}.")
        await send_push_notification("AFK Kick Warning!", f"{player_name}, you will be kicked for being idle soon!",
                                     tags="warning")
        mention_string = get_player_specific_mention(player_name)
        kick_timestamp = int(time.time()) + Config.BEHAVIOR.AFK_WARNING_BEFORE_KICK_SEC
        embed = discord.Embed(title=" idling too long!",
                              description=f"**{player_name}**, move or you will be kicked for being AFK!",
                              color=Config.COLORS.INFO)
        embed.add_field(name="Kick Timer", value=f"Kick <t:{kick_timestamp}:R>")
        await target_channel.send(content=mention_string, embed=embed)
    except asyncio.CancelledError:
        print(f"AFK timer for {player_name} was cancelled successfully.")
    except Exception as e:
        print(f"An error occurred in afk_warning_task for {player_name}: {e}")
    finally:
        afk_timers.pop(player_name.lower(), None)


# =================================================================================
# --- BACKGROUND TASKS ---
# =================================================================================
async def monitor_minecraft_chat_loop():
    await bot.wait_until_ready()
    global target_channel
    target_channel = bot.get_channel(Config.DISCORD.CHANNEL_ID)
    if not target_channel:
        print(f"FATAL ERROR: Channel with ID {Config.DISCORD.CHANNEL_ID} not found. Bot cannot continue.")
        return

    print(f"Monitoring Minecraft log at: {Config.MINECRAFT.LOG_FILE_PATH}")
    while True:
        try:
            with open(Config.MINECRAFT.LOG_FILE_PATH, "r", encoding="utf-8") as log_file:
                log_file.seek(0, 2)
                while True:
                    line = log_file.readline()
                    if not line:
                        await asyncio.sleep(0.2)
                        continue
                    if Config.MINECRAFT.LOG_CHAT_PREFIX not in line:
                        continue
                    raw_message = line.split(Config.MINECRAFT.LOG_CHAT_PREFIX, 1)[1].strip()

                    if afk_match := re.search(r"\* (.+?) is now AFK\.", raw_message):
                        player_name = afk_match.group(1)
                        if player_name.lower() in [p.lower() for p in Config.FILTERS.PLAYER_NAMES]:
                            if player_name.lower() in afk_timers: afk_timers[player_name.lower()].cancel()
                            print(f"Player {player_name} is now AFK. Starting 30-minute kick timer.")
                            task = asyncio.create_task(afk_warning_task(player_name))
                            afk_timers[player_name.lower()] = task
                        continue

                    if not_afk_match := re.search(r"\* (.+?) is no longer AFK\.", raw_message):
                        player_name = not_afk_match.group(1)
                        if player_name.lower() in [p.lower() for p in Config.FILTERS.PLAYER_NAMES]:
                            task = afk_timers.pop(player_name.lower(), None)
                            if task: task.cancel(); print(f"Player {player_name} is no longer AFK. Timer cancelled.")
                        continue

                    if wtrade_match := re.search(r"\[WTrade\] » (.+?) received (?:a|an) (.+?) from WonderTrade!",
                                                 raw_message):
                        player_name, pokemon_name = wtrade_match.groups()
                        if player_name.lower() in [p.lower() for p in Config.FILTERS.PLAYER_NAMES]:
                            print(
                                f"Wonder Trade detected for {player_name}. Scheduling a reminder in {Config.BEHAVIOR.WONDER_TRADE_COOLDOWN_SEC / 60} minutes.")
                            asyncio.create_task(schedule_wondertrade_reminder(player_name, pokemon_name))
                        continue

                    if "[Raid]" in raw_message and "A raid is starting against" in raw_message:
                        mention_string = ' '.join(f'<@{uid}>' for uid in subscribed_users)
                        for sub_line in raw_message.split('\\n'):
                            if raid_match := re.search(r"starting against .*?(.+?)!", sub_line, re.I):
                                pokemon_name = raid_match.group(1).strip()
                                normalized_name = normalize_pokemon_name(pokemon_name)
                                pokemon_data = pokemon_db.get(normalized_name, {})
                                is_mega_raid = pokemon_data.get('has_mega') == 'TRUE'
                                raid_tier = determine_raid_tier(pokemon_data, is_mega_raid)
                                setup_time = Config.BEHAVIOR.RAID_TIER_TIMERS_SEC.get(raid_tier,
                                                                                      Config.BEHAVIOR.RAID_TIER_TIMERS_SEC[
                                                                                          "default"])
                                if raid_tier in ["Mega", "Paradox", "S"]:
                                    summary_text = f"**S+ RAID STARTED!** - {pokemon_name.title()}"
                                    push_title = f"S+ RAID - {pokemon_name.upper()}"
                                else:
                                    summary_text = f"**RAID STARTED!** - {pokemon_name.title()}"
                                    push_title = f"RAID STARTED - {pokemon_name.upper()}"

                                # ### MODIFIED ### - Call get_push_message_details with full_detail=False for Raids/Bosses
                                detailed_message, icon_url = await get_push_message_details(pokemon_name,
                                                                                            force_mega=1 if is_mega_raid else 0,
                                                                                            full_detail=False)
                                await send_push_notification(push_title, detailed_message, "battle", icon_url=icon_url)

                                embed_title = "⚔️ RAID STARTED! ⚔️"
                                embed = await create_pokemon_embed(pokemon_name, embed_title, Config.COLORS.RAID,
                                                                   is_full_analysis=True,
                                                                   force_mega=1 if is_mega_raid else 0)
                                if embed:
                                    end_setup_time = int(time.time()) + setup_time
                                    embed.insert_field_at(0, name="⏳ Phase",
                                                          value=f"**Setup** (Ends <t:{end_setup_time}:R>)",
                                                          inline=False)
                                    embed.insert_field_at(1, name="⭐ Raid Tier", value=f"**{raid_tier}**", inline=False)
                                    if pokemon_data.get('has_mega_2') == 'TRUE':
                                        embed.add_field(name="❗️ Multiple Mega Forms",
                                                        value=f"Admin can use `!raid form <message_id> 2` to switch.",
                                                        inline=False)
                                    sent_message = await target_channel.send(
                                        content=f"{summary_text}\n{mention_string}".strip(), embed=embed)
                                    asyncio.create_task(raid_timer_task(sent_message, setup_time))
                                    if pokemon_data.get('has_mega_2') == 'TRUE':
                                        updated_embed = sent_message.embeds[0]
                                        updated_embed.set_field_at(len(updated_embed.fields) - 1,
                                                                   name="❗️ Multiple Mega Forms",
                                                                   value=f"Admin can use `!raid form {sent_message.id} 2` to switch.",
                                                                   inline=False)
                                        await sent_message.edit(embed=updated_embed)
                                else:
                                    print(
                                        f"WARNING: Could not create embed for '{pokemon_name}'. Sending simple alert.")
                                    await target_channel.send(content=f"{summary_text}\n{mention_string}".strip())
                                break
                        continue

                    if boss_match := re.search(
                            r"\[Boss\].*?A (Common|Uncommon|Rare|Legendary) Boss (.+?) has spawned .*? near (.+?)!",
                            raw_message, re.I):
                        rarity, pokemon_name, player_name = boss_match.groups()
                        if player_name.lower() in [p.lower() for p in Config.FILTERS.PLAYER_NAMES]:
                            mention_string = get_player_specific_mention(player_name)
                            detailed_message, icon_url = await get_push_message_details(pokemon_name,
                                                                                        f"A {rarity} Boss has appeared!",
                                                                                        full_detail=False)
                            await send_push_notification(f"BOSS SPAWN ({player_name}) - {pokemon_name.upper()}",
                                                         detailed_message, "rotating_light", icon_url=icon_url)
                            summary_text = f"**⭐ BOSS SPAWNED!** - {pokemon_name.title()} near **{player_name}**"
                            desc = f"A **{rarity} Boss** version of **{pokemon_name.title()}** has spawned near **{player_name}**!"
                            embed = await create_pokemon_embed(pokemon_name, "⭐ BOSS SPAWNED! ⭐", Config.COLORS.BOSS,
                                                               is_full_analysis=True, description_override=desc)
                            if embed:
                                await target_channel.send(content=f"{summary_text}\n{mention_string}".strip(),
                                                          embed=embed)
                            else:
                                print(f"WARNING: Could not create embed for '{pokemon_name}'. Sending simple alert.")
                                await target_channel.send(content=f"{summary_text}\n{mention_string}".strip())
                        continue

                    if shiny_match := re.search(r"A (shiny|shinier|shiniest) (.+?) spawned on (.+?)!", raw_message,
                                                re.I):
                        rarity, pokemon_name, player_name = shiny_match.groups()
                        if player_name.lower() in [p.lower() for p in Config.FILTERS.PLAYER_NAMES]:
                            mention_string = get_player_specific_mention(player_name)
                            detailed_message, icon_url = await get_push_message_details(pokemon_name,
                                                                                        f"A {rarity.title()} {pokemon_name.title()} has appeared!",
                                                                                        full_detail=True)  # Shinies are informational, so full detail is fine
                            await send_push_notification(f"SHINY SPAWN ({player_name}) - {pokemon_name.upper()}",
                                                         detailed_message, "sparkles", icon_url=icon_url)
                            summary_text = f"**✨ SHINY SPAWNED!** - {pokemon_name.title()} for **{player_name}**"
                            desc = f"A **{rarity.title()} {pokemon_name.title()}** has appeared for **{player_name}**!"
                            embed = await create_pokemon_embed(pokemon_name, f"✨ SHINY SPAWNED! ✨", Config.COLORS.SHINY,
                                                               description_override=desc)
                            if embed:
                                await target_channel.send(content=f"{summary_text}\n{mention_string}".strip(),
                                                          embed=embed)
                            else:
                                print(f"WARNING: Could not create embed for '{pokemon_name}'. Sending simple alert.")
                                await target_channel.send(content=f"{summary_text}\n{mention_string}".strip())
                        continue

                    if special_match := re.search(
                            r"A(?:n)? (Ultra Beast|Mythical|Legendary) (.+?) has spawned near (.+?)!", raw_message,
                            re.I):
                        category, pokemon_name, player_name = special_match.groups()
                        if player_name.lower() in [p.lower() for p in Config.FILTERS.PLAYER_NAMES]:
                            mention_string = get_player_specific_mention(player_name)
                            detailed_message, icon_url = await get_push_message_details(pokemon_name,
                                                                                        f"A {category} has appeared!",
                                                                                        full_detail=True)  # Also informational
                            await send_push_notification(
                                f"{category.upper()} SPAWN ({player_name}) - {pokemon_name.upper()}", detailed_message,
                                "warning", icon_url=icon_url)
                            summary_text = f"**‼️ {category.upper()} SPAWNED!** - {pokemon_name.title()} near **{player_name}**"
                            desc = f"A **{category} {pokemon_name.title()}** has appeared near **{player_name}**!"
                            embed = await create_pokemon_embed(pokemon_name, f"‼️ {category.upper()} SPAWNED! ‼️",
                                                               Config.COLORS.LEGENDARY, description_override=desc)
                            if embed:
                                await target_channel.send(content=f"{summary_text}\n{mention_string}".strip(),
                                                          embed=embed)
                            else:
                                print(f"WARNING: Could not create embed for '{pokemon_name}'. Sending simple alert.")
                                await target_channel.send(content=f"{summary_text}\n{mention_string}".strip())
                        continue

                    if raw_message.startswith("[Trivia]"):
                        mention_string = ' '.join(f'<@{uid}>' for uid in subscribed_users)
                        if answer := answer_trivia(raw_message):
                            clean_answer_for_push = answer.replace('**', '')
                            await send_push_notification("Trivia Answer!", clean_answer_for_push, "brain")
                            content = raw_message.replace("[Trivia]", "").replace("»", "").strip()
                            message_body = f"**[Trivia]** {content}"
                            await target_channel.send(f"{message_body}\n{mention_string}".strip())
                            await asyncio.sleep(1)
                            await target_channel.send(answer)
                        continue
        except FileNotFoundError:
            print(f"WARNING: Log file not found. Restart the script when the game is running.")
            await target_channel.send(
                f"<@{Config.DISCORD.ADMIN_ID}> **[ALERT]** » The Minecraft log file disappeared. The bot will stop monitoring and needs to be restarted once the game is running again.")
            await bot.close()
        except Exception as e:
            print(f"CRITICAL ERROR in monitoring loop: {e}")
            if target_channel: await target_channel.send(
                f"<@{Config.DISCORD.ADMIN_ID}> **[CRITICAL ALERT]** » Unexpected error: `{e}`.")
            await asyncio.sleep(30)


@tasks.loop(seconds=30)
async def check_log_file_activity():
    global log_inactivity_warning_sent
    try:
        if not os.path.exists(Config.MINECRAFT.LOG_FILE_PATH): return
        mod_time = datetime.fromtimestamp(os.path.getmtime(Config.MINECRAFT.LOG_FILE_PATH))
        if (datetime.now() - mod_time).total_seconds() > Config.MINECRAFT.IDLE_TIME_UNTIL_WARNING_SEC:
            if not log_inactivity_warning_sent:
                await target_channel.send(
                    f"<@{Config.DISCORD.ADMIN_ID}> **[ALERT]** » The Minecraft log is inactive. The game might be closed or frozen.")
                log_inactivity_warning_sent = True
        elif log_inactivity_warning_sent:
            await target_channel.send(f"**[INFO]** » Minecraft log activity has resumed.")
            log_inactivity_warning_sent = False
    except Exception as e:
        await target_channel.send(
            f"<@{Config.DISCORD.ADMIN_ID}> **[CRITICAL ALERT]** » Error checking log file activity: `{e}`")


@bot.event
async def on_ready():
    global target_channel
    print(f'Bot connected as {bot.user.name} (ID: {bot.user.id})')
    target_channel = bot.get_channel(Config.DISCORD.CHANNEL_ID)
    if not target_channel:
        print(f"FATAL ERROR: Channel with ID {Config.DISCORD.CHANNEL_ID} not found.")
        return await bot.close()
    if Config.BEHAVIOR.CLEAR_CHANNEL_ON_STARTUP:
        try:
            await target_channel.purge(limit=100); print("Channel successfully cleared.")
        except discord.errors.Forbidden:
            print("WARNING: Bot lacks permission to clear messages in the channel.")
        except Exception as e:
            print(f"ERROR: Could not clear the channel: {e}")
    await target_channel.send(f"Bot online! Use `{Config.DISCORD.COMMAND_PREFIX}help` to see all available commands.")
    check_log_file_activity.start()
    bot.loop.create_task(monitor_minecraft_chat_loop())


def is_admin():
    async def predicate(ctx): return ctx.author.id == Config.DISCORD.ADMIN_ID

    return commands.check(predicate)


@bot.command(name='help')
async def show_help_panel(ctx):
    embed = discord.Embed(title="Cobblemon Bot Commands",
                          description=f"Here are the commands you can use. For a list of all automatic features, type `{Config.DISCORD.COMMAND_PREFIX}features`.",
                          color=Config.COLORS.DEFAULT)
    embed.add_field(name="🔔 Discord Mentions",
                    value=f"`{Config.DISCORD.COMMAND_PREFIX}notifications on` - Subscribe to get mentioned in alerts.\n`{Config.DISCORD.COMMAND_PREFIX}notifications off` - Unsubscribe from mentions.\n`{Config.DISCORD.COMMAND_PREFIX}notifications` - Check your current subscription status.",
                    inline=False)
    embed.add_field(name="⚙️ Admin",
                    value=f"`{Config.DISCORD.COMMAND_PREFIX}debug` - Show diagnostic info.\n`{Config.DISCORD.COMMAND_PREFIX}notifications list` - List subscribed users.\n`{Config.DISCORD.COMMAND_PREFIX}raid form <message_id> <1|2>` - Switch a raid to its other Mega form.",
                    inline=False)
    embed.set_footer(text="Bot developed for the Dystoria community.")
    await ctx.send(embed=embed)


@bot.command(name='features', aliases=['skills'])
async def show_features_panel(ctx):
    embed = discord.Embed(title="🤖 Bot Features & Automatic Alerts",
                          description="This bot monitors the game log to provide real-time alerts and assistance. Here's what it does automatically:",
                          color=Config.COLORS.INFO)
    embed.add_field(name="🚨 Smart Raid Alerts",
                    value=f"The bot announces Raids with a live timer that progresses from **Setup** -> **Fight** -> **Ended**. It also automatically assigns a tier and intelligently decides who to mention:\n• **S+ Raids (Mega/Paradox/S):** Mentions everyone subscribed with `!notifications on`.\n• **Personal Events (Boss, Shiny, etc.):** Only mentions the specific user linked to the Minecraft player, and only if they are subscribed.",
                    inline=False)
    embed.add_field(name="🎁 Wonder Trade Reminder",
                    value=f"After a configured player uses Wonder Trade, the bot will post a reminder here and **personally @mention** them (if subscribed) after the {int(Config.BEHAVIOR.WONDER_TRADE_COOLDOWN_SEC / 60)}-minute cooldown has passed.",
                    inline=False)
    embed.add_field(name="👋 AFK Kick Warning",
                    value=f"If a configured player is AFK for {int((Config.BEHAVIOR.AFK_KICK_TIME_SEC - Config.BEHAVIOR.AFK_WARNING_BEFORE_KICK_SEC) / 60)} minutes, the bot will send a warning with a 5-minute countdown to the kick. The timer is cancelled if the player is no longer AFK.",
                    inline=False)
    embed.add_field(name="📱 Push Notifications (Mobile)",
                    value=f"Receive push notifications for all events. **Raids/Bosses** show key weaknesses. **Shinies/Legendaries** show full stats. The **Wonder Trade/AFK** alerts are sent when the final timer is up. To set it up:\n1. Install the **ntfy** app.\n2. Subscribe to the public topic: `{Config.NTFY.TOPIC}`",
                    inline=False)
    embed.set_footer(text="All these features run automatically in the background.")
    await ctx.send(embed=embed)


@bot.group(invoke_without_command=True)
async def notifications(ctx):
    status = "subscribed" if ctx.author.id in subscribed_users else "not subscribed"
    await ctx.send(f"You are currently **{status}** to Discord mention notifications.", ephemeral=True, delete_after=15)
    await ctx.message.delete()


@notifications.command(name='on')
async def notifications_on(ctx):
    if ctx.author.id not in subscribed_users:
        subscribed_users.add(ctx.author.id)
        await ctx.send(f"✅ Subscription activated! You will now be mentioned in relevant Discord alerts.",
                       ephemeral=True, delete_after=10)
    else:
        await ctx.send("You are already subscribed.", ephemeral=True, delete_after=10)
    await ctx.message.delete()


@notifications.command(name='off')
async def notifications_off(ctx):
    if ctx.author.id in subscribed_users:
        subscribed_users.discard(ctx.author.id)
        await ctx.send("❌ Subscription removed. You will no longer be mentioned.", ephemeral=True, delete_after=10)
    else:
        await ctx.send("You were not subscribed in the first place.", ephemeral=True, delete_after=10)
    await ctx.message.delete()


@notifications.command(name='list')
@is_admin()
async def notifications_list(ctx):
    if not subscribed_users:
        return await ctx.send("No users are subscribed to Discord mentions.", ephemeral=True)
    user_mentions = [f"<@{user_id}>" for user_id in subscribed_users]
    embed = discord.Embed(title=f"Discord Mention Subscribers ({len(subscribed_users)})",
                          description="\n".join(user_mentions), color=Config.COLORS.INFO)
    await ctx.send(embed=embed, ephemeral=True)


@bot.group(invoke_without_command=True)
@is_admin()
async def raid(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f"Invalid raid command. Use `{Config.DISCORD.COMMAND_PREFIX}raid form`.", ephemeral=True)


@raid.command(name='form')
@is_admin()
async def raid_form(ctx, message_id: int, form_number: int):
    if form_number not in [1, 2]:
        await ctx.send("❌ Error: Form number must be 1 or 2.", ephemeral=True);
        return
    try:
        message = await ctx.channel.fetch_message(message_id)
    except discord.NotFound:
        await ctx.send("❌ Error: Message ID not found.", ephemeral=True);
        return
    if not message.embeds or message.author.id != bot.user.id or "RAID" not in message.embeds[0].title:
        await ctx.send("❌ Error: The message is not a raid alert from me.", ephemeral=True);
        return
    original_embed = message.embeds[0]
    phase_field = tier_field = None
    for field in original_embed.fields:
        if "Phase" in field.name: phase_field = field
        if "Tier" in field.name: tier_field = field
    try:
        footer_text = original_embed.footer.text
        base_pokemon_name = footer_text.split('|')[0].replace('Pokémon:', '').strip()
    except (IndexError, AttributeError):
        await ctx.send("❌ Error: Could not parse Pokémon name from the embed footer.", ephemeral=True);
        return
    pokemon_data = pokemon_db.get(normalize_pokemon_name(base_pokemon_name))
    if not pokemon_data or pokemon_data.get('has_mega') != 'TRUE':
        await ctx.send("❌ Error: This Pokémon does not have a Mega form.", ephemeral=True);
        return
    if form_number == 2 and pokemon_data.get('has_mega_2') != 'TRUE':
        await ctx.send("❌ Error: This Pokémon does not have a second Mega form.", ephemeral=True);
        return
    new_embed = await create_pokemon_embed(base_pokemon_name, "⚔️ RAID STARTED! ⚔️", Config.COLORS.RAID,
                                           is_full_analysis=True, force_mega=form_number)
    if not new_embed:
        await ctx.send("❌ Error: Failed to generate the new embed for the requested form.", ephemeral=True);
        return
    if phase_field: new_embed.insert_field_at(0, name=phase_field.name, value=phase_field.value,
                                              inline=phase_field.inline)
    if tier_field: new_embed.insert_field_at(1, name=tier_field.name, value=tier_field.value, inline=tier_field.inline)
    if pokemon_data.get('has_mega_2') == 'TRUE':
        new_embed.add_field(name="❗️ Multiple Mega Forms",
                            value=f"Admin can use `!raid form {message.id} {1 if form_number == 2 else 2}` to switch back.",
                            inline=False)
    await message.edit(embed=new_embed)
    await ctx.send(
        f"✅ Switched raid to display **{new_embed.footer.text.split('|')[0].replace('Pokémon:', '').strip()}**.",
        ephemeral=True, delete_after=10)
    await ctx.message.delete()


@bot.command(name='debug')
@is_admin()
async def debug_command(ctx):
    embed = discord.Embed(title="Bot Diagnostic Information", color=Config.COLORS.DEFAULT,
                          timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Log File Path", value=f"```\n{Config.MINECRAFT.LOG_FILE_PATH}```", inline=False)
    if os.path.exists(Config.MINECRAFT.LOG_FILE_PATH):
        stats = os.stat(Config.MINECRAFT.LOG_FILE_PATH)
        mod_time = datetime.fromtimestamp(stats.st_mtime)
        embed.add_field(name="Log Status", value="File Found", inline=True);
        embed.add_field(name="File Size", value=f"{stats.st_size / 1024:.2f} KB", inline=True);
        embed.add_field(name="Last Modified", value=f"<t:{int(mod_time.timestamp())}:R>", inline=False)
    else:
        embed.add_field(name="Log Status", value="**File Not Found**", inline=False)
    player_map_str = "\n".join(
        [f"`{name.lower()}` -> <@{profile['discord_id']}>" for name, profile in USER_PROFILES.items()])
    embed.add_field(name="Player -> Discord Map", value=player_map_str or "Not configured", inline=False)
    embed.add_field(name="Subscribers (Discord @)", value=f"{len(subscribed_users)} user(s)", inline=True)
    embed.add_field(name="Push Notifications (ntfy)", value=f"Active on topic: `{Config.NTFY.TOPIC}`", inline=False)
    embed.set_footer(text=f"Bot: {bot.user.name} | Latency: {bot.latency * 1000:.2f}ms")
    await ctx.send(embed=embed, delete_after=Config.BEHAVIOR.DEBUG_MSG_LIFETIME_SEC)
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass


async def main():
    load_pokemon_data()
    async with bot:
        await bot.start(Config.DISCORD.TOKEN)


if __name__ == "__main__":
    if select_user_and_configure():
        try:
            asyncio.run(main())
        except discord.errors.LoginFailure:
            print("CRITICAL ERROR: Invalid bot token. Please check your config_local.py file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")