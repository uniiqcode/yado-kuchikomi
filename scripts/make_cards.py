"""県のページの共有カード（og.jpg、1200×630）を作る。Threads などに URL を貼った時に出る絵。

使い方: python3 scripts/make_cards.py [出力先のフォルダ]   （build_site.py からも呼ばれる）
- 左に県の形（data/geo/<県>.json。地球地図日本（国土地理院）を加工して作成）、右に県の名前と
  「623軒 → 13軒 → 3軒 → 1軒」のような絞り込みの数（chain()）。下の帯は「宿の口コミ」
- 背景の色は県ごと（data/prefs/<県>.json の color）
- 楽天トラベルの写真は使わない（SNS に出るため。楽天トラベルの「ご利用上の注意」）
- Pillow と Noto CJK のフォントが要る。無い時は作らずに None を返す（ページは共通の絵を使う）
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIRS = ["/usr/share/fonts/opentype/noto", "/usr/share/fonts/noto-cjk", "/usr/share/fonts/opentype/noto-cjk"]
KAKI = (216, 105, 26)
W, H = 1200, 630


def _font(name, size):
    from PIL import ImageFont
    for d in FONT_DIRS:
        path = os.path.join(d, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size, index=0)   # index 0 = JP
    raise FileNotFoundError(name)


def chain(p):
    """絞り込みの数の並び。調べた軒数 → 候補 → 行きたい3軒 → 紹介した宿。"""
    nums = [p["funnel"][0][0], len(p["candidates"])]
    three = [c for c in p["candidates"] if c.get("three")]
    picks = [c for c in p["candidates"] if c.get("pick")]
    if three and len(three) < nums[-1]:
        nums.append(len(three))
    if picks and len(picks) < nums[-1]:
        nums.append(len(picks))
    return nums


def note(p):
    """カードの数の下の一言。"""
    if p.get("card_note"):
        return p["card_note"]
    picks = [c for c in p["candidates"] if c.get("pick")]
    if picks:
        return "紹介した宿: " + "、".join(c["name"] for c in picks)
    if any(c.get("three") for c in p["candidates"]):
        return "この中から、行きたい宿の3軒"
    return "評価・夕食・田舎らしさ・行き方で絞りました"


def _wrap(d, text, font, width):
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) > width:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    return lines + ([cur] if cur else [])


def card(p, out_path):
    try:
        from PIL import Image, ImageDraw
        serif, sans, sans_r = "NotoSerifCJK-Bold.ttc", "NotoSansCJK-Bold.ttc", "NotoSansCJK-Regular.ttc"
        _font(serif, 10), _font(sans, 10), _font(sans_r, 10)
    except Exception as e:  # noqa: BLE001  Pillow かフォントが無い
        print(f"カードを作れません（{e}）", file=sys.stderr)
        return None
    with open(os.path.join(ROOT, "data", "geo", f'{p["slug"]}.json'), encoding="utf-8") as f:
        geo = json.load(f)
    bg = tuple(int(p.get("color", "#1E5A6E")[i:i + 2], 16) for i in (1, 3, 5))
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # 県の形（左。緯度で横を縮める）
    pts = [pt for ring in geo["rings"] for pt in ring]
    minx, maxx = min(x for x, _ in pts), max(x for x, _ in pts)
    miny, maxy = min(y for _, y in pts), max(y for _, y in pts)
    k = math.cos(math.radians((miny + maxy) / 2))
    bw, bh = (maxx - minx) * k, maxy - miny
    box_w, box_h = 430, H - 70 - 80
    s = min(box_w / bw, box_h / bh)
    ox, oy = 60 + (box_w - bw * s) / 2, 40 + (box_h - bh * s) / 2
    for ring in geo["rings"]:
        d.polygon([(ox + (x - minx) * k * s, oy + (maxy - y) * s) for x, y in ring], fill=(255, 255, 255))

    # 文字（右）
    x0, right = 540, W - 40
    d.text((x0, 72), "田舎の宿", font=_font(serif, 40), fill=(235, 240, 242))
    d.text((x0, 120), p["pref"], font=_font(serif, 92), fill="white")
    nums = chain(p)
    # 数の並びが右に収まる大きさを探す（最後の数だけ大きく・明るく）
    for size in range(84, 30, -2):
        f_n, f_last, f_arrow = _font(sans, size), _font(sans, int(size * 1.3)), _font(sans, int(size * 0.7))
        parts = [(f"{n:,}軒", f_last if i == len(nums) - 1 else f_n) for i, n in enumerate(nums)]
        total = sum(d.textlength(t, font=f) for t, f in parts) + (len(parts) - 1) * (d.textlength("→", font=f_arrow) + 24)
        if total <= right - x0:
            break
    base = 330 + int(size * 1.3)   # 文字の下の線をそろえる
    x = x0
    for i, (t, f) in enumerate(parts):
        last = i == len(parts) - 1
        d.text((x, base), t, font=f, fill=(255, 190, 120) if last else "white", anchor="ls")
        x += d.textlength(t, font=f)
        if not last:
            d.text((x + 12, base - size * 0.15), "→", font=f_arrow, fill=(250, 200, 150), anchor="ls")
            x += d.textlength("→", font=f_arrow) + 24
    text = note(p)
    for size_n in (30, 28, 26, 24):   # 2行に収まり、最後の行が1〜2字だけにならない大きさ
        f_note = _font(sans_r, size_n)
        lines = _wrap(d, text, f_note, right - x0)
        if len(lines) == 1 or (len(lines) == 2 and len(lines[1]) > 3):
            break
    for i, line in enumerate(lines[:2]):
        d.text((x0, base + 30 + i * (size_n + 12)), line, font=f_note, fill=(225, 235, 238))

    # 下の帯
    d.rectangle((0, H - 70, W, H), fill=KAKI)
    d.text((40, H - 58), "宿の口コミ", font=_font(serif, 36), fill="white")
    d.text((260, H - 48), "uniiqcode.com/yado-kuchikomi", font=_font(sans_r, 24), fill=(255, 235, 215))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, quality=88)
    return out_path


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_site
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "_cards")
    for p in build_site.load_prefs():
        print(card(p, os.path.join(out, p["slug"], "og.jpg")))
