import os
import base64

# Minimal 1x1 pixel transparent PNG
# Source: https://git.io/fAdH5
ONE_PIXEL_PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

ICON_DIR = "d:/Url/version2/Project/extension/icons"
os.makedirs(ICON_DIR, exist_ok=True)

sizes = [16, 48, 128]

for size in sizes:
    with open(f"{ICON_DIR}/icon{size}.png", "wb") as f:
        f.write(ONE_PIXEL_PNG)
    print(f"Created icon{size}.png")
