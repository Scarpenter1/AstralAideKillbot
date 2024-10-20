import discord
import time
import datetime
from collections import Counter
from .api_request import *
from .config import TARGET_DISCORD_CHANNEL_ID, TARGET_ENTITY_ID, TARGET_ENTITY
from .utils import format_currency, capitalize_and_replace, log_time, get_current_time

semaphore = asyncio.Semaphore(5)  # Limit concurrent tasks

async def send_killmail_embed(bot, killmail):
    print("\n\nhandling killmail")
    print(killmail)
    async with semaphore:
        start_time = get_current_time()
        human_readable_start_time = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
        print(f"Started killmail {killmail.get('killID')} {human_readable_start_time} UTC")
        killmail = await organize_killmail_data(killmail)
        victim = killmail.get('victim')
        if not victim:
            return

        attackers = killmail.get('attackers')
        final_blow_id = next((attacker['character_id'] for attacker in attackers if attacker.get('final_blow') and 'character_id' in attacker), None)

        final_blow_name = await get_player_name(final_blow_id) if final_blow_id else None
        solar_system_name, sec_status = await get_system_name_and_sec_status(killmail.get('solar_system_id'))

        victim_name = await get_player_name(victim.get('character_id')) if 'character_id' in victim else None
        victim_ship = await get_victim_ship(victim.get('ship_type_id'))
        victim_corp = await get_victim_corp(victim.get('corporation_id'))
        victim_alliance = await get_victim_alliance(victim.get('alliance_id')) if 'alliance_id' in victim else None

        killmail_url = f"https://zkillboard.com/kill/{killmail.get('killmail_id')}/"
        zkb_data = killmail.get('zkb', {})
        fitted_value = format_currency(zkb_data.get('fittedValue', 0))
        dropped_value = format_currency(zkb_data.get('droppedValue', 0))
        destroyed_value = format_currency(zkb_data.get('destroyedValue', 0))
        total_value = format_currency(zkb_data.get('totalValue', 0))
        is_loss = int(TARGET_ENTITY_ID) == victim.get("corporation_id") or int(TARGET_ENTITY_ID) == victim.get("alliance_id") and TARGET_ENTITY != 'corporation'

        embed = discord.Embed(
            title=f"{solar_system_name} - ({round(sec_status, 1)})",
            description=killmail_url,
            color=discord.Color.red() if is_loss else discord.Color.green()
        )

        if victim_name:
            embed.add_field(name="Pilot", value=f"[{victim_name}](https://zkillboard.com/character/{victim.get('character_id')}/)", inline=True)

        embed.add_field(name="Corporation", value=f"[{victim_corp}](https://zkillboard.com/corporation/{victim.get('corporation_id')}/)", inline=True)

        if victim_alliance:
            embed.add_field(name="Alliance", value=f"[{victim_alliance}](https://zkillboard.com/alliance/{victim.get('alliance_id')}/)", inline=True)

        embed.add_field(name="Helpful Links", value=f"[evewho](https://evewho.com/character/{victim.get('character_id')}), [dotlan](https://evemaps.dotlan.net/system/{solar_system_name})", inline=False)
        embed.add_field(name="Ship", value=f"[{victim_ship}](https://wiki.eveuniversity.org/{capitalize_and_replace(victim_ship)})", inline=False)
        embed.set_image(url=f"https://images.evetech.net/types/{victim.get('ship_type_id')}/render?size=128")
        embed.add_field(name="Fitted Value", value=fitted_value, inline=True)
        embed.add_field(name="Dropped Value", value=dropped_value, inline=True)
        embed.add_field(name="Destroyed Value", value=destroyed_value, inline=True)
        embed.add_field(name="Total Value", value=total_value, inline=False)

        if final_blow_id:
            embed.add_field(name="Final Blow", value=f"[{final_blow_name}](https://zkillboard.com/character/{final_blow_id})", inline=False)

        if victim_name:
            top_3_kill_names, top_3_loss_names = await get_top_kills_losses(victim['character_id'])
            embed.set_thumbnail(url=f"https://images.evetech.net/characters/{victim['character_id']}/portrait?size=512")

            if top_3_kill_names:
                recent_kill_text = ', '.join(
                    [f"{kill[0]}" 
                    for kill in top_3_kill_names]
                )
                embed.add_field(name="Recent Kills", value=f"[{recent_kill_text}](https://zkillboard.com/character/{victim['character_id']}/kills/)", inline=False)

            if top_3_loss_names:
                recent_loss_text = ', '.join(
                    [f"[{loss[0]}](https://zkillboard.com/character/{victim['character_id']}/losses/shipTypeID/{loss[1]}/)" 
                    for loss in top_3_loss_names]
                )
                embed.add_field(name="Recent Losses", value=f"{recent_loss_text}", inline=False)


        channel = bot.get_channel(TARGET_DISCORD_CHANNEL_ID)
        
        if channel:
            await channel.send(embed=embed)
        else:
            print(f"Channel with ID {TARGET_DISCORD_CHANNEL_ID} not found")
        
        log_time(start_time, killmail.get('killmail_id'))

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