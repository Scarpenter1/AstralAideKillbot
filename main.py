import discord
import asyncio
from discord.ext import commands
from astralAideKillbot.config import TOKEN, TARGET_DISCORD_CHANNEL_ID
from astralAideKillbot.websocket_handler import subscribe_to_websocket
from astralAideKillbot.api_request import  get_pilot_by_name
# from astralAideKillbot.config import TARGET_DISCORD_CHANNEL_ID

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    bot.loop.create_task(subscribe_to_websocket(bot))  # Pass bot to the websocket handler
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(TARGET_DISCORD_CHANNEL_ID)
    if channel:
        await channel.send("Connected Successfully")
    else:
        print(f"Channel with ID {TARGET_DISCORD_CHANNEL_ID} not found")

# @bot.command(name='pilot')
# async def pilot(ctx, *, name: str):  # The asterisk allows capturing the entire string as 'name'
#     if ctx.channel.id != TARGET_DISCORD_CHANNEL_ID:
#         await ctx.send("This command can't be used in this channel.")
#         return

#     pilot_data = await get_pilot_by_name(name)
    
#     if pilot_data:
#         await ctx.send(f'Pilot data for {name}: {pilot_data}')
#     else:
#         await ctx.send(f'Could not find pilot data for {name}.')

# @bot.event
# async def on_message(message):
#     if bot.user in message.mentions and not message.mention_everyone:
#         embed = discord.Embed(
#             title="Greeting",
#             description=f'Hello {message.author.display_name}!',
#             color=discord.Color.blue()
#         )
#         await message.channel.send(embed=embed)
        
#     await bot.process_commands(message)

bot.run(TOKEN)
