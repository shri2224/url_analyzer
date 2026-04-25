import os
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, path):
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Draw background shield-like shape
    d.ellipse([2, 2, size-2, size-2], fill="#1e3a5f", outline="#60a5fa", width=2)
    
    # Draw "G" text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
        # Scale font size roughly
        # For default font, we can't scale, so this is just a placeholder
        # Ideally we'd use a ttf but we don't want to rely on system fonts
    except:
        pass

    # Save
    img.save(path)
    print(f"Created {path}")

# Ensure directory exists
os.makedirs("d:/Url/version2/Project/extension/icons", exist_ok=True)

# Generate sizes
create_icon(16, "d:/Url/version2/Project/extension/icons/icon16.png")
create_icon(48, "d:/Url/version2/Project/extension/icons/icon48.png")
create_icon(128, "d:/Url/version2/Project/extension/icons/icon128.png")
