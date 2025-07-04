import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import random
import json
import os
import re
import io
import aiohttp
from discord import Embed, ButtonStyle, File
from discord.ui import View, Button
import sys
from discord import app_commands
import requests
from io import BytesIO


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')
player_data = {}

def save_data():
    with open("data.json", "w") as f:
        json.dump(player_data, f, indent=4)

def load_data():
    global player_data
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            player_data = json.load(f)
    else:
        player_data = {}

def generate_random_location():
    letters = 'ABCDEFGH'
    numbers = range(1, 9)
    return f"{random.choice(letters)}{random.choice(numbers)}"

@bot.event
async def on_ready():
    load_data()
    print(f'Bot is online as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

@bot.command()
async def start(ctx):
    user_id = str(ctx.author.id)

    if user_id in player_data:
        embed = discord.Embed(
            title="Welcome Back!",
            description=f"Your castle is level {player_data[user_id]['castle_level']}.",
            color=discord.Color.green()
        )
    else:
        player_data[user_id] = {
            "username": ctx.author.name,
            "castle_level": 1,
            "gold": 1000,
            "food": 1000,
            "troops": 0,
            "location": generate_random_location(),
            "tutorial_done": False,
            "gems": 100,
            "battles_won": 0,
            "battles_lost": 0
        }
        save_data()
        embed = discord.Embed(
            title="Welcome to Castle RPG!",
            description=(
                f"You've been placed at `{player_data[user_id]['location']}`.\n"
                f"Type `!tutorial` to begin your journey!"
            ),
            color=discord.Color.gold()
        )

    await ctx.send(embed=embed)

@bot.tree.command(name="start", description="Start your adventure or return to your kingdom.")
async def start_slash(interaction: discord.Interaction):
    ctx = await bot.get_context(interaction)
    await start(ctx)

@bot.command()
async def tutorial(ctx):
    user_id = str(ctx.author.id)

    if user_id not in player_data:
        await ctx.send(embed=discord.Embed(title="Start First", description="Type `!start` first.", color=discord.Color.red()))
        return

    if player_data[user_id].get("tutorial_done"):
        await ctx.send(embed=discord.Embed(title="Tutorial Already Done", description="You've already completed it!", color=discord.Color.green()))
        return

    await ctx.send(embed=discord.Embed(title="Tutorial Start", description="Let's begin!", color=discord.Color.blurple()))

    await ctx.send(embed=discord.Embed(title="Step 1", description="Type `!build castle`", color=discord.Color.blurple()))
    def check1(m): return m.author == ctx.author and m.content.lower() == '!build castle'
    try:
        await bot.wait_for('message', check=check1, timeout=60)
        await ctx.send(embed=discord.Embed(title="Castle Built!", description="Level 1 castle ready.", color=discord.Color.green()))
    except:
        await ctx.send(embed=discord.Embed(title="Timeout", description="Try `!tutorial` again.", color=discord.Color.red()))
        return

    await ctx.send(embed=discord.Embed(title="Step 2", description="Type `!collect`", color=discord.Color.blurple()))
    def check2(m): return m.author == ctx.author and m.content.lower() == '!collect'
    try:
        await bot.wait_for('message', check=check2, timeout=60)
        player_data[user_id]["gold"] += 500
        player_data[user_id]["food"] += 500
        save_data()
        await ctx.send(embed=discord.Embed(title="Resources Collected", description="+500 gold & food", color=discord.Color.green()))
    except:
        await ctx.send(embed=discord.Embed(title="Timeout", description="Try `!tutorial` again.", color=discord.Color.red()))
        return

    await ctx.send(embed=discord.Embed(title="Step 3", description="Type `!train`", color=discord.Color.blurple()))
    def check3(m): return m.author == ctx.author and m.content.lower() == '!train'
    try:
        await bot.wait_for('message', check=check3, timeout=60)
        player_data[user_id]["troops"] += 10
        player_data[user_id]["tutorial_done"] = True
        save_data()
        await ctx.send(embed=discord.Embed(title="Troops Ready!", description="10 troops trained.", color=discord.Color.green()))
    except:
        await ctx.send(embed=discord.Embed(title="Timeout", description="Try `!tutorial` again.", color=discord.Color.red()))
        return

    await ctx.send(embed=discord.Embed(title="Tutorial Complete", description="You're now ready!", color=discord.Color.purple()))

@bot.command()
async def build(ctx, building: str):
    user_id = str(ctx.author.id)

    if user_id not in player_data:
        await ctx.send(embed=discord.Embed(title="Start First", description="Type `!start` first.", color=discord.Color.red()))
        return

    if building.lower() == "castle":
        embed = discord.Embed(title="Castle Already Built", description="You already have it.", color=discord.Color.green())
    else:
        embed = discord.Embed(title="Building Not Available", description="Only `castle` is available for now.", color=discord.Color.orange())

    await ctx.send(embed=embed)

@bot.tree.command(name="build", description="Build a building (currently only 'castle').")
@app_commands.describe(building="The building to construct (currently only 'castle')")
async def build_slash(interaction: discord.Interaction, building: str):
    ctx = await bot.get_context(interaction)
    await build(ctx, building)

@bot.command()
async def collect(ctx):
    user_id = str(ctx.author.id)

    if user_id not in player_data:
        await ctx.send(embed=discord.Embed(title="Start First", description="Type `!start` first.", color=discord.Color.red()))
        return

    gold = random.randint(100, 200)
    food = random.randint(100, 200)
    player_data[user_id]["gold"] += gold
    player_data[user_id]["food"] += food
    save_data()

    embed = discord.Embed(title="Resources Collected", color=discord.Color.green())
    embed.add_field(name="Gold", value=str(gold), inline=True)
    embed.add_field(name="Food", value=str(food), inline=True)
    await ctx.send(embed=embed)

@bot.tree.command(name="collect", description="Collect resources (gold and food).")
async def collect_slash(interaction: discord.Interaction):
    ctx = await bot.get_context(interaction)
    await collect(ctx)

@bot.command()
async def train(ctx):
    user_id = str(ctx.author.id)

    if user_id not in player_data:
        await ctx.send(embed=discord.Embed(title="Start First", description="Type `!start` first.", color=discord.Color.red()))
        return

    cost_gold = 100
    cost_food = 100

    if player_data[user_id]["gold"] < cost_gold or player_data[user_id]["food"] < cost_food:
        await ctx.send(embed=discord.Embed(title="Not Enough Resources", description="Need 100 gold & 100 food.", color=discord.Color.red()))
        return

    player_data[user_id]["gold"] -= cost_gold
    player_data[user_id]["food"] -= cost_food
    player_data[user_id]["troops"] += 5
    save_data()

    await ctx.send(embed=discord.Embed(title="Troops Trained", description=f"Now have {player_data[user_id]['troops']} troops.", color=discord.Color.green()))

@bot.tree.command(name="train", description="Train troops for your kingdom.")
async def train_slash(interaction: discord.Interaction):
    ctx = await bot.get_context(interaction)
    await train(ctx)

@bot.command()
async def upgrade(ctx, building: str):
    user_id = str(ctx.author.id)

    if user_id not in player_data:
        await ctx.send(embed=discord.Embed(title="Start First", description="Type `!start` first.", color=discord.Color.red()))
        return

    if building.lower() == "castle":
        level = player_data[user_id]["castle_level"]
        gold_cost = 500 * level
        food_cost = 300 * level

        if player_data[user_id]["gold"] < gold_cost or player_data[user_id]["food"] < food_cost:
            await ctx.send(embed=discord.Embed(title="Not Enough Resources", description=f"Need {gold_cost} gold & {food_cost} food.", color=discord.Color.red()))
            return

        player_data[user_id]["gold"] -= gold_cost
        player_data[user_id]["food"] -= food_cost
        player_data[user_id]["castle_level"] += 1
        save_data()

        embed = discord.Embed(title="Castle Upgraded!", description=f"Now level {player_data[user_id]['castle_level']}.", color=discord.Color.green())
        embed.add_field(name="Gold Spent", value=str(gold_cost), inline=True)
        embed.add_field(name="Food Spent", value=str(food_cost), inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(title="Upgrade Not Available", description="Only `castle` can be upgraded now.", color=discord.Color.orange()))

@bot.tree.command(name="upgrade", description="Upgrade your castle.")
@app_commands.describe(building="The building to upgrade (currently only 'castle')")
async def upgrade_slash(interaction: discord.Interaction, building: str):
    ctx = await bot.get_context(interaction)
    await upgrade(ctx, building)

def location_to_xy(loc_str):
    match = re.match(r"([A-Z]+)(\d+)", loc_str.upper())
    if not match:
        return None
    col_letters, row_number = match.groups()

    # Convert column letters to number (e.g. "A" -> 0, "B" -> 1, ..., "AA" -> 26)
    x = 0
    for char in col_letters:
        x = x * 26 + (ord(char) - ord('A') + 1)
    x -= 1  # zero-indexed
    y = int(row_number) - 1  # zero-indexed

    return x, y

@bot.command(aliases=["info", "stats"])
async def profile(ctx):
    user_id = str(ctx.author.id)

    if user_id not in player_data:
        await ctx.send(embed=discord.Embed(title="Start First", description="Type `!start` first.", color=discord.Color.red()))
        return

    p = player_data[user_id]

    embed = discord.Embed(title=f"{ctx.author.name}'s Kingdom", color=discord.Color.purple())
    embed.add_field(name="Castle Level", value=str(p["castle_level"]), inline=True)
    embed.add_field(name="Troops", value=str(p["troops"]), inline=True)
    embed.add_field(name="Location", value=p["location"], inline=True)
    embed.add_field(name="Gold", value=str(p["gold"]), inline=True)
    embed.add_field(name="Food", value=str(p["food"]), inline=True)
    embed.add_field(name="Gems", value=str(p["gems"]), inline=True)
    embed.add_field(name="Battles Won", value=str(p["battles_won"]), inline=True)
    embed.add_field(name="Battles Lost", value=str(p["battles_lost"]), inline=True)
    embed.set_footer(text="Castle RPG Bot")

    await ctx.send(embed=embed)

@bot.tree.command(name="profile", description="View your kingdom's stats.")
async def profile_slash(interaction: discord.Interaction):
    ctx = await bot.get_context(interaction)
    await profile(ctx)

@bot.command()
async def world(ctx):
    map_image_path = os.path.join(os.path.dirname(__file__), "world_map_with_coords.png")
    with open("data.json", "r") as f:
        players = json.load(f)

    base_map = Image.open(map_image_path).convert("RGBA")
    draw = ImageDraw.Draw(base_map)

    cell_size = 45
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()

    for player_id, pdata in players.items():
        loc = pdata.get("location")
        if not loc:
            continue

        coords = location_to_xy(loc)
        if not coords:
            continue

        x, y = coords
        px = x * cell_size + cell_size // 4
        py = y * cell_size + cell_size // 4
        username = pdata.get("username", "Player")

        # Draw castle icon (circle for now)
        draw.ellipse([px, py, px + 18, py + 18], fill="blue", outline="white", width=2)
        draw.text((px + 20, py), username[:6], fill="black", font=font)

    buffer = io.BytesIO()
    base_map.save(buffer, format="PNG")
    buffer.seek(0)

    file = discord.File(fp=buffer, filename="current_world.png")
    embed = discord.Embed(
        title="You are currently viewing your kingdom",
        description="This is a kingdom with all the players around you",
        color=discord.Color.blue()
    )
    embed.set_image(url="attachment://current_world.png")
    await ctx.send(embed=embed, file=file)

@bot.command()
async def createguild(ctx):
    import aiohttp
    user_id = str(ctx.author.id)

    # Check if user is in any guild (as leader or member)
    if not os.path.exists("guilds.json"):
        with open("guilds.json", "w") as f:
            json.dump({}, f)
    with open("guilds.json", "r") as f:
        guilds = json.load(f)
    for gname, ginfo in guilds.items():
        if user_id in ginfo.get("members", {}):
            await ctx.send("❌ You are already in a guild. Please disband or leave your current guild before creating a new one.")
            return

    # 1. Ask for image
    await ctx.send("Please upload an image for your guild (or type 'skip' to skip):")
    def image_check(m):
        return m.author == ctx.author and (m.attachments or m.content.lower() == 'skip')
    try:
        image_msg = await bot.wait_for('message', check=image_check, timeout=60)
    except:
        await ctx.send("⏰ Timed out. Please try again.")
        return
    image_path = None
    if image_msg.attachments:
        img_url = image_msg.attachments[0].url
        ext = os.path.splitext(img_url)[-1]
        if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'  # fallback
        if not os.path.exists('guild_images'):
            os.makedirs('guild_images')
        filename = f"guild_{user_id}{ext}"
        image_path = os.path.join("guild_images", filename)
        async with aiohttp.ClientSession() as session:
            async with session.get(img_url) as resp:
                if resp.status == 200:
                    img_bytes = await resp.read()
                    with open(image_path, 'wb') as f:
                        f.write(img_bytes)
    # 2. Ask for title
    await ctx.send("What should be the name of your guild?")
    def title_check(m): return m.author == ctx.author
    try:
        title_msg = await bot.wait_for('message', check=title_check, timeout=60)
    except:
        await ctx.send("⏰ Timed out. Please try again.")
        return
    name = title_msg.content.strip()

    # 3. Ask for description
    await ctx.send("Please provide a description for your guild:")
    try:
        desc_msg = await bot.wait_for('message', check=title_check, timeout=60)
    except:
        await ctx.send("⏰ Timed out. Please try again.")
        return
    description = desc_msg.content.strip()

    # 4. Ask if user wants to set requirements (with buttons)
    from discord.ui import Button, View
    class ReqView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.value = None
        @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
        async def yes(self, interaction: discord.Interaction, button: Button):
            self.value = True
            self.stop()
        @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
        async def no(self, interaction: discord.Interaction, button: Button):
            self.value = False
            self.stop()
    view = ReqView()
    req_msg = await ctx.send("Do you want to set minimum requirements for joining?", view=view)
    await view.wait()
    await req_msg.edit(view=None)

    if view.value:
        # 5. Ask for requirements
        await ctx.send("Enter minimum castle level:")
        try:
            castle_msg = await bot.wait_for('message', check=title_check, timeout=60)
            min_castle_level = int(castle_msg.content.strip())
        except:
            await ctx.send("⏰ Timed out or invalid input. Please try again.")
            return
        await ctx.send("Enter minimum battles won:")
        try:
            battles_msg = await bot.wait_for('message', check=title_check, timeout=60)
            min_battles_won = int(battles_msg.content.strip())
        except:
            await ctx.send("⏰ Timed out or invalid input. Please try again.")
            return
    else:
        min_castle_level = 1
        min_battles_won = 0

    if name in guilds:
        await ctx.send("⚠️ This guild name already exists.")
        return
    guilds[name] = {
        "leader": user_id,
        "leader_name": ctx.author.display_name,
        "requirements": {
            "castle_level": min_castle_level,
            "battles_won": min_battles_won
        },
        "members": {user_id: "Leader"},
        "pending_requests": [],
        "description": description,
        "image_path": image_path
    }
    with open("guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)
    embed = discord.Embed(title=f"Guild Created: {name}", description=description, color=discord.Color.green())
    if image_path:
        file = discord.File(image_path, filename=os.path.basename(image_path))
        embed.set_thumbnail(url=f"attachment://{os.path.basename(image_path)}")
        await ctx.send(f"✅ Guild **{name}** created successfully!", embed=embed, file=file)
    else:
        await ctx.send(f"✅ Guild **{name}** created successfully!", embed=embed)

@bot.command()
async def disbandguild(ctx):
    user_id = str(ctx.author.id)
    if not os.path.exists("guilds.json"):
        await ctx.send("No guilds exist.")
        return
    with open("guilds.json", "r") as f:
        guilds = json.load(f)
    found = None
    for gname, ginfo in guilds.items():
        if ginfo.get("leader") == user_id:
            found = gname
            break
    if not found:
        await ctx.send("❌ You are not the leader of any guild.")
        return
    del guilds[found]
    with open("guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)
    await ctx.send(f"🗑️ Guild **{found}** has been disbanded.")

@bot.command()
async def joinguild(ctx, name: str):
    user_id = str(ctx.author.id)

    with open("guilds.json", "r") as f:
        guilds = json.load(f)

    with open("data.json", "r") as f:
        players = json.load(f)

    if name not in guilds:
        await ctx.send("❌ No such guild.")
        return

    if user_id in guilds[name]["members"]:
        await ctx.send("⚠️ You're already in this guild.")
        return

    # Requirements check
    player = players[user_id]
    reqs = guilds[name]["requirements"]

    if player["castle_level"] < reqs["castle_level"] or player["battles_won"] < reqs["battles_won"]:
        await ctx.send("❌ You don't meet this guild's requirements.")
        return

    if user_id in guilds[name]["pending_requests"]:
        await ctx.send("⏳ Your join request is already pending.")
        return

    guilds[name]["pending_requests"].append(user_id)

    with open("guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)

    await ctx.send(f"📬 Join request sent to **{name}**.")
@bot.command()
async def accept(ctx, guild_name: str, member_id: str):
    user_id = str(ctx.author.id)

    with open("guilds.json", "r") as f:
        guilds = json.load(f)

    if guild_name not in guilds:
        await ctx.send("Guild not found.")
        return

    guild = guilds[guild_name]
    role = guild["members"].get(user_id)

    if role not in ["Leader", "R4"]:
        await ctx.send("❌ Only Leader or R4 can accept members.")
        return

    if member_id not in guild["pending_requests"]:
        await ctx.send("That user did not request to join.")
        return

    guild["members"][member_id] = "R1"
    guild["pending_requests"].remove(member_id)

    with open("guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)

    await ctx.send(f"✅ Accepted <@{member_id}> into **{guild_name}**.")
@bot.command()
async def setrank(ctx, guild_name: str, member_id: str, rank: str):
    user_id = str(ctx.author.id)
    valid_ranks = ["R1", "R2", "R3", "R4"]

    with open("guilds.json", "r") as f:
        guilds = json.load(f)

    if guild_name not in guilds:
        await ctx.send("Guild not found.")
        return

    guild = guilds[guild_name]
    role = guild["members"].get(user_id)

    if role != "Leader":
        await ctx.send("Only the Leader can set ranks.")
        return

    if rank not in valid_ranks:
        await ctx.send("Invalid rank.")
        return

    if member_id not in guild["members"]:
        await ctx.send("User not in guild.")
        return

    guild["members"][member_id] = rank

    with open("guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)

    await ctx.send(f"🎖️ Updated <@{member_id}> to rank **{rank}**.")
@bot.command()
async def guildlist(ctx):
    import json
    from discord import Embed
    import os

    with open("guilds.json", "r") as f:
        guilds = json.load(f)

    if not guilds:
        await ctx.send("No guilds have been created yet.")
        return

    for guild_name, info in guilds.items():
        leader = info.get("leader_name", "Unknown")
        member_count = len(info.get("members", {}))
        req = info.get("requirements", {})
        castle_req = req.get("castle_level", 1)
        battle_req = req.get("battles_won", 0)
        description = info.get("description", "No description provided.")
        image_path = info.get("image_path")

        desc = (
            f"👑 **Leader**: {leader}\n"
            f"👥 **Members**: {member_count}\n"
            f"{description}"
        )
        # Only show requirements if set by leader (not default values)
        if castle_req > 1 or battle_req > 0:
            desc += (f"\n🔒 **Requirements**:\n")
            if castle_req > 1:
                desc += f"• Castle Level ≥ {castle_req}\n"
            if battle_req > 0:
                desc += f"• Battles Won ≥ {battle_req}"
        embed = Embed(title=guild_name, description=desc, color=0x00ffcc)
        if image_path and os.path.exists(image_path):
            file = discord.File(image_path, filename=os.path.basename(image_path))
            embed.set_thumbnail(url=f"attachment://{os.path.basename(image_path)}")
            # Set image as thumbnail (left of embed text)
            await ctx.send(embed=embed, file=file)
        else:
            await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    from discord.ui import View, Button
    embed = discord.Embed(title="Castle RPG Bot Help", description="Select a category below to view commands.", color=discord.Color.blurple())
    embed.set_footer(text="Castle RPG Bot - All commands start with !")

    view = View()

    # Main category buttons
    guild_btn = Button(label="Guild Commands", style=ButtonStyle.primary, custom_id="help_guild")
    guild_admin_btn = Button(label="Guild Admin Commands", style=ButtonStyle.danger, custom_id="help_guild_admin")
    general_btn = Button(label="General Commands", style=ButtonStyle.secondary, custom_id="help_general")

    async def guild_callback(interaction):
        guild_embed = discord.Embed(title="Guild Commands", color=discord.Color.blue())
        guild_embed.add_field(name="!createguild", value="Create a new guild (one per player).", inline=False)
        guild_embed.add_field(name="!joinguild <guild>", value="Request to join a guild.", inline=False)
        guild_embed.add_field(name="!guildlist", value="List all guilds and their info.", inline=False)
        guild_embed.add_field(name="!leaveguild", value="Leave your current guild (if not leader).", inline=False)
        guild_embed.add_field(name="!guildinfo <guild>", value="View info about a specific guild.", inline=False)
        guild_embed.add_field(name="!pendingrequests <guild>", value="View pending join requests (Leader/R4 only).", inline=False)
        await interaction.response.send_message(embed=guild_embed, ephemeral=True)

    async def guild_admin_callback(interaction):
        admin_embed = discord.Embed(title="Guild Admin Commands", color=discord.Color.red())
        admin_embed.add_field(name="!disbandguild", value="Disband your guild (leader only).", inline=False)
        admin_embed.add_field(name="!accept <guild> <member_id>", value="Accept a join request (leader or R4 only).", inline=False)
        admin_embed.add_field(name="!setrank <guild> <member_id> <rank>", value="Set a member's rank (leader only). Ranks: R1, R2, R3, R4.", inline=False)
        admin_embed.add_field(name="!kickmember <user>", value="Kick a member from your guild (Leader/R4 only).", inline=False)
        admin_embed.add_field(name="!demote <@user>", value="Demote a member to a lower rank (Leader only).", inline=False)
        await interaction.response.send_message(embed=admin_embed, ephemeral=True)

    async def general_callback(interaction):
        general_embed = discord.Embed(title="General Commands", color=discord.Color.green())
        general_embed.add_field(name="!start", value="Start your adventure or return to your kingdom.", inline=False)
        general_embed.add_field(name="!tutorial", value="Begin the tutorial for new players.", inline=False)
        general_embed.add_field(name="!build <building>", value="Build a building (currently only 'castle').", inline=False)
        general_embed.add_field(name="!collect", value="Collect resources (gold and food).", inline=False)
        general_embed.add_field(name="!train", value="Train troops for your kingdom.", inline=False)
        general_embed.add_field(name="!upgrade <building>", value="Upgrade your castle.", inline=False)
        general_embed.add_field(name="!profile / !info / !stats", value="View your kingdom's stats.", inline=False)
        general_embed.add_field(name="!world", value="View the world map with all players.", inline=False)
        general_embed.add_field(name="!help", value="Show this help message.", inline=False)
        await interaction.response.send_message(embed=general_embed, ephemeral=True)

    guild_btn.callback = guild_callback
    guild_admin_btn.callback = guild_admin_callback
    general_btn.callback = general_callback

    view.add_item(guild_btn)
    view.add_item(guild_admin_btn)
    view.add_item(general_btn)

    await ctx.send(embed=embed, view=view)

@bot.command()
async def leaveguild(ctx):
    user_id = str(ctx.author.id)
    if not os.path.exists("guilds.json"):
        await ctx.send(embed=discord.Embed(title="No Guilds Exist", description="There are no guilds to leave.", color=discord.Color.red()))
        return
    with open("guilds.json", "r") as f:
        guilds = json.load(f)
    found = None
    for gname, ginfo in guilds.items():
        if user_id in ginfo.get("members", {}) and ginfo.get("leader") != user_id:
            found = gname
            break
    if not found:
        await ctx.send(embed=discord.Embed(title="Not a Guild Member", description="You are not a member of any guild or you are the leader. Leaders must use !disbandguild.", color=discord.Color.orange()))
        return
    del guilds[found]["members"][user_id]
    with open("guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)
    # Also update data.json to clear guild info for this user
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            data = json.load(f)
        if user_id in data:
            data[user_id]["guild"] = None
            data[user_id]["guild_rank"] = None
            with open("data.json", "w") as f:
                json.dump(data, f, indent=4)
    embed = discord.Embed(title="Left Guild", description=f"{ctx.author.mention} has left **{found}**.", color=discord.Color.blurple())
    await ctx.send(embed=embed)
@bot.command()
async def guildinfo(ctx, *, guild_name: str):
    user_id = str(ctx.author.id)

    # Read from guilds.json instead of data.json
    if not os.path.exists("guilds.json"):
        await ctx.send("❌ No guilds exist.")
        return
    with open("guilds.json", "r") as f:
        guilds = json.load(f)
    
    # Case-insensitive search for guild name
    found_guild = None
    for gname in guilds:
        if gname.lower() == guild_name.lower():
            found_guild = gname
            break
    if not found_guild:
        await ctx.send("❌ Guild not found.")
        return
    guild = guilds[found_guild]

    embed = Embed(
        title=f"🏰 {found_guild}",
        description=guild.get("description", "No description provided."),
        color=discord.Color.gold()
    )

    image_path = guild.get("image_path")
    file = None
    if image_path and os.path.exists(image_path):
        file = discord.File(image_path, filename=os.path.basename(image_path))
        embed.set_image(url=f"attachment://{os.path.basename(image_path)}")

    leader_id = guild.get("leader")
    embed.add_field(name="👑 Leader", value=f"<@{leader_id}>", inline=True)
    members_dict = guild.get("members", {})
    embed.add_field(name="👥 Members", value=str(len(members_dict)), inline=True)
    
    reqs = guild.get("requirements", {})
    req_text = (
        f"🏗️ Castle Level: {reqs.get('castle_level', 'N/A')}\n"
        f"🏆 Battles Won: {reqs.get('battles_won', 'N/A')}"
    )
    embed.add_field(name="🔒 Requirements", value=req_text, inline=False)

    # Get the user's rank in the guild
    player_rank = guild.get("members", {}).get(user_id, "R1")

    # --- Move GuildAdminView class definition here ---
    class GuildAdminView(discord.ui.View):
        def __init__(self, is_leader, guild, guild_name, image_path, ctx, file=None):
            super().__init__(timeout=60)
            self.guild = guild
            self.guild_name = guild_name
            self.image_path = image_path
            self.is_leader = is_leader
            self.ctx = ctx
            self.file = file

        @discord.ui.button(label="View Join Requests", style=discord.ButtonStyle.primary, custom_id="view_requests")
        async def view_requests_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            pending = self.guild.get("pending_requests", [])
            if not pending:
                await interaction.response.send_message("No pending join requests.", ephemeral=True)
                return
            msg = "\n".join([f"<@{uid}>" for uid in pending])
            embed = discord.Embed(title=f"Pending Join Requests for {self.guild_name}", description=msg, color=discord.Color.orange())
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @discord.ui.button(label="Promote/Demote", style=discord.ButtonStyle.secondary, custom_id="rank_manage")
        async def rank_manage_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            members = self.guild.get("members", {})
            member_list = [uid for uid in members if members[uid] != "Leader"]
            if not member_list:
                await interaction.response.send_message("No members to promote/demote.", ephemeral=True)
                return
            options = [discord.SelectOption(label=f"<@{uid}> ({members[uid]})", value=uid) for uid in member_list]
            class PromoteDemoteView(discord.ui.View):
                @discord.ui.select(placeholder="Select a member", options=options)
                async def select_member(self, select_interaction: discord.Interaction, select: discord.ui.Select):
                    uid = select.values[0]
                    current_rank = members[uid]
                    rank_order = ["R4", "R3", "R2", "R1"]
                    if current_rank not in rank_order:
                        await select_interaction.response.send_message("Cannot promote/demote this member.", ephemeral=True)
                        return
                    current_index = rank_order.index(current_rank)
                    promote = current_index > 0
                    demote = current_index < len(rank_order) - 1
                    view = discord.ui.View()
                    if promote:
                        @discord.ui.button(label="Promote", style=discord.ButtonStyle.success)
                        async def promote_btn(promote_interaction, button):
                            new_rank = rank_order[current_index - 1]
                            members[uid] = new_rank
                            with open("guilds.json", "r") as f:
                                guilds = json.load(f)
                            guilds[self.guild_name]["members"][uid] = new_rank
                            with open("guilds.json", "w") as f:
                                json.dump(guilds, f, indent=4)
                            await promote_interaction.response.send_message(f"<@{uid}> promoted to {new_rank}.", ephemeral=True)
                        view.add_item(promote_btn)
                    if demote:
                        @discord.ui.button(label="Demote", style=discord.ButtonStyle.danger)
                        async def demote_btn(demote_interaction, button):
                            new_rank = rank_order[current_index + 1]
                            members[uid] = new_rank
                            with open("guilds.json", "r") as f:
                                guilds = json.load(f)
                            guilds[self.guild_name]["members"][uid] = new_rank
                            with open("guilds.json", "w") as f:
                                json.dump(guilds, f, indent=4)
                            await demote_interaction.response.send_message(f"<@{uid}> demoted to {new_rank}.", ephemeral=True)
                        view.add_item(demote_btn)
                    await select_interaction.response.send_message(f"Selected <@{uid}> ({current_rank})", view=view, ephemeral=True)
            await interaction.response.send_message("Select a member to promote/demote:", view=PromoteDemoteView(), ephemeral=True)

        @discord.ui.button(label="Kick Member", style=discord.ButtonStyle.danger, custom_id="kick_member")
        async def kick_member_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            members = self.guild.get("members", {})
            member_list = [uid for uid in members if members[uid] != "Leader"]
            if not member_list:
                await interaction.response.send_message("No members to kick.", ephemeral=True)
                return
            options = [discord.SelectOption(label=f"<@{uid}> ({members[uid]})", value=uid) for uid in member_list]
            class KickView(discord.ui.View):
                @discord.ui.select(placeholder="Select a member to kick", options=options)
                async def select_kick(self, select_interaction: discord.Interaction, select: discord.ui.Select):
                    uid = select.values[0]
                    del members[uid]
                    with open("guilds.json", "r") as f:
                        guilds = json.load(f)
                    guilds[self.guild_name]["members"].pop(uid, None)
                    with open("guilds.json", "w") as f:
                        json.dump(guilds, f, indent=4)
                    await select_interaction.response.send_message(f"<@{uid}> has been kicked from the guild.", ephemeral=True)
            await interaction.response.send_message("Select a member to kick:", view=KickView(), ephemeral=True)

        @discord.ui.button(label="Disband Guild", style=discord.ButtonStyle.red, custom_id="disband_guild")
        async def disband_guild_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not self.is_leader:
                await interaction.response.send_message("Only the leader can disband the guild.", ephemeral=True)
                return
            with open("guilds.json", "r") as f:
                guilds = json.load(f)
            if self.guild_name in guilds:
                del guilds[self.guild_name]
                with open("guilds.json", "w") as f:
                    json.dump(guilds, f, indent=4)
                await interaction.response.send_message(f"Guild **{self.guild_name}** has been disbanded.", ephemeral=True)
            else:
                await interaction.response.send_message("Guild not found.", ephemeral=True)

    class GuildInfoView(discord.ui.View):
        def __init__(self, guild, found_guild, image_path, player_rank, ctx):
            super().__init__(timeout=60)
            self.guild = guild
            self.guild_name = found_guild
            self.image_path = image_path
            self.player_rank = player_rank
            self.ctx = ctx
            # Members button
            members_btn = discord.ui.Button(label="Members", style=discord.ButtonStyle.primary, row=0)
            async def members_btn_callback(interaction: discord.Interaction):
                members = self.guild.get("members", {})
                msg = '\n'.join([f"<@{uid}> — {rank}" for uid, rank in members.items()])
                embed = discord.Embed(title=f"Members of {self.guild_name}", description=msg, color=discord.Color.blurple())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            members_btn.callback = members_btn_callback
            self.add_item(members_btn)
            # My Rank button
            myrank_btn = discord.ui.Button(label="My Rank", style=discord.ButtonStyle.secondary, row=0)
            async def myrank_btn_callback(interaction: discord.Interaction):
                await interaction.response.send_message(f"Your rank in **{self.guild_name}**: **{self.player_rank}**", ephemeral=True)
            myrank_btn.callback = myrank_btn_callback
            self.add_item(myrank_btn)
            # Message Leader button
            msg_leader_btn = discord.ui.Button(label="Message Leader", style=discord.ButtonStyle.success, row=0)
            async def msg_leader_btn_callback(interaction: discord.Interaction):
                leader_id = self.guild.get("leader")
                if str(interaction.user.id) == leader_id:
                    await interaction.response.send_message("You are the leader!", ephemeral=True)
                    return
                await interaction.response.send_message("Please type your message to the leader. You have 60 seconds.", ephemeral=True)
                def check(m):
                    return m.author.id == interaction.user.id and m.channel == interaction.channel
                try:
                    msg = await bot.wait_for('message', check=check, timeout=60)
                except Exception:
                    await interaction.followup.send("Timed out. Please try again.", ephemeral=True)
                    return
                confirm_view = discord.ui.View()
                async def send_callback(confirm_interaction):
                    leader = interaction.guild.get_member(int(leader_id))
                    if leader:
                        await leader.send(f"Message from <@{interaction.user.id}> in guild **{self.guild_name}**:\n```{msg.content}```")
                        await confirm_interaction.response.send_message("Message sent to the leader!", ephemeral=True)
                    else:
                        await confirm_interaction.response.send_message("Could not DM the leader.", ephemeral=True)
                send_btn = discord.ui.Button(label="Send", style=discord.ButtonStyle.success)
                send_btn.callback = send_callback
                confirm_view.add_item(send_btn)
                await interaction.followup.send(f"Send this message to the leader?\n```{msg.content}```", view=confirm_view, ephemeral=True)
            msg_leader_btn.callback = msg_leader_btn_callback
            self.add_item(msg_leader_btn)
            # Manage Guild button (if Leader or R4)
            if self.player_rank in ["Leader", "R4"]:
                manage_btn = discord.ui.Button(label="Manage Guild", style=discord.ButtonStyle.danger, row=1)
                async def manage_guild_btn_callback(interaction: discord.Interaction):
                    if self.player_rank not in ["Leader", "R4"]:
                        await interaction.response.send_message("You do not have permission to manage the guild.", ephemeral=True)
                        return
                    is_leader = self.player_rank == "Leader"
                    members = self.guild.get("members", {})
                    pending = self.guild.get("pending_requests", [])
                    reqs = self.guild.get("requirements", {})
                    desc = (
                        f"**Guild Name:** {self.guild_name}\n"
                        f"**Leader:** <@{self.guild.get('leader')}>\n"
                        f"**Members:** {len(members)}\n"
                        f"**Pending Requests:** {len(pending)}\n"
                        f"**Requirements:**\n"
                        f"- Castle Level: {reqs.get('castle_level', 'N/A')}\n"
                        f"- Battles Won: {reqs.get('battles_won', 'N/A')}\n"
                        f"**Description:** {self.guild.get('description', 'No description provided.')}\n\n"
                        f"**Member List:**\n" + '\n'.join([f"<@{uid}> ({rank})" for uid, rank in members.items()])
                    )
                    admin_embed = discord.Embed(
                        title=f"Guild Admin Panel: {self.guild_name}",
                        description=desc,
                        color=discord.Color.red()
                    )
                    if self.image_path and os.path.exists(self.image_path):
                        admin_embed.set_thumbnail(url=f"attachment://{os.path.basename(self.image_path)}")
                        file = discord.File(self.image_path, filename=os.path.basename(self.image_path))
                        await interaction.response.edit_message(embed=admin_embed, view=GuildAdminView(is_leader, self.guild, self.guild_name, self.image_path, self.ctx), attachments=[file])
                    else:
                        await interaction.response.edit_message(embed=admin_embed, view=GuildAdminView(is_leader, self.guild, self.guild_name, self.image_path, self.ctx))
                manage_btn.callback = manage_guild_btn_callback
                self.add_item(manage_btn)
    view = GuildInfoView(guild, found_guild, image_path, player_rank, ctx)
    if file:
        await ctx.send(embed=embed, view=view, file=file)
    else:
        await ctx.send(embed=embed, view=view)

@bot.command()
async def currentguildinfo(ctx):
    user_id = str(ctx.author.id)

    # Try new data.json structure first (players/guilds), fallback to old (guilds.json)
    data = None
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            try:
                data = json.load(f)
            except Exception:
                data = None

    player = None
    guild = None
    guild_name = None

    # Try new structure: data["players"][user_id] and data["guilds"][guild_name]
    if data and "players" in data and "guilds" in data:
        player = data["players"].get(user_id)
        if player and player.get("guild_name"):
            guild_name = player["guild_name"]
            guild = data["guilds"].get(guild_name)
    # Fallback: try old structure (guilds.json)
    if not guild:
        if os.path.exists("guilds.json"):
            with open("guilds.json", "r") as f:
                guilds = json.load(f)
            for gname, ginfo in guilds.items():
                if user_id in ginfo.get("members", {}):
                    guild_name = gname
                    guild = ginfo
                    break

    if not guild or not guild_name:
        await ctx.send("❌ You are not in a guild.")
        return

    image_url = guild.get("image_url")
    image_path = guild.get("image_path")
    leader_id = guild.get("leader_id") or guild.get("leader", "unknown")
    leader_name = guild.get("leader_name", f"@{leader_id}")
    members = guild.get("members", {})
    member_count = len(members) if isinstance(members, dict) else len(members) if isinstance(members, list) else 0
    desc = guild.get("description", "No description.")

    # Prepare image for embed (guild_menu_base.png with guild icon and info)
    base_template_path = os.path.join(os.path.dirname(__file__), "guild_menu_base.png")
    image_file = None
    image_file_name = "guild_info.png"
    if os.path.exists(base_template_path):
        try:
            base_image = Image.open(base_template_path).convert("RGBA")
            draw = ImageDraw.Draw(base_image)

            # --- Guild Icon: fit perfectly in the silver box (45,75)-(185,215) ---
            guild_icon = None
            if image_url:
                try:
                    response = requests.get(image_url, timeout=10)
                    response.raise_for_status()
                    guild_icon = Image.open(BytesIO(response.content)).convert("RGBA")
                except Exception:
                    guild_icon = None
            if not guild_icon and image_path and os.path.exists(image_path):
                try:
                    guild_icon = Image.open(image_path).convert("RGBA")
                except Exception:
                    guild_icon = None
            if guild_icon:
                guild_icon = guild_icon.resize((140, 140))
                base_image.paste(guild_icon, (45, 75), guild_icon)

            # --- Font setup with fallback ---
            try:
                font_title = ImageFont.truetype("arialbd.ttf", 38)
            except Exception:
                font_title = ImageFont.load_default()
            try:
                font_text = ImageFont.truetype("arial.ttf", 26)
            except Exception:
                font_text = ImageFont.load_default()
            try:
                font_desc = ImageFont.truetype("arial.ttf", 22)
            except Exception:
                font_desc = ImageFont.load_default()

            # --- Guild Name: top center (middle) ---
            # The image is 700px wide, so center is x=350, y=40
            guild_name_text = guild_name
            w, h = draw.textsize(guild_name_text, font=font_title)
            draw.text((350, 40), guild_name_text, font=font_title, fill="white", anchor="mm")

            # --- Guild Leader and Members: right side, aligned with existing text ---
            # The template has "Guild Leader" at (470, 90), so info should be at (620, 90)
            # "Members" at (470, 130), info at (620, 130)
            draw.text((620, 90), str(leader_name), font=font_text, fill="white", anchor="lm")
            draw.text((620, 130), str(member_count), font=font_text, fill="white", anchor="lm")

            # --- Guild Description: blue box, center bottom ---
            # Blue box is at y~350-410, center x=350, y=380
            desc_text = desc
            # Wrap description if too long
            import textwrap
            desc_lines = textwrap.wrap(desc_text, width=40)
            y_desc = 360
            for line in desc_lines:
                draw.text((350, y_desc), line, font=font_desc, fill="white", anchor="mm")
                y_desc += font_desc.size + 2

            # Save to buffer
            output_buffer = BytesIO()
            base_image.save(output_buffer, format="PNG")
            output_buffer.seek(0)
            image_file = discord.File(fp=output_buffer, filename=image_file_name)
        except Exception:
            image_file = None

    # Build the embed
    embed = discord.Embed(
        title=f"🏰 {guild_name}",
        description=desc,
        color=discord.Color.blue()
    )
    embed.add_field(name="Leader", value=leader_name, inline=True)
    embed.add_field(name="Members", value=str(member_count), inline=True)
    embed.set_footer(text="Guild Info for Members Only")

    # Always set the main image to the generated guild_info.png
    if image_file:
        embed.set_image(url=f"attachment://{image_file_name}")

    # Remove thumbnail to avoid confusion with the main image
    # (If you want to show the guild icon as thumbnail, you can add it back)

    # Buttons
    class GuildInfoButtons(discord.ui.View):
        def __init__(self, guild, guild_name, leader_id, members, ctx):
            super().__init__(timeout=60)
            self.guild = guild
            self.guild_name = guild_name
            self.leader_id = leader_id
            self.members = members
            self.ctx = ctx

        @discord.ui.button(label="Members", style=discord.ButtonStyle.primary)
        async def members_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            msg = '\n'.join([f"<@{uid}> — {rank}" for uid, rank in self.members.items()])
            embed = discord.Embed(title=f"Members of {self.guild_name}", description=msg or "No members.", color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @discord.ui.button(label="Message Leader", style=discord.ButtonStyle.success)
        async def message_leader_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            if str(interaction.user.id) == str(self.leader_id):
                await interaction.response.send_message("You are the leader!", ephemeral=True)
                return
            await interaction.response.send_message("Please type your message to the leader. You have 60 seconds.", ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel == interaction.channel
            try:
                msg = await bot.wait_for('message', check=check, timeout=60)
            except Exception:
                await interaction.followup.send("Timed out. Please try again.", ephemeral=True)
                return
            leader = interaction.guild.get_member(int(self.leader_id))
            if leader:
                await leader.send(f"Message from <@{interaction.user.id}> in guild **{self.guild_name}**:\n```{msg.content}```")
                await interaction.followup.send("Message sent to the leader!", ephemeral=True)
            else:
                await interaction.followup.send("Could not DM the leader.", ephemeral=True)

        @discord.ui.button(label="Leave Guild", style=discord.ButtonStyle.danger)
        async def leave_guild_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            if str(interaction.user.id) == str(self.leader_id):
                await interaction.response.send_message("Leader must use the disband command to leave.", ephemeral=True)
                return
            if str(interaction.user.id) in self.members:
                self.members.pop(str(interaction.user.id))
                if os.path.exists("guilds.json"):
                    with open("guilds.json", "r") as f:
                        guilds = json.load(f)
                    if self.guild_name in guilds and str(interaction.user.id) in guilds[self.guild_name]["members"]:
                        del guilds[self.guild_name]["members"][str(interaction.user.id)]
                        with open("guilds.json", "w") as f:
                            json.dump(guilds, f, indent=4)
                await interaction.response.send_message("You have left the guild.", ephemeral=True)
            else:
                await interaction.response.send_message("You are not a member of this guild.", ephemeral=True)

    view = GuildInfoButtons(guild, guild_name, leader_id, members, ctx)

    # Send embed with the generated image as the main image
    if image_file:
        await ctx.send(embed=embed, view=view, file=image_file)
    else:
        await ctx.send(embed=embed, view=view)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    custom_id = interaction.data.get("custom_id")
    user_id = str(interaction.user.id)
    
    if custom_id == "view_requests":
        await interaction.response.send_message("📬 Here are pending join requests...", ephemeral=True)

    elif custom_id == "rank_manage":
        await interaction.response.send_message("⚙️ Choose a member to promote/demote.", ephemeral=True)
        
    elif custom_id == "kick_member":
        await interaction.response.send_message("💢 Enter a member to kick.", ephemeral=True)
        
    elif custom_id == "disband_guild":
        await interaction.response.send_message("⚠️ Are you sure you want to disband the guild? This is permamnent.", ephemeral=True)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional, only for local dev

token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print('Error: DISCORD_BOT_TOKEN environment variable not set. You can create a .env file with DISCORD_BOT_TOKEN=your-token.')
    sys.exit(1)

bot.run(token)