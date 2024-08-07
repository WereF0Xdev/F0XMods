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
from pathlib import Path



load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

api_key = os.getenv("OPENAI_API_KEY")


CURSEFORGE_API_KEY = os.getenv("CURSEFORGE_API_KEY")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

TOKEN = os.getenv("TOKEN")

DATABASE_USER = os.getenv("DATABASE_USER")

DATABASE_NAME = os.getenv("DATABASE_NAME")

DATABASE_PASSW = os.getenv("DATABASE_PASSW")

DATABASE_HOST = os.getenv("DATABASE_HOST")

chatgpt = api_key

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)


guild_ids = [1130229274452971581]

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



# UI SETUP

class OpenTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Open a ticket", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await open_ticket(interaction)
        

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(OpenTicketButton())




# MODS / MISCELLANEOUS SECTION


@bot.slash_command(
  name="order",
  description="Order a Mod from the server developer",
  guild_ids=guild_ids
)
async def order(ctx, title: str, version: str, loader: str, price: int, username: str, *, desc: str):
    if len(desc) < 30:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Hey! Please provide a longer description, fill in everything the developer should know! (Minimum 30 characters)",
                          color=discord.Color.red())
        await ctx.respond(embed=embed)
        return

    if price <= 0:
        embed = discord.Embed(title="❌ Something went wrong...",
                          description=f"Hey! Unfortunately free commissions were dismissed, Don't worry, cheap commissions are sometimes given for free.",
                          color=discord.Color.red())
        await ctx.respond(embed=embed)
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

    await ctx.respond(embed=embed)

    developer_user = bot.get_user(developer_id)
    if developer_user is not None:
        try:
            await developer_user.respond(embed=embed)
        except discord.Forbidden:
            await ctx.respond("I couldn't send the commission details to the developer. Please check their privacy settings.")
    else:
        await ctx.respond("Developer user not found.")



@bot.slash_command(
  name="hello",
  description="Say hello!",
  guild_ids=guild_ids
)
async def hi(ctx):
    rnum = random.randint(1, 3)
    
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

    await ctx.respond(embed=embed)


@bot.slash_command(
  name="mod",
  description="Make the bot find you a mod on CurseForge",
guild_ids=guild_ids
)
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
                await ctx.respond("No mod found with that identifier.")
                return
        else:
            await ctx.respond(f"Error: {search_response.status_code} - {search_response.text}")
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

        await ctx.respond(embed=embed)
    else:
        await ctx.respond(f"Error: {response.status_code} - {response.text}")



@bot.slash_command(
  name="server",
  description="Find info on a server",
  guild_ids=guild_ids
)
async def find_server(ctx, ip):
    server = JavaServer.lookup(ip)
    status = server.status()
    embed = discord.Embed(
            title=f"**SERVER INFO**",
            description=f'''**IP:** {ip}
 **Online players:** {status.players.online}''',
            color=discord.Color.green()
        )
    await ctx.respond(embed=embed)

@find_server.error
async def find_server_error(ctx, error):
    await ctx.respond(f"There was an error retrieving information about the server. Is the IP correct?")


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

