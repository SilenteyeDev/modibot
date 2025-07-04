# Castle RPG Discord Bot

A feature-rich Discord RPG bot with a world map, guild system, player management, and map generation utilities.

## Features

- **Player System:** Start, train, collect resources, upgrade castle, and view stats.
- **World Map:** Procedurally generated map for up to 5000 players, with coordinates and player locations.
- **Guild System:** Create, join, manage, and disband guilds. Set requirements, upload guild images, and manage ranks.
- **Interactive UI:** Uses Discord embeds, buttons, and slash commands for a modern experience.
- **Map Utilities:** Python scripts for generating and editing the world map.

## Directory Structure

```
.
├── bot/
│   ├── bot.py                # Main Discord bot code
│   ├── .env                  # Bot token (should be in .gitignore)
│   ├── data.json             # Player data (auto-generated)
│   ├── guilds.json           # Guild data (auto-generated)
│   ├── remove_grey_dots.py   # Map utility
│   ├── world_map_with_coords.png # Map with grid
│   └── guild_images/         # Guild icon uploads
├── map/
│   ├── add_grid_coordinates.py # Add grid labels to map
│   ├── enlarge_map.py          # Enlarge map image
│   └── large_world_map.png     # Base map image
├── data.json                # Player data (legacy)
├── guilds.json              # Guild data (legacy)
├── generate_map.py          # Generate a new world map
├── 5000_player_world_map.png # Generated map
├── world_map_updated.png    # Updated map
├── .gitignore
└── README.md
```

## Setup

1. **Install Python dependencies:**
   ```sh
   pip install discord.py pillow python-dotenv aiohttp requests
   ```

2. **Create a `.env` file in the `bot/` directory:**
   ```
   DISCORD_BOT_TOKEN=your-bot-token-here
   ```

3. **Run the bot:**
   ```sh
   cd bot
   python bot.py
   ```

4. **(Optional) Generate or edit maps:**
   - Use `generate_map.py` to create a new map.
   - Use scripts in `map/` to enlarge or add coordinates to maps.

## Commands

- `!start` — Start your adventure or return to your kingdom.
- `!tutorial` — Guided tutorial for new players.
- `!build <building>` — Build structures (currently only 'castle').
- `!collect` — Collect resources.
- `!train` — Train troops.
- `!upgrade <building>` — Upgrade your castle.
- `!profile` / `!info` / `!stats` — View your stats.
- `!world` — View the world map with all players.
- **Guilds:**
  - `!createguild` — Create a new guild.
  - `!joinguild <guild>` — Request to join a guild.
  - `!guildlist` — List all guilds.
  - `!guildinfo <guild>` — View info about a guild.
  - `!leaveguild` — Leave your current guild.
  - `!disbandguild` — Disband your guild (leader only).
  - `!accept <guild> <member_id>` — Accept join requests.
  - `!setrank <guild> <member_id> <rank>` — Set member rank.

Use `!help` in Discord for an interactive help menu.
