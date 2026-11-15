"""アイコン（ホーム画面・タブ）と、共有した時の絵（og.jpg）を作る。

使い方: python3 scripts/make_icons.py   （Pillow が必要）
- 元の絵は design/logo-source.png（Threads・Instagram と同じアイコン。柿色の正方形いっぱいに白い文字「宿の／口コミ」、1080×1080）
- 元の絵がまだ無い時は、仮のアイコン（ゴシック体の文字）を作る。本物を置いたら、もう一度動かす
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "design", "logo-source.png")
OUT = os.path.join(ROOT, "site", "assets")
KAKI = (216, 105, 26)   # #D8691A


def placeholder(size=1080):
    img = Image.new("RGB", (size, size), KAKI)
    d = ImageDraw.Draw(img)
    font = None
    for path in ("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf", "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"):
        if os.path.exists(path):
            font = ImageFont.truetype(path, 300)
            break
    font = font or ImageFont.load_default()
    for text, y in (("宿の", 250), ("口コミ", 570)):
        w = d.textlength(text, font=font)
        d.text(((size - w) / 2, y), text, font=font, fill="white")
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    src = Image.open(SRC).convert("RGB") if os.path.exists(SRC) else placeholder()
    if not os.path.exists(SRC):
        print("design/logo-source.png が無いので、仮のアイコンを作りました")
    for name, size in (("icon-192.png", 192), ("icon-512.png", 512), ("apple-touch-icon.png", 180), ("favicon-32.png", 32)):
        src.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name))
    src.resize((48, 48), Image.LANCZOS).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    # Android の丸い切り抜き用: 絵を直径80%の円に収める（背景は同じ柿色）
    m = Image.new("RGB", (512, 512), KAKI)
    inner = src.resize((410, 410), Image.LANCZOS)
    m.paste(inner, (51, 51))
    m.save(os.path.join(OUT, "icon-maskable-512.png"))
    # 共有した時の絵（1200×630）: 柿色の中央にアイコン
    og = Image.new("RGB", (1200, 630), KAKI)
    og.paste(src.resize((520, 520), Image.LANCZOS), (340, 55))
    og.save(os.path.join(OUT, "og.jpg"), quality=88)


if __name__ == "__main__":
    main()
