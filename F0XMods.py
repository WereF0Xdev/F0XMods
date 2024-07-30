import discord
from discord.ext import commands, tasks
import json
import random
from datetime import timedelta
import requests
from mcipc.query import Client
from mcstatus import JavaServer
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yt_dlp as youtube_dl
import asyncio
import aiofiles
from dotenv import load_dotenv
import os
import openai

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

api_key = os.getenv("OPENAI_API_KEY")

# Access the variables
CURSEFORGE_API_KEY = os.getenv("CURSEFORGE_API_KEY")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

TOKEN = os.getenv("TOKEN")

chatgpt = api_key

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_new_videos.start()
    load_tickets()

developer_id = 984121073173921863

STAFF_ID = [984121073173921863, 796974752546947113]

role_id = 1148982361518776320
reaction_emoji = "🟢" 

tester_role_id = 1256872666351271986  
developer_role_id = 1148982361518776320  
tester_emoji = "🟢"
developer_emoji = "🔸"

log_channel_id = 1267426335689801738

ticket_channels = {}

TICKET_FILE = "tickets.json"


# MODS / MISCELLANEOUS SECTION


@bot.command()
async def order(ctx, title: str = None, version: str = None, loader: str = None, price: int = None, username: str = None, *, desc: str = None):

    if title is None:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Please provide a title for your commission!",
                          color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    if version is None:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Please provide the version you'd want your mod to be for.",
                          color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if loader is None:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Please specify a loader for your mod! Typical loaders are for example Forge, Fabric, Spigot, Bukkit etc.",
                          color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    if price is None:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Please specify the price you'd like to ask for. Please insert a price suited for the complexity of your mod.",
                          color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    if username is None:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Please provide your Discord username if the developer needs to contact you. Make sure you send your correct USERNAME and not DISPLAY NAME!",
                          color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if version not in ["1.20.1", "1.20.4"]:
        embed = discord.Embed(title=":mag_right: Just a tip!",
                          description=f"Hey! Please keep in mind that versions older than 1.20.1 are discontinued, and commissions on older versions are often rejected. If possible, request mods for 1.20.1 or 1.20.4! (You can proceed with your request from here)",
                          color=discord.Color.blue())
        await ctx.send(embed=embed)

    if desc is None:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Please provide a description for your mod! Don't make it too short, it has to include everything that you want to be added, including details as the developer will need a clear vision of your idea.",
                          color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if len(desc) < 30:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Hey! Please provide a longer description, fill in everything the developer should know! (Minimum 30 characters)",
                          color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if price <= 0:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Hey! Unfortunately free commissions were dismissed around 6 months ago, so you're a bit late! Don't worry, a cheap alternative might be just around the corner. Submit your commission with the price you'd want and hope for the best!",
                          color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title="New Commission Received",
                          description=f"Commission received from **{ctx.author}**",
                          color=discord.Color.green())
    embed.add_field(name="Title", value=title, inline=False)
    embed.add_field(name="Version", value=version, inline=False)
    embed.add_field(name="Description", value=desc, inline=False)
    embed.add_field(name="Loader", value=loader, inline=False)
    embed.add_field(name="Price", value=f"${price}", inline=False)
    embed.add_field(name="Username", value=username, inline=False)

    await ctx.send(embed=embed)

    developer_user = bot.get_user(developer_id)
    if developer_user is not None:
        try:
            await developer_user.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I couldn't send the commission details to the developer. Please check their privacy settings.")
    else:
        await ctx.send("Developer user not found.")



@bot.command()
async def hello(ctx):
    user = ctx.author.id
    embed = discord.Embed(title="Hi!",
                          description=f"Nice to meet you, {ctx.author.mention}!",
                          color=discord.Color.green())
    if ctx.author.id == 1201786714318983212:
        await ctx.send("No you smell")
    elif ctx.author.id == 349241986701852672:
        embed = discord.Embed(title="Yo!",
                          description=f"What's up {ctx.author.mention}?",
                          color=discord.Color.yellow())
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=embed)

