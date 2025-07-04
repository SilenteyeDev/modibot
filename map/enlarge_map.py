from PIL import Image

# === CONFIG ===
input_image_path = "large_world_map.png"  # your current map
output_image_path = "world_map_for_5000_players.png"  # new map
scale_factor = 3  # how much bigger (2 = double, 3 = triple)

# === PROCESS ===
# Open the existing image
original_img = Image.open(input_image_path)

# Calculate new size
new_width = original_img.width * scale_factor
new_height = original_img.height * scale_factor
new_size = (new_width, new_height)

# Resize using nearest neighbor to preserve the pixel style
resized_img = original_img.resize(new_size, Image.Resampling.NEAREST)

# Save the new image
resized_img.save(output_image_path)

print(f"✅ New map saved as {output_image_path} ({new_width}x{new_height})")