@bot.slash_command(
  name="skin",
  description="Get any player's skin",
  guild_ids=guild_ids
)
async def skin(ctx, username):
    uuid = await get_uuid(username)
    if uuid:
        skin_url = f"https://crafatar.com/renders/body/{uuid}"
        async with aiohttp.ClientSession() as session:
            async with session.get(skin_url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    skin_file = discord.File(io.BytesIO(data), filename=f"{username}.png")
                    await ctx.respond(f"Skin for {username}:", file=skin_file)
                else:
                    await ctx.respond('Could not download file...')
    else:
        await ctx.respond(f"Unable to find UUID for {username}")



# EVENTS

@bot.event
async def on_ready():
    await update_all_affiliates()
    print(f'Logged in as {bot.user}')
    load_tickets()


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

    try:
        color = discord.Color(random.randint(0, 0xFFFF))

        embed = discord.Embed(
                title="Welcome!",
                description=f"Welcome {member.mention} to F0X Mods! Make yourself at home, visit the rules and happy stay!",
                color=color
        )
        await member.send(embed=embed)
        print(f"Sent welcome message to {member.name}")
    except discord.Forbidden:
        return
    except discord.HTTPException as e:
        return





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


@bot.slash_command(
  name="role",
  description="Add a role to any user",
  guild_ids=guild_ids
)
async def role(ctx, member: discord.Member, *, role_name: str):
    if ctx.author.id != developer_id:
        embed = discord.Embed(
            title="❌ Error",
            description=f"You do not have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)
        return



    role = discord.utils.get(ctx.guild.roles, name=role_name)
    
    if role:
        await member.add_roles(role)
        embed = discord.Embed(
            title="✅ Success",
            description=f"Role {role_name} has been added to {member.name}.",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)
        print(f"Role {role_name} added to {member.name} by {ctx.author.name}.")
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Role {role_name} not found.",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)
        print(f"Role {role_name} not found for {member.name} by {ctx.author.name}.")



@bot.slash_command(
  name="dm",
  description="DM a user",
  guild_ids=guild_ids
)
async def dm(ctx, member: discord.Member, title: str, *, description: str):
    if ctx.author.id not in STAFF_ID:
        await ctx.send("You don't have permission to use this command.")
        return

    color = discord.Color(random.randint(0, 0xFFFF))

    embed = discord.Embed(
            title=f"{title}",
            description=f"{description}",
            color=color
    )
    await member.send(embed=embed)
    print(f"Sent message to {member.name}")
    await ctx.respond(f"Message sent to {member.name}")




# AI


from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
os.environ.get("OPENAI_API_KEY")

openai.api_key = api_key

client = OpenAI()




@bot.slash_command(
  name='roleplay',
  description="Have the AI roleplay as any character",
  guild_ids=guild_ids
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def roleplay(ctx, character: str, *, message: str):

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
                title="F0X Mods Roleplay AI",
                description=completion.choices[0].message.content,
                color=color
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.respond(f"An error occurred: {str(e)}")


ai_assistant_id = "asst_12yy4IGQzG2RF0vWutoWt9r7"



@bot.slash_command(
  name="ai",
  description="Ask anything to the AI",
  guild_ids=guild_ids
)
@commands.cooldown(1, 40, commands.BucketType.user)
async def ai(ctx, *, prompt):
    await ctx.respond("The AI is thinking...", ephemeral=True)
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
    asyncio.sleep(5)
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
        thread_id=thread.id
  )
        
        print(messages)
        color = discord.Color(random.randint(0, 0xFFFF))

        embed = discord.Embed(
                title="F0X Mods AI Assistant",
                description=f"### Replying to {ctx.author.mention}\n{messages.data[0].content[0].text.value}",
                color=color
        )
        embed.set_footer(text=f"Request: {prompt}")

        await ctx.send(embed=embed)



    if ctx.author.voice is None or ctx.author.voice.channel is None:
        return

    voice_channel = ctx.author.voice.channel

    
    if ctx.voice_client is None:
        vc = await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client

    
    speech_file_path = Path(__file__).parent / "speech.mp3"

    
    speech_file_path.parent.mkdir(parents=True, exist_ok=True)

    
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=f"{messages.data[0].content[0].text.value}"
    )

 
    response.stream_to_file(speech_file_path)

    
    if vc.is_playing():
        vc.stop()

    vc.play(discord.FFmpegPCMAudio(str(speech_file_path)), after=lambda e: print('done', e))





@bot.slash_command(
  name="generate",
  description="Ask the AI to generate an image",
  guild_ids=guild_ids
)
async def generate(ctx, *,  prompt: str):
    await ctx.respond("The AI is thinking...", ephemeral=True)

    response = client.images.generate(
  model="dall-e-3",
  prompt=f"{prompt}",
  size="1024x1024",
  quality="standard",
  n=1,
)

    image_url = response.data[0].url


    color = discord.Color(random.randint(0, 0xFFFF))

    embed = discord.Embed(
                title="F0X Mods AI Image Generator",
                description=f"### Replying to {ctx.author.mention}",
                color=color
        )

    embed.set_image(url=image_url)

    embed.set_footer(text=f"Request: {prompt}")

    await ctx.send(embed=embed)




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
        affiliates[str(user_id)] = {"affiliate": 0, "balance": 0, "daily-points": 0.03, "last-claimed": datetime.now().isoformat()}
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
    await ctx.respond(embed=embed)


async def affiliate_error_false(ctx):
    embed = discord.Embed(
        title="❌ Not an Affiliate",
        description="You are not an Affiliate. If you wish to apply for Affiliate, you can do it ~~here~~ [Applications closed]",
        color=discord.Color.red()
    )
    await ctx.respond(embed=embed)


async def affiliate_error_low_balance(ctx):
    embed = discord.Embed(
        title="❌ Error",
        description="Your balance is too low to withdraw. The withdraw threshold is 1.50$.",
        color=discord.Color.red()
    )
    await ctx.respond(embed=embed)


async def affiliate_withdraw_message(ctx):
    embed = discord.Embed(
        title="💸 Withdraw Balance",
        description=(
            "Thank you for being a F0X Mods Affiliate.\n"
            "Your request has been received and a Staff Member will shortly address your request."
        ),
        color=discord.Color.yellow()
    )
    await ctx.respond(embed=embed, ephemeral=True)


async def update_all_affiliates():
    affiliates = await load_affiliates()
    current_time = datetime.now().isoformat()

    for user_id in affiliates:
        claimed_last_date = datetime.fromisoformat(affiliates[user_id]['last-claimed'])
        if datetime.now() - claimed_last_date < timedelta(days=1):
            return
        affiliates[user_id]['balance'] += affiliates[user_id]['daily-points']
        affiliates[user_id]['last-claimed'] = current_time
    await save_affiliates(affiliates)



@bot.slash_command(
  name="affiliate-status",
  description="Check your Affiliate Status",
  guild_ids=guild_ids
)
async def affiliate_status(ctx):
    affiliates = await load_affiliates()
    await check_affiliates(ctx.author.id, affiliates)

    if affiliates[str(ctx.author.id)]['affiliate'] == 0:
        await affiliate_error_false(ctx)
        return

    embed = discord.Embed(
            title="ℹ️ Affiliate Status",
            description="You are an **Affiliate**.",
            color=discord.Color.blue()
        )
    await ctx.respond(embed=embed)


@bot.slash_command(
  name="affiliate-balance",
  description="Check your Affiliate balance",
  guild_ids=guild_ids
)
async def affiliate_balance(ctx):
    affiliates = await load_affiliates()
    await check_affiliates(ctx.author.id, affiliates)

    if affiliates[str(ctx.author.id)]['affiliate'] == 0:
        await affiliate_error_false(ctx)
        return

    embed = discord.Embed(
            title="💰 Affiliate Balance",
            description=f"Nice to see you, Affiliate {ctx.author.mention}!",
            color=discord.Color.green()
        )
    embed.add_field(
            name="Your Balance",
            value=f"{affiliates[str(ctx.author.id)]['balance']:.2f}$"
        )
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(
  name="affiliate-withdraw",
  description="Withdraw your Affiliate balance",
  guild_ids=guild_ids
)
async def affiliate_withdraw(ctx):
    affiliates = await load_affiliates()
    await check_affiliates(ctx.author.id, affiliates)

    if affiliates[str(ctx.author.id)]['affiliate'] == 0:
        await affiliate_error_false(ctx)
        return

    if affiliates[str(ctx.author.id)]['balance'] < 1.5:
        await affiliate_error_low_balance(ctx)
    else:
        await affiliate_withdraw_message(ctx)
        embed = discord.Embed(
                title="📋 Withdraw Details",
                description=(
                    f"### Affiliate: {ctx.author.mention}\n"
                    f"### Withdrawn Balance: {affiliates[str(ctx.author.id)]['balance']:.2f}$"
                ),
                color=discord.Color.yellow()
            )
        await ctx.respond(embed=embed, ephemeral=True)
        channel = bot.get_channel(affiliate_reports_channel)
        if channel:
            embed = discord.Embed(
                    title="💸 Withdraw Request",
                    description=(
                        f"### Affiliate: {ctx.author.mention}\n"
                        f"### Withdrawn Balance: {affiliates[str(ctx.author.id)]['balance']:.2f}$"
                    ),
                    color=discord.Color.green()
                )
            await channel.send(embed=embed)





@bot.slash_command(
  name="affiliate-quests",
  description="See all the Affiliate Quests to earn more.",
  guild_ids=guild_ids
)
async def affiliate_quests(ctx):
    
    affiliates = await load_affiliates()
    await check_affiliates(ctx.author.id, affiliates)

    embed = discord.Embed(
                title="",
                description=(
                    f"## Affiliate Quests\nAffiliate Quests are optional requirements that Affiliates can complete, based on the agreement and their job/occupation to earn more from their Affiliate Status. Affiliate Quests are divided into sections based on what the Affiliate activity is. For example, an Affiliate who runs Minecraft related activities would want to go to the section `MINECRAFT`."
                ),
                color=discord.Color.yellow()
            )

    if affiliates[str(ctx.author.id)]['affiliate'] == 1:

        embed.add_field(name="☑️ Quest List", value=" **Quests Sections** \nHere is the list of sections with the relative quests. Navigate to your home section and once you complete your quest milestone, open a ticket to claim your reward balance. \n\n **➡️MINECRAFT**\n**Minecraft Addons**\n> Quest: Have a minimum of 10.000 downloads on a single project hosted on a website such as CurseForge, Modrinth.\n**Minecraft Servers**\n> Quest: Have over 500 players online at the same time.\n **➡️DISCORD**\n**Discord Servers**\n> Quest: Have over 800 members in your Discord server at the same time. Bots, Webhooks, Automations or Botted Accounts don't count.\n **➡️CONTENT CREATORS**\n**YouTube**\n> Quest: Reach 10.000 subscribers.\n**Twitch**\n> Quest: Reach 800 followers.\n**Other**\n> Quest: Reach 1.000.000 views on a single video within the first 30 days.\n **➡️OTHER ACTIVITIES**\n**Websites**\n> Quest: Reach 10.000 visitors during a period of 30 days.\n**More/Other**\n> Please open a ticket to discuss the appropriate Quest.", inline=False)


    else:
        embed.add_field(name="❌ Not an Affiliate", value="You are not an Affiliate. If you wish to see the Affiliate Quests list, apply for Affiliate.", inline=False)

    await ctx.respond(embed=embed)


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


@bot.slash_command(
  name="ticket-open",
  description="Open a ticket",
  guild_ids=guild_ids
)
async def ticket_open(ctx):
    view = MyView()
    embed = discord.Embed(
                title="Tickets",
                description=(
                    f"Click the button to open a Ticket."
                ),
                color=discord.Color.blue()
            )
    await ctx.respond(embed=embed, view=view)

@bot.slash_command(
  name="ticket-close",
  description="Close a ticket",
  guild_ids=guild_ids
)
async def ticket_close(ctx):
    await close_ticket(ctx)

@bot.slash_command(
  name="ticket-claim",
  description="Claim a ticket",
  guild_ids=guild_ids
)
async def ticket_claim(ctx):
    await claim_ticket(ctx)



async def open_ticket(interaction):
    guild = interaction.guild
    author = interaction.user
    if str(author.id) in ticket_channels:
        await interaction.respond("You already have an open ticket. Please have only one ticket at a time. You can close the other ticket anytime with `!ticket close`", ephemeral=True)
        return
    category = discord.utils.get(guild.categories, name="Tickets")
    if category is None:
        category = await guild.create_category("Tickets")

    ticket_channel = await guild.create_text_channel(
        f"ticket-{author.name}",
        category=category,
        overwrites={
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            author: discord.PermissionOverwrite(read_messages=True),
            guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(read_messages=True)
        }
    )

    ticket_channels[str(author.id)] = ticket_channel.id
    save_tickets()
    embed = discord.Embed(
                title="Ticket Created",
                description=(
                    f"{author.mention} Your ticket has been created. A staff member will be with you shortly."
                ),
                color=discord.Color.blue()
            )
    await ticket_channel.send(embed=embed)
    await interaction.respond(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

async def claim_ticket(ctx):
    if ctx.author.id not in STAFF_ID:
        await ctx.respond("You do not have permission to use this command.")
        return

    if ctx.channel.id not in ticket_channels.values():
        await ctx.respond("This is not a ticket channel.")
        return

    await ctx.respond(f"Ticket claimed by {ctx.author.mention}")
    ticket_creator_id = next((k for k, v in ticket_channels.items() if v == ctx.channel.id), None)
    if ticket_creator_id:
        ticket_creator = discord.utils.get(ctx.guild.members, id=int(ticket_creator_id))
        if ticket_creator:
            await ctx.channel.respond(f"{ticket_creator.mention} Your ticket has been claimed by {ctx.author.mention}")

async def close_ticket(ctx):
    if ctx.channel.id not in ticket_channels.values():
        await ctx.respond("This is not a ticket channel.")
        return

    await ctx.channel.delete()
    ticket_creator_id = next((k for k, v in ticket_channels.items() if v == ctx.channel.id), None)
    if ticket_creator_id:
        del ticket_channels[ticket_creator_id]
        save_tickets()





# DATABASE


@bot.slash_command(
  name="login",
  description="Login to your F0XMods account",
  guild_ids=guild_ids
)
async def login(ctx):
    embed = discord.Embed(
                title="➡️ **LOGIN**",
                description=(
                    f"### Log into your F0XMods Account here:\n> [f0xmods.com/login](<https://f0xmods.com/login-system/frontend/login.html)"
                ),
                color=discord.Color.blue()
            )
    await ctx.respond(embed=embed)


@bot.slash_command(
  name="register",
  description="Create your F0XMods account",
  guild_ids=guild_ids
)
async def register(ctx):
    embed = discord.Embed(
                title="➡️ **REGISTER**",
                description=(
                    f"### Create your F0XMods Account here:\n> [f0xmods.com/register](<https://f0xmods.com/login-system/frontend/register.html)"
                ),
                color=discord.Color.blue()
            )
    await ctx.respond(embed=embed)





# MUSIC
import yt_dlp

song_playlist = []


@bot.slash_command(
  name="play",
  description="Play a song",
  guild_ids=guild_ids
)
async def play(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        embed = discord.Embed(
            title=":x: Error",
            description=f"You need to be in a voice channel to use this command!",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)
        return

    if not song_playlist:
        embed = discord.Embed(
            title=":x: Error",
            description=f"The playlist is empty. Add songs with !song",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)
        return

    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client

    try:
        ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_playlist[0]}", download=False)
            url = info['entries'][0]['url']
            song_title = info['entries'][0]['title']

        vc.play(discord.FFmpegPCMAudio(url), after=lambda e: print('done', e))
        embed = discord.Embed(
            title="▶️ Playing song",
            description=f"{song_title}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        song_playlist.pop(0)

    except Exception as e:
        embed = discord.Embed(
            title=":x: Error",
            description=f"Error playing the song: {e}",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)

@bot.slash_command(
  name="stop",
  description="Stop the current song",
  guild_ids=guild_ids
)
async def stop(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        embed = discord.Embed(
            title=":pause_button: Music Stopped",
            description=f"Stopped the music and disconnected from the voice channel.",
            color=discord.Color.blue()
        )
        await ctx.respond(embed=embed)
     
    else:
        embed = discord.Embed(
            title=":x: Error",
            description=f"I'm not currently in a voice channel.",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)


@bot.slash_command(
  name="song",
  description="Add a song to the playlist",
  guild_ids=guild_ids
)
async def song(ctx, *, title: str):
    if title is None:
        embed = discord.Embed(
            title=":x: Error",
            description=f"You must specify a song to play.",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)
        return

    song_playlist.append(f"{title}")
    embed = discord.Embed(
            title="🎶 Song added",
            description=f"The requested song was added to the playlist",
            color=discord.Color.green()
        )
    await ctx.respond(embed=embed)


@bot.slash_command(
  name="playlist",
  description="Send the song playlist",
  guild_ids=guild_ids
)
async def playlist(ctx, placement: int = None):
    if placement is None:
        if not song_playlist:
            embed = discord.Embed(
                title="📋 Playlist",
                description="The playlist is empty.",
                color=discord.Color.yellow()
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="📋 Playlist",
                description="\n".join(song_playlist),
                color=discord.Color.yellow()
            )
            await ctx.respond(embed=embed)
    else:
        real_placement = placement -1
        if placement <= 0:
            await ctx.respond("The playlist placement has to be at least 1.")
            return
        if real_placement > len(song_playlist):
            embed = discord.Embed(
                title="❌ Error",
                description="The playlist has fewer songs than the number you provided.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
            return

        embed = discord.Embed(
            title=f"📋 Playlist Song {placement}",
            description=f"The song number {placement} in the playlist is **{song_playlist[real_placement]}**",
            color=discord.Color.yellow()
        )
        await ctx.respond(embed=embed)





# PROTOCOL
from datetime import datetime, timedelta

owner_role_id = 1130229890650734643

messages_file_path = 'messages.json'


# Ensure the messages file exists or create it
def ensure_messages_file():
    if not os.path.exists(messages_file_path):
        with open(messages_file_path, 'w') as file:
            json.dump({}, file)

# Load the messages JSON file
def load_messages_file():
    with open(messages_file_path, 'r') as file:
        return json.load(file)

# Save to the messages JSON file
def save_messages_file(data):
    with open(messages_file_path, 'w') as file:
        json.dump(data, file, indent=4)


@bot.event
async def on_message(message):
    if message.author.id == developer_id:
        ensure_messages_file()
        data = load_messages_file()
        data[str(developer_id)] = {
            "last_message": message.content,
            "date": datetime.now().isoformat()
        }
        save_messages_file(data)
    await bot.process_commands(message)

@bot.slash_command(
  name='protocol',
  description="Activate the protocol",
  guild_ids=guild_ids
)
async def protocol(ctx):
    if ctx.author.id not in STAFF_ID:
        await ctx.respond("No access.")
        return
    ensure_messages_file()
    data = load_messages_file()
    if str(developer_id) in data:
        last_message_date = datetime.fromisoformat(data[str(developer_id)]["date"])
        if datetime.now() - last_message_date > timedelta(days=90):  # Check if more than 90 days have passed
            member = ctx.author
            owner_role = ctx.guild.get_role(owner_role_id)
            if owner_role:
                await member.add_roles(owner_role)
                await ctx.send(f'{member.mention} has been given the Owner role.')
            else:
                await ctx.send('Could not find the Owner role.')
        else:
            await ctx.send('The developer has been active within the last 90 days.')
    else:
        await ctx.send('No data found for the developer.')

@protocol.error
async def protocol_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permission to use this command.')




# PARTNERSHIPS

partnership_channel_id = 1267426335689801738

@bot.slash_command(
  name="partnership",
  description="Request a Partnership with Fox Mods",
  guild_ids=guild_ids
)
async def partnership(ctx, what_you_want_to_promote: str, how_the_partnership_should_work: str, why_are_you_requesting_this: str):

    embed = discord.Embed(
                title="🤝 Partnership",
                description="Thank you for requesting a Partnership with Fox Mods. A Staff Member will check this as soon as possible.",
                color=discord.Color.green()
            )
    await ctx.respond(embed=embed, ephemeral=True)

    embed = discord.Embed(
                title="🤝 Partnership Request",
                description=f"{ctx.author.mention} requested a Partnership!",
                color=discord.Color.green()
            )
    embed.add_field(name="Activity", value=what_you_want_to_promote, inline=False)

    embed.add_field(name="Mechanic", value=how_the_partnership_should_work, inline=False)

    embed.add_field(name="Motive", value=why_are_you_requesting_this, inline=False)
    
    partnership_channel = bot.get_channel(partnership_channel_id)

    await partnership_channel.send(embed=embed)




# TESTING (FEATURES STILL IN BETA)

@bot.user_command(name="Say Hello")
async def hi(ctx, user):
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!", ephemeral=True)





# COMMANDS ERRORS AND COOLDOWNS


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="❌ Cooldown",
            description=f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("There was an error. Make sure you're using application/slash commands.")





# RUN THE BOT

bot.run(TOKEN)