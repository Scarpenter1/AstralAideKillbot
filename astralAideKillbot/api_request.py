import aiohttp
import asyncio
from .config import DELAY
import json
from collections import Counter

async def fetch_data(url):
    print(f"\tcalling {url}")
    await asyncio.sleep(DELAY)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"\t\t\tFailed to fetch data: HTTP {response.status} {url}")
                return {}

async def get_pilot_by_name(name: str):
    url = 'https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en'
    headers = {
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }
    data = json.dumps([name])
    data = await fetch_data(url, headers, data)
    characters = data.get("characters", None)
    print(data)
    print(characters)
    if characters != None:
        character = characters[0]
        return character
    else:
        return None

async def get_name_async(url):
    data = await fetch_data(url)
    return data.get('name')

async def get_system_name_and_sec_status(id):
    url = f'https://esi.evetech.net/latest/universe/systems/{id}'
    data = await fetch_data(url)
    return data.get('name'), data.get('security_status')

async def get_player_name(id):
    url = f'https://esi.evetech.net/latest/characters/{id}/'
    return await get_name_async(url)

async def get_victim_ship(id):
    url = f'https://esi.evetech.net/latest/universe/types/{id}/'
    return await get_name_async(url)

async def get_victim_corp(id):
    url = f'https://esi.evetech.net/latest/corporations/{id}/'
    return await get_name_async(url)

async def get_victim_alliance(id):
    url = f'https://esi.evetech.net/latest/alliances/{id}/'
    return await get_name_async(url)

async def get_kill_loss_data(character_id):
    kill_url = f"https://zkillboard.com/api/kills/characterID/{character_id}/pastSeconds/604800/"
    loss_url = f"https://zkillboard.com/api/losses/characterID/{character_id}/pastSeconds/604800/"

    kills = await fetch_data(kill_url)
    losses = await fetch_data(loss_url)

    return kills, losses

async def fetch_killmail_details(killmail_id, killmail_hash):
    url = f"https://esi.evetech.net/latest/killmails/{killmail_id}/{killmail_hash}/"
    return await fetch_data(url)

async def get_ship_type_name(ship_type_id):
    url = f"https://esi.evetech.net/latest/universe/types/{ship_type_id}/"
    data = await fetch_data(url)
    if isinstance(data, dict):
        return data.get('name', 'Unknown')
    else:
        return 'Unknown'

async def organize_killmail_data(killmail):
    esi_url = f"https://esi.evetech.net/latest/killmails/{killmail.get('killID')}/{killmail.get('hash')}/"
    esi_data = await fetch_data(esi_url)

    zkill_url = f"https://zkillboard.com/api/killID/{killmail.get('killID')}/"
    zkill_data = await fetch_data(zkill_url)

    if zkill_data and 'zkb' in zkill_data[0]:
        esi_data['zkb'] = zkill_data[0]['zkb']

    return esi_data

async def get_top_kills_losses(character_id):
    kills, losses = await get_kill_loss_data(character_id)
    kill_ship_types = [await fetch_killmail_ship_type(kill) for kill in kills]
    loss_ship_types = [await fetch_killmail_ship_type(loss) for loss in losses]
    
    top_3_kill_ship_types = Counter(kill_ship_types).most_common(3)
    top_3_loss_ship_types = Counter(loss_ship_types).most_common(3)

    top_3_kill_names = [[f"{await get_ship_type_name(ship_type) or 'N/A'} ({count})", ship_type] for ship_type, count in top_3_kill_ship_types]
    top_3_loss_names = [[f"{await get_ship_type_name(ship_type) or 'N/A'} ({count})", ship_type] for ship_type, count in top_3_loss_ship_types]
    
    return top_3_kill_names, top_3_loss_names

async def fetch_killmail_ship_type(kill):
    try:
        killmail_id = kill['killmail_id']
        killmail_hash = kill['zkb']['hash']
        killmail_details = await fetch_killmail_details(killmail_id, killmail_hash)
        return killmail_details['victim']['ship_type_id']
    except (KeyError, TypeError):
        return None