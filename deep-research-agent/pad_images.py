import os
from PIL import Image, ImageDraw

colors = {
    "WortHomepage.png": "#1A3C2B",
    "websearchchat.png": "#1A3C2B",
    "Deepresearch.png": "#FF8C69",
    "allocateDynamicNumberofAgents.jpg": "#9EFFBF",
    "parallel research.png": "#1A3C2B",
    "ExtermeResearchFeature.png": "#FF8C69"
}

def add_corners(im, rad):
    mask = Image.new('L', im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + im.size, radius=rad, fill=255)
    
    im_rgba = im.convert("RGBA")
    im_rgba.putalpha(mask)
    return im_rgba

for filename, color in colors.items():
    filepath = f"assets/{filename}"
    if not os.path.exists(filepath):
        print(f"File not found: {filename}")
        continue
    
    # 1. Open the original image
    img = Image.open(filepath)
    
    # Target padding: 5% or 30px minimum
    pad_x = int(img.width * 0.05)
    pad_y = int(img.height * 0.05)
    if pad_x < 30: pad_x = 30
    if pad_y < 30: pad_y = 30
    
    new_w = img.width + pad_x*2
    new_h = img.height + pad_y*2
    
    # 2. Add border radius to inner image (10px as in CSS)
    img_rounded = add_corners(img, 10)
    
    # 3. Create the background pad
    bg = Image.new('RGBA', (new_w, new_h), color)
    # Convert bg to have rounded corners too (16px as in CSS)
    bg_rounded = add_corners(bg, 16)
    
    # 4. Paste inner image onto background (using alpha channel as mask for transparency)
    bg_rounded.paste(img_rounded, (pad_x, pad_y), img_rounded)
    
    # Save as PNG unconditionally since it has transparency
    new_filepath = filepath
    if filepath.endswith(".jpg"):
        new_filepath = filepath.replace(".jpg", ".png")
        os.remove(filepath) # Keep the git index clean
        
    bg_rounded.save(new_filepath)
    print(f"Padded {filename}")
    
