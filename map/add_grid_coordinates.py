from PIL import Image, ImageDraw, ImageFont

# === SETTINGS ===
input_image = "world_map_for_5000_players.png"
output_image = "world_map_with_coords.png"
cell_size = 45  # same as your original tile size
font_size = 20

# === Load image ===
img = Image.open(input_image)
draw = ImageDraw.Draw(img)

# === Try to load font ===
try:
    font = ImageFont.truetype("arial.ttf", font_size)
except:
    font = ImageFont.load_default()

# === Generate grid labels ===
cols = img.width // cell_size
rows = img.height // cell_size

def get_col_letter(index):
    result = ""
    while index >= 0:
        result = chr(index % 26 + 65) + result
        index = index // 26 - 1
    return result

# === Draw column letters ===
for col in range(cols):
    label = get_col_letter(col)
    x = col * cell_size + 5
    draw.text((x, 2), label, fill="black", font=font)

# === Draw row numbers ===
for row in range(rows):
    label = str(row + 1)
    y = row * cell_size + 2
    draw.text((2, y), label, fill="black", font=font)

# === Save the result ===
img.save(output_image)
print(f"✅ Grid labels added! Saved as {output_image}")
