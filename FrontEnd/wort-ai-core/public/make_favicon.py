from PIL import Image

img = Image.open("/Users/choclate/.gemini/antigravity/brain/eafdd51a-4af9-442e-9dbb-55978bc69496/media__1774145220792.png").convert("RGBA")
w, h = img.size
size = max(w, h)

new_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
new_img.paste(img, ((size - w) // 2, (size - h) // 2), img)

new_img.save("/Users/choclate/Desktop/WORT/FrontEnd/wort-ai-core/public/favicon.ico", format='ICO', sizes=[(16,16), (32,32), (64,64)])
new_img.resize((512, 512), Image.Resampling.LANCZOS).save("/Users/choclate/Desktop/WORT/FrontEnd/wort-ai-core/public/apple-touch-icon.png", format='PNG')
print("Successfully generated icons!")
