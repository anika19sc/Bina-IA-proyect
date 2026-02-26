from PIL import Image, ImageDraw, ImageFont

# Create a 512x512 image (dark blue background)
img = Image.new('RGB', (512, 512), color = (30, 60, 114))

d = ImageDraw.Draw(img)

# Draw a circle
center = (256, 256)
radius = 200
d.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], outline=(255,215,0), width=10)

# Draw text "Bina"
try:
    # Try to use a font, fallback to default
    font = ImageFont.truetype("arial.ttf", 100)
except IOError:
    font = ImageFont.load_default()

text = "Bina"
# Get text bounding box
left, top, right, bottom = d.textbbox((0, 0), text, font=font)
text_width = right - left
text_height = bottom - top

d.text(((512-text_width)/2, (512-text_height)/2), text, font=font, fill=(255, 255, 255))

img.save('frontend/src/assets/icon.png')
print("Icon generated successfully.")