@bot.command()
async def hi(ctx):
    rnum = random.randint(1, 4)
    
    if rnum == 1:
        embed = discord.Embed(
            title="Hi!",
            description=f"Nice to meet you, {ctx.author.mention}!",
            color=discord.Color.green()
        )
    elif rnum == 2:
        embed = discord.Embed(
            title="No!",
            description=f"Oh hell no you stink {ctx.author.mention}!",
            color=discord.Color.red()
        )
    elif rnum == 3:
        embed = discord.Embed(
            title="Yo!",
            description=f"What's up {ctx.author.mention}? You sound cool as hell 😎",
            color=discord.Color.yellow()
        )
    elif rnum == 4:
        embed = discord.Embed(
            title="GG",
            description=f"{ctx.author.mention} got owned and muted 💀",
            color=discord.Color.blue()
        )
        
    await ctx.send(embed=embed)
    
    if rnum == 4:
        try:
            duration = timedelta(minutes=1)
            end_time = datetime.utcnow() + duration
            await ctx.author.edit(timed_out_until=end_time, reason="GG")
        except Exception as e:
            await ctx.send(f"")




@bot.command()
async def mod(ctx, identifier: str):
    api_endpoint = "https://api.curseforge.com/v1/mods"
    api_key = CURSEFORGE_API_KEY 

    headers = {
        "x-api-key": api_key
    }

    if identifier.isdigit():
        url = f"{api_endpoint}/{identifier}"
    else:
        search_endpoint = f"{api_endpoint}/search"
        params = {
            "gameId": 432,
            "searchFilter": identifier
        }
        search_response = requests.get(search_endpoint, headers=headers, params=params)
        if search_response.status_code == 200:
            search_results = search_response.json()
            if search_results['data']:
                mod_id = search_results['data'][0]['id']
                url = f"{api_endpoint}/{mod_id}"
            else:
                await ctx.send("No mod found with that identifier.")
                return
        else:
            await ctx.send(f"Error: {search_response.status_code} - {search_response.text}")
            return

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        mod_details = response.json()['data']
        extracted_data = {
            'Name or Slug': mod_details.get('name') or mod_details.get('slug'),
            'Description': mod_details.get('summary'),
            'Logo': mod_details.get('logo', {}).get('url'),
            'Author': mod_details.get('authors', [{}])[0].get('name'),
            'Versions': list(set(v for file in mod_details.get('latestFiles', []) for v in file.get('gameVersions', []))),
            'DownloadLink': mod_details.get('links', {}).get('websiteUrl'),
            'Downloads': mod_details.get('downloadCount')
        }

        embed = discord.Embed(
            title=extracted_data['Name or Slug'],
            description=extracted_data['Description'],
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=extracted_data['Logo'])
        embed.add_field(name="Author", value=extracted_data['Author'], inline=False)
        embed.add_field(name="Versions", value=", ".join(extracted_data['Versions']), inline=False)
        embed.add_field(name="Downloads", value=f"{extracted_data['Downloads']:,}", inline=False)
        embed.add_field(name="Download", value=f"[Download Here]({extracted_data['DownloadLink']})", inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Error: {response.status_code} - {response.text}")



@bot.command()
async def find_server(ctx, ip):
    server = JavaServer.lookup(ip)
    status = server.status()
    embed = discord.Embed(
            title=f"**SERVER INFO**",
            description=f'''**IP:** {ip}
 **Online players:** {status.players.online}''',
            color=discord.Color.green()
        )
    await ctx.send(embed=embed)

@find_server.error
async def find_server_error(ctx, error):
    await ctx.send(f"There was an error retrieving information about the server. Is the IP correct?")


import aiohttp
import io

async def get_uuid(username):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['id']
                else:
                    return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@bot.command()
async def skin(ctx, username):
    uuid = await get_uuid(username)
    if uuid:
        skin_url = f"https://crafatar.com/renders/body/{uuid}"
        async with aiohttp.ClientSession() as session:
            async with session.get(skin_url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    skin_file = discord.File(io.BytesIO(data), filename=f"{username}.png")
                    await ctx.send(f"Skin for {username}:", file=skin_file)
                else:
                    await ctx.send('Could not download file...')
    else:
        await ctx.send(f"Unable to find UUID for {username}")



# EVENTS




@bot.event
async def on_member_join(member):
    role_name = "Member"
    guild = member.guild
    role = discord.utils.get(guild.roles, name=role_name)
    
    if role:
        await member.add_roles(role)
        print(f'Assigned {role_name} role to {member.name}')
    else:
        print(f'Role "{role_name}" not found')



@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return

    if payload.emoji.name == tester_emoji:
        role = guild.get_role(tester_role_id)
    elif payload.emoji.name == developer_emoji:
        role = guild.get_role(developer_role_id)
    else:
        return

    if role:
        await member.add_roles(role)
        print(f"Assigned {role.name} role to {member.name}")



@bot.event
async def on_raw_reaction_remove(payload):
    if payload.emoji.name == reaction_emoji:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(role_id)
        if role:
            member = guild.get_member(payload.user_id)
            if member and not member.bot:
                await member.remove_roles(role)
                print(f"Removed role from {member.name}")



@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return

    if payload.emoji.name == tester_emoji:
        role = guild.get_role(tester_role_id)
    elif payload.emoji.name == developer_emoji:
        role = guild.get_role(developer_role_id)
    else:
        return

    if role:
        await member.add_roles(role)
        print(f"Assigned {role.name} role to {member.name}")



@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return

    if payload.emoji.name == tester_emoji:
        role = guild.get_role(tester_role_id)
    elif payload.emoji.name == developer_emoji:
        role = guild.get_role(developer_role_id)
    else:
        return

    if role:
        await member.remove_roles(role)
        print(f"Removed {role.name} role from {member.name}")



@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    log_channel = bot.get_channel(log_channel_id)
    if log_channel:
        embed = discord.Embed(
            title="Message Deleted",
            description=f"**Author:** {message.author.mention}\n"
                        f"**Channel:** {message.channel.mention}\n"
                        f"**Content:** {message.content or 'No content'}",
            color=discord.Color.red()
        )
        await log_channel.send(embed=embed)



# MODERATION COMMANDS


@bot.command()
async def role(ctx, member: discord.Member = None, *, role_name: str):
    if ctx.author.id != developer_id:
        embed = discord.Embed(
            title="❌ Error",
            description=f"You do not have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if member is None:
        embed = discord.Embed(
            title="❌ Error",
            description=f"You must specify a member to add the role to.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return


    role = discord.utils.get(ctx.guild.roles, name=role_name)
    
    if role:
        await member.add_roles(role)
        embed = discord.Embed(
            title="✅ Success",
            description=f"Role {role_name} has been added to {member.name}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        print(f"Role {role_name} added to {member.name} by {ctx.author.name}.")
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Role {role_name} not found.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        print(f"Role {role_name} not found for {member.name} by {ctx.author.name}.")



@bot.command()
async def reaction_roles(ctx):
    guild = ctx.guild
    tester_role = guild.get_role(tester_role_id)
    developer_role = guild.get_role(developer_role_id)
    
    if not tester_role or not developer_role:
        await ctx.send("Roles not found in the server.")
        return

    embed = discord.Embed(
        title="⭐️ Reaction Roles",
        description=f"React with {tester_emoji} to apply for {tester_role.mention} role and with {developer_emoji} to enter Developer Mode!",
        color=0xFFFF00
    )
    message = await ctx.send(embed=embed)
    await message.add_reaction(tester_emoji)
    await message.add_reaction(developer_emoji)



# AUTOMATIC YT VIDEO CHECKER



CUSTOM_URL_HANDLE = 'Were_F0X'
DISCORD_CHANNEL_ID = 1144945925240934400  


last_video_id = None



def get_channel_id(custom_handle):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={custom_handle}&key={YOUTUBE_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get('items')
        if items:
            return items[0]['snippet']['channelId']
    return None


def get_latest_video(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={channel_id}&part=snippet,id&order=date&maxResults=1'
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get('items')
        if items:
            return items[0]
    return None

@tasks.loop(minutes=15)
async def check_new_videos():
    global last_video_id
    channel_id = get_channel_id(CUSTOM_URL_HANDLE)
    if channel_id:
        latest_video = get_latest_video(channel_id)
        if latest_video:
            video_id = latest_video['id'].get('videoId')
            if video_id and video_id != last_video_id:
                last_video_id = video_id
                video_details = latest_video['snippet']
                embed = discord.Embed(
                    title="WereF0X just uploaded a new video!",
                    color=discord.Color.red()
                )
                embed.set_image(url=video_details['thumbnails']['high']['url'])
                embed.add_field(name=video_details['title'], value=f"[Watch here!](<https://www.youtube.com/watch?v={video_id}>)", inline=False)
                channel = bot.get_channel(DISCORD_CHANNEL_ID)
                if channel:
                    await channel.send(embed=embed)



@bot.command()
async def check_videos(ctx):
    check_new_videos.start()



# AI


from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
os.environ.get("OPENAI_API_KEY")

openai.api_key = api_key

client = OpenAI()




@bot.command(name='deprecated_ai')
@commands.cooldown(1, 30, commands.BucketType.user)
async def deprecated_ai(ctx, *, message: str):

    if ctx.author.id == developer_id:
        ai_max_tokens = 1000
    else:
        ai_max_tokens = 500

    try:
        completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": f"{message}"}
  ]
,
            max_tokens=ai_max_tokens  # Adjust as necessary
        )
        color = discord.Color(random.randint(0, 0xFFFF))

        embed = discord.Embed(
                title="",
                description=completion.choices[0].message.content,
                color=color
            )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")




@bot.command(name='buff_ai')
async def buff_ai(ctx, *, message: str):

    if ctx.author.id != developer_id:
        await ctx.send("No permission. Use `!ai`.")
        return
    ai_max_tokens = 1000

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're a helpful assistant."},
                {"role": "user", "content": message}
            ],
            max_tokens=ai_max_tokens  # Adjust as necessary
        )
        color = discord.Color(random.randint(0, 0xFFFF))

        embed = discord.Embed(
                title="",
                description=response['choices'][0]['message']['content'].strip(),
                color=color
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")




@bot.command(name='roleplay')
@commands.cooldown(1, 30, commands.BucketType.user)
async def roleplay(ctx, character: str = None, *, message: str):
    return
    if character is None:
        await ctx.send("This command is used for roleplay and you must specify a character for me to roleplay as. To use normal AI commands, use `!ai`")
        return

    if ctx.author.id == developer_id:
        ai_max_tokens = 300
    else:
        ai_max_tokens = 200

    try:
        completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": f"Imagine you are {character} and have a conversation with them."},
    {"role": "user", "content": f"{message}"}
  ]
,
            max_tokens=ai_max_tokens  # Adjust as necessary
        )
        color = discord.Color(random.randint(0, 0xFFFF))

        embed = discord.Embed(
                title="",
                description=completion.choices[0].message.content,
                color=color
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")


ai_assistant_id = "asst_12yy4IGQzG2RF0vWutoWt9r7"



@bot.command()
@commands.cooldown(1, 40, commands.BucketType.user)
async def ai(ctx, *, prompt: str = None):
    return
    if prompt is None:
        await ctx.send("What did you want to ask me?")
        return
    

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content=f"{prompt}"
)
    run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id,
      assistant_id=ai_assistant_id,
      instructions="Please help the user answering his questions and helping with code if requested."
)
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
        thread_id=thread.id
  )
        
        print(messages)
        color = discord.Color(random.randint(0, 0xFFFF))

        embed = discord.Embed(
                title="F0X Mods AI Assistant",
                description=messages.data[0].content[0].text.value,
                color=color
        )
        await ctx.send(embed=embed)
    else:
        print(run.status)








