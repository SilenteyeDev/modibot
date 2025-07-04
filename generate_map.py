from PIL import Image, ImageDraw, ImageFilter
import random

# Settings
grid_cols = 120      # horizontal tiles
grid_rows = 100      # vertical tiles
cell_size = 50       # pixel size per tile
image_width = grid_cols * cell_size
image_height = grid_rows * cell_size

# Terrain styles
terrain_colors = {
    "grass": (110, 170, 110),
    "forest": (34, 139, 34),
    "mountain": (120, 120, 120),
    "water": (70, 130, 180),
    "desert": (237, 201, 175)
}

terrain_weights = {
    "grass": 0.35,
    "forest": 0.2,
    "mountain": 0.15,
    "water": 0.15,
    "desert": 0.15
}

def random_terrain():
    return random.choices(list(terrain_weights.keys()), weights=terrain_weights.values())[0]

def random_location(existing_locations):
    while True:
        col = random.randint(0, grid_cols - 1)
        row = random.randint(0, grid_rows - 1)
        if (col, row) not in existing_locations:
            return (col, row)

# Generate terrain grid
terrain_grid = {}
for col in range(grid_cols):
    for row in range(grid_rows):
        terrain_grid[(col, row)] = random_terrain()

# Generate unique player positions
player_locations = set()
while len(player_locations) < 5000:
    player_locations.add(random_location(player_locations))

# Create the map image
img = Image.new("RGB", (image_width, image_height))
draw = ImageDraw.Draw(img)

# Draw terrain
for (col, row), terrain in terrain_grid.items():
    x0 = col * cell_size
    y0 = row * cell_size
    x1 = x0 + cell_size
    y1 = y0 + cell_size
    draw.rectangle([x0, y0, x1, y1], fill=terrain_colors[terrain])

# Add smooth blur effect
img = img.filter(ImageFilter.GaussianBlur(radius=0.6))

# Draw player castles
for col, row in player_locations:
    x = col * cell_size + cell_size // 2
    y = row * cell_size + cell_size // 2
    draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill="gray", outline="black")

# Save the final image
img.save("5000_player_world_map.png")
print("✅ Map saved as 5000_player_world_map.png")
