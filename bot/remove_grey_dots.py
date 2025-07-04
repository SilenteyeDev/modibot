from PIL import Image

# Path to your map image
image_path = "world_map_with_coords.png"

# Open the image
img = Image.open(image_path).convert("RGBA")
pixels = img.load()

width, height = img.size

# Define what counts as 'grey' (tweak as needed)
def is_grey(r, g, b, threshold=15, min_brightness=100, max_brightness=220):
    return (
        abs(r - g) < threshold and abs(g - b) < threshold and abs(r - b) < threshold
        and min_brightness <= r <= max_brightness
    )

removed = 0
for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        if is_grey(r, g, b):
            pixels[x, y] = (r, g, b, 0)  # Make transparent
            removed += 1

img.save(image_path)
print(f"Done. Removed {removed} grey dots from {image_path}.")