# AFFILIATES SECTION
async def ensure_affiliates_file():
    if not os.path.exists('affiliates.json'):
        async with aiofiles.open('affiliates.json', 'w') as f:
            await f.write('{}')


async def load_affiliates():
    await ensure_affiliates_file()
    async with aiofiles.open('affiliates.json', 'r') as f:
        affiliates = await f.read()
        return json.loads(affiliates)


async def save_affiliates(affiliates):
    async with aiofiles.open('affiliates.json', 'w') as f:
        await f.write(json.dumps(affiliates, indent=4))


async def check_affiliates(user_id, affiliates):
    if str(user_id) not in affiliates:
        affiliates[str(user_id)] = {"affiliate": 0, "balance": 0, "daily-points": 0.03}
        await save_affiliates(affiliates)




affiliate_functions = ["status", "balance", "withdraw"]

affiliate_reports_channel = 1267426335689801738



async def affiliate_error_parameters(ctx):
    embed = discord.Embed(
        title="❌ Error",
        description=(
            "You must specify what function of the Affiliate command you want to call.\n"
            "- Use `!affiliate status` to check your Affiliate status\n"
            "- Use `!affiliate balance` to check your Affiliate balance\n"
            "- Use `!affiliate withdraw` to withdraw your balance\n"
            "- Use `!claim` to claim your daily credits"
        ),
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


async def affiliate_error_false(ctx):
    embed = discord.Embed(
        title="❌ Not an Affiliate",
        description="You are not an Affiliate. If you wish to apply for Affiliate, you can do it ~~here~~ [Applications closed]",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


async def affiliate_error_low_balance(ctx):
    embed = discord.Embed(
        title="❌ Error",
        description="Your balance is too low to withdraw. The withdraw threshold is 3.00$.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


async def affiliate_withdraw_message(ctx):
    embed = discord.Embed(
        title="💸 Withdraw Balance",
        description=(
            "Thank you for being a F0X Mods Affiliate.\n"
            "Your request has been received and a Staff Member will shortly address your request."
        ),
        color=discord.Color.yellow()
    )
    await ctx.send(embed=embed)


@bot.command()
async def affiliate(ctx, function: str = None):
    affiliates = await load_affiliates()
    await check_affiliates(ctx.author.id, affiliates)

    if function is None or function not in affiliate_functions:
        await affiliate_error_parameters(ctx)
        return

    if affiliates[str(ctx.author.id)]['affiliate'] == 0:
        await affiliate_error_false(ctx)
        return

    if function == "status":
        embed = discord.Embed(
            title="ℹ️ Affiliate Status",
            description="You are an **Affiliate**.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    elif function == "balance":
        embed = discord.Embed(
            title="💰 Affiliate Balance",
            description=f"Nice to see you, Affiliate {ctx.author.mention}!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Your Balance",
            value=f"{affiliates[str(ctx.author.id)]['balance']}$"
        )
        await ctx.send(embed=embed)

    elif function == "withdraw":
        if affiliates[str(ctx.author.id)]['balance'] < 3:
            await affiliate_error_low_balance(ctx)
        else:
            await affiliate_withdraw_message(ctx)
            embed = discord.Embed(
                title="📋 Withdraw Details",
                description=(
                    f"### Affiliate: {ctx.author.mention}\n"
                    f"### Withdrawn Balance: {affiliates[str(ctx.author.id)]['balance']}$"
                ),
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
            channel = bot.get_channel(affiliate_reports_channel)
            if channel:
                embed = discord.Embed(
                    title="💸 Withdraw Request",
                    description=(
                        f"### Affiliate: {ctx.author.mention}\n"
                        f"### Withdrawn Balance: {affiliates[str(ctx.author.id)]['balance']}$"
                    ),
                    color=discord.Color.green()
                )
                await channel.send(embed=embed)




@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def claim(ctx):
    affiliates = await load_affiliates()
    await check_affiliates(ctx.author.id, affiliates)

    if affiliates[str(ctx.author.id)]['affiliate'] != 1:
        await affiliate_error_false()
    affiliates[str(ctx.author.id)]['balance'] = affiliates[str(ctx.author.id)]['balance'] + affiliates[str(ctx.author.id)]['daily-points']
    await save_affiliates(affiliates)

    embed = discord.Embed(
                title="🎁 Daily Credits Claimed",
                description=(
                    f"### Affiliate: {ctx.author.mention}\n"
                    f"### Credits Claimed: {affiliates[str(ctx.author.id)]['daily-points']}$"
                ),
                color=discord.Color.green()
            )
    await ctx.send(embed=embed)



# TICKETS

def ensure_ticket_file():
    if not os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, 'w') as f:
            json.dump({}, f)

def load_tickets():
    global ticket_channels
    ensure_ticket_file()
    with open(TICKET_FILE, 'r') as f:
        ticket_channels = json.load(f)

def save_tickets():
    with open(TICKET_FILE, 'w') as f:
        json.dump(ticket_channels, f)


STAFF_ROLE_ID = 1130230179646689461




@bot.command()
async def ticket(ctx, action: str):
    if action == "open":
        await open_ticket(ctx)
    elif action == "claim":
        await claim_ticket(ctx)
    elif action == "close":
        await close_ticket(ctx)
    else:
        await ctx.send("Invalid action. Use !ticket <open|claim|close>")

async def open_ticket(ctx):
    guild = ctx.guild
    if str(ctx.author.id) in ticket_channels:
        await ctx.send("You already have an open ticket. Please have only one ticket at a time. You can close the other ticket anytime with `!ticket close`")
        return
    category = discord.utils.get(guild.categories, name="Tickets")
    if category is None:
        category = await guild.create_category("Tickets")

    ticket_channel = await guild.create_text_channel(
        f"ticket-{ctx.author.name}",
        category=category,
        overwrites={
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True),
            guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(read_messages=True)
        }
    )

    ticket_channels[str(ctx.author.id)] = ticket_channel.id
    save_tickets()
    embed = discord.Embed(
                title="Ticket Created",
                description=(
                    f"{ctx.author.mention} Your ticket has been created. A staff member will be with you shortly."
                ),
                color=discord.Color.blue()
            )
    await ticket_channel.send(embed=embed)
    await ctx.send(f"Ticket created: {ticket_channel.mention}")

async def claim_ticket(ctx):
    if ctx.author.id not in STAFF_ID:
        await ctx.send("You do not have permission to use this command.")
        return

    if ctx.channel.id not in ticket_channels.values():
        await ctx.send("This is not a ticket channel.")
        return

    await ctx.send(f"Ticket claimed by {ctx.author.mention}")
    ticket_creator_id = next((k for k, v in ticket_channels.items() if v == ctx.channel.id), None)
    if ticket_creator_id:
        ticket_creator = discord.utils.get(ctx.guild.members, id=int(ticket_creator_id))
        if ticket_creator:
            await ctx.channel.send(f"{ticket_creator.mention} Your ticket has been claimed by {ctx.author.mention}")

async def close_ticket(ctx):
    if ctx.channel.id not in ticket_channels.values():
        await ctx.send("This is not a ticket channel.")
        return

    await ctx.channel.delete()
    ticket_creator_id = next((k for k, v in ticket_channels.items() if v == ctx.channel.id), None)
    if ticket_creator_id:
        del ticket_channels[ticket_creator_id]
        save_tickets()
        await ctx.send("Ticket closed.")





# COMMANDS ERRORS AND COOLDOWNS



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="Cooldown",
            description=f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send('There was an error. Either the command does not exist or the parameters were wrong.')


# RUN THE BOT

bot.run(TOKEN)