"""data/ から、公開するページ _site/ を作る。

使い方: python3 scripts/build_site.py
- トップ（index.html）: 県のカード・遍路宿・紹介した宿（追加した順＝先着順）
- 県のページ（<slug>/index.html）: どうやって探したか（絞り込みの段）と、候補の宿（data/prefs/<slug>.json）。
  候補の一覧は #candidates で直接開ける（Threads から「候補の宿」へすぐ飛ばすため）
- 遍路宿のページ（henro/index.html）: 紹介した遍路宿
- 県のページの共有カード（<slug>/og.jpg）は scripts/make_cards.py（Pillow と Noto CJK が無ければ共通の絵）
- 宿の写真は data/rakuten.json（scripts/fetch_images.py が楽天トラベルの API で取った URL）。左下に楽天トラベルのクレジット
- 一覧は HTML に書き込む（検索対策。seo-uniiqcode スキルの手順2）。sitemap.xml も作る
"""
import datetime
import glob
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_cards  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://uniiqcode.com/yado-kuchikomi/"   # 正式な URL（seo-uniiqcode スキル）
THREADS_URL = "https://www.threads.com/@yado_kuchikomi"
MARKS = {"solo": "一人旅", "henro": "遍路宿"}
ACCESS = {"○": "acc-ok", "△": "acc-mid", "?": "acc-q"}
JST = datetime.timezone(datetime.timedelta(hours=9))
DESC = "県ごとに宿のクチコミを読んで、一人で行くなら・だれかと行くならの宿を紹介します。四国の遍路宿もオフシーズンに。良いところと、合わない人がいそうな点、冬と行き方まで。"
e = html.escape


def read(*path):
    with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
        return json.load(f)


def load():
    return sorted(read("data", "yado.json"), key=lambda y: (y["added"], y["id"]))   # 先着順


def load_prefs():
    prefs = [read(p) for p in glob.glob(os.path.join(ROOT, "data", "prefs", "*.json"))]
    return sorted(prefs, key=lambda p: p["checked"], reverse=True)   # 新しく調べた県が上


def load_images():
    path = os.path.join(ROOT, "data", "rakuten.json")
    return read("data", "rakuten.json") if os.path.exists(path) else {}


def jp_date(s):
    d = datetime.date.fromisoformat(s)
    return f"{d.year}年{d.month}月{d.day}日"


def photo(no, name, images):
    img = images.get(str(no)) if no else None
    if not img or not img.get("image"):
        return ""
    return (f'<figure class="ph"><img src="{e(img["image"])}" alt="{e(name)}（楽天トラベル）" loading="lazy" '
            f'width="600" height="400" referrerpolicy="no-referrer-when-downgrade"><figcaption>楽天トラベル</figcaption></figure>')


def own_photo(y):
    """人が自分で撮った写真（site/assets/photos/）。楽天トラベルの画像ではないので、宿のところだけでなく SNS にも使える。"""
    ph = y.get("photo")
    if not ph:
        return ""
    return (f'<figure class="ph"><img src="{e(SITE_URL + ph["file"])}" alt="{e(ph["alt"])}" loading="lazy" '
            f'width="600" height="338"><figcaption>{e(ph["caption"])}</figcaption></figure>')


def rakuten_link(link, fallback=""):
    """人が作った楽天アフィリエイトのリンクを優先。無ければ API が返した楽天トラベルのページ。"""
    if link:
        return (f'<p class="link"><a href="{e(link)}" target="_blank" rel="nofollow sponsored noopener">'
                f'楽天トラベルで見る</a><span class="pr">PR（楽天アフィリエイト）</span></p>')
    if fallback:
        return (f'<p class="link"><a href="{e(fallback)}" target="_blank" rel="nofollow noopener">'
                f'楽天トラベルで見る</a></p>')
    return ""


def card(y, images):
    marks = "".join(f'<span class="mark mark-{m}">{MARKS[m]}</span>' for m in y["marks"] if m in MARKS)
    r = y["rating"]
    rows = []
    if y.get("winter"):
        rows.append(f'<div class="row"><dt>冬</dt><dd>{e(y["winter"])}</dd></div>')
    if y.get("access"):
        rows.append(f'<div class="row"><dt>行き方</dt><dd>{e(y["access"])}</dd></div>')
    own = f'<p class="own">{e(y["own"])}</p>' if y.get("own") else ""
    note = f'<p class="note">{e(y["note"])}</p>' if y.get("note") else ""
    img = images.get(str(y.get("hotelNo") or ""), {})
    return f'''<article class="yado" id="{e(y["id"])}" data-id="{e(y["id"])}" data-marks="{e(" ".join(y["marks"]))}" data-added="{e(y["added"])}">
  <div class="head">
    <p class="where"><span class="kind">{e(y["kind"])}</span>{e(y["pref"])}・{e(y["area"])}</p>
    <h2>{e(y["name"])}</h2>
    <p class="marks">{marks}</p>
    <button class="save" type="button" aria-pressed="false" aria-label="{e(y["name"])}を行ってみたいに保存">行ってみたい</button>
  </div>
  {own_photo(y) or photo(y.get("hotelNo"), y["name"], images)}
  <p class="lead">{e(y["lead"])}</p>
  {own}
  <p class="src">{e(r["source"])}のクチコミ{r["count"]:,}件・評価{e(r["score"])}（{jp_date(r["checked"])}時点）を読んで</p>
  <h3>良いところ</h3>
  <ul class="good">{"".join(f"<li>{e(g)}</li>" for g in y["good"])}</ul>
  <h3>合わない人がいそうな点</h3>
  <ul class="caveat">{"".join(f"<li>{e(c)}</li>" for c in y["caveat"])}</ul>
  <dl>{"".join(rows)}</dl>
  {note}
  {rakuten_link(y.get("link", ""), img.get("url", ""))}
  <p class="added">{jp_date(y["added"])}に追加</p>
</article>'''


def cand_card(c, images, yado_ids):
    r = c["rating"]
    a = c["access"]
    pick = ""
    if c.get("pick") and c["pick"] in yado_ids:
        pick = f'<a class="pick" href="../#{e(c["pick"])}">紹介した宿 → 詳しく</a>'
    if c.get("three"):
        pick = '<span class="pick three">行きたい宿の3軒</span>' + pick
    img = images.get(str(c["hotelNo"]), {})
    acc = f'<span class="acc {ACCESS.get(a["mark"], "acc-q")}">{e(a["mark"])} {e(a["note"])}</span>' if a.get("note") else ""
    rv = c.get("review")
    if rv:
        rows = "".join(f'<div class="row"><dt>{k}</dt><dd>{e(rv[f])}</dd></div>'
                       for k, f in (("一人旅", "solo"), ("冬", "winter"), ("行き方", "access")) if rv.get(f))
        review = f'''<details class="rv" open>
    <summary>クチコミのまとめ</summary>
    <p class="src">楽天トラベルのクチコミ{rv["count"]:,}件・評価{e(rv["score"])}（{jp_date(rv["checked"])}時点）、2年以内の{rv["recent"]}件を読んで</p>
    <h4>良いところ</h4><ul class="good">{"".join(f"<li>{e(g)}</li>" for g in rv["good"])}</ul>
    <h4>合わない人がいそうな点</h4><ul class="caveat">{"".join(f"<li>{e(x)}</li>" for x in rv["caveat"])}</ul>
    <dl>{rows}</dl>
  </details>'''
    else:
        review = '<p class="rv-yet">クチコミのまとめは準備中です</p>'
    return f'''<article class="cand" id="h{e(str(c["hotelNo"]))}">
  {pick}
  <h3 class="cn">{e(c["name"])}</h3>
  <p class="cw">{e(c["place"])}</p>
  {photo(c["hotelNo"], c["name"], images)}
  <p class="cr">{e(c["lead"])}</p>
  <div class="cm"><span>楽天 {e(r["score"])}（{r["count"]:,}件）</span><span>夕食 {float(r["dinner"]):.2f}</span>{acc}</div>
  {review}
  {rakuten_link(c.get("link", ""), img.get("url", ""))}
</article>'''


def json_ld(name, url, items):
    data = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": "宿の口コミ", "url": SITE_URL, "inLanguage": "ja"},
        {"@type": "ItemList", "name": name, "numberOfItems": len(items),
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "url": u} for i, (n, u) in enumerate(items)]},
    ]}
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def stage_text(p, k):
    """段ごとのページのタイトルと説明。その段より先の結果（軒数・宿の名前）を出さない。"""
    st = make_cards.steps(p)[:k]
    n_first, kind, pref = st[0][0], st[-1][1], p["pref"]
    if kind == "all":
        return (f"{pref}の田舎の宿｜{n_first:,}軒から探します｜宿の口コミ",
                f"{pref}の楽天トラベルの宿{n_first:,}軒から、評価・夕食・田舎らしさ・行き方で田舎の宿を探します。")
    n_c = st[1][0]
    if kind == "cands":
        return (f"{pref}の田舎の宿｜{n_first:,}軒から{n_c}軒へ｜宿の口コミ",
                f"{pref}の楽天トラベルの宿{n_first:,}軒から、評価・夕食・田舎らしさ・行き方で{n_c}軒に絞りました。どう探したかと、候補の宿の写真・評価・行き方。")
    if kind == "three":
        return (f"{pref}の田舎の宿｜{n_c}軒から行きたい宿の3軒｜宿の口コミ",
                f"{pref}の楽天トラベルの宿{n_first:,}軒から{n_c}軒に絞り、クチコミを読んで行きたい宿の3軒を選びました。")
    names = "、".join(c["name"] for c in p["candidates"] if c.get("pick"))
    return (f"{pref}の田舎の宿｜紹介した宿: {names}｜宿の口コミ",
            f"{pref}の楽天トラベルの宿{n_first:,}軒から絞り込み、クチコミを読んで選んだ宿: {names}。")


def stage_page(title, desc, url, og):
    """段ごとのカードを出すだけのページ。人は県のページへ移る（#の後ろも引き継ぐ）。検索には出さない。
    og:url は自分の URL にする（Threads が og:url の先のカードを読みに行かないように）。"""
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex">
<meta property="og:type" content="website">
<meta property="og:site_name" content="宿の口コミ">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<script>location.replace("../" + location.hash)</script>
</head>
<body><p><a href="../">{e(title)}</a></p></body>
</html>
'''


def layout(*, title, desc, url, depth, body, ld, tabs, current, og=""):
    up = "../" * depth
    cur = ' aria-current="page"'
    tab_html = "".join(
        f'<a href="{up}{href}"{cur if key == current else ""}>{e(label)}</a>' for key, label, href in tabs)
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#D8691A">
<meta property="og:type" content="website">
<meta property="og:site_name" content="宿の口コミ">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og or SITE_URL + "assets/og.jpg"}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="{up}manifest.webmanifest">
<link rel="icon" href="{up}assets/favicon.ico" sizes="any">
<link rel="icon" href="{up}assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
<meta name="apple-mobile-web-app-title" content="宿の口コミ">
<link rel="stylesheet" href="{up}assets/style.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<header class="top">
  <div class="wrap">
    <a href="{up}" style="display:contents;color:inherit;text-decoration:none"><img src="{up}assets/icon-192.png" width="64" height="64" alt="宿の口コミのロゴ"></a>
    <div>
      <{"h1" if depth == 0 else "p"} class="site" style="margin:0;font-family:'Hiragino Mincho ProN','Yu Mincho','Noto Serif JP',serif;font-size:28px;font-weight:700;letter-spacing:.06em;line-height:1.2">宿の口コミ</{"h1" if depth == 0 else "p"}>
      <p class="tag">読んで見つけた良いところ</p>
    </div>
  </div>
</header>
<div class="wrap"><nav class="tabs" aria-label="ページ">{tab_html}</nav></div>
{body}
<footer>
  <div class="wrap">
    <p>Threads で毎朝投稿しています: <a href="{THREADS_URL}" target="_blank" rel="noopener">@yado_kuchikomi</a></p>
    <p>クチコミの要約は、楽天トラベルなどのクチコミを読んで、3件以上に出てくる声を自分の言葉でまとめたものです（件数と評価は書いた日の時点）。クチコミの文章は載せていません。料金・空室は、リンク先で確かめてください。</p>
    <p>宿の写真は、楽天トラベルの API で提供されている画像です（左下に「楽天トラベル」と表示）。「楽天トラベルで見る」のうち「PR」と書いたものは、楽天アフィリエイトの広告です。</p>
    <p><a href="https://webservice.rakuten.co.jp/" target="_blank" rel="noopener">Supported by Rakuten Developers</a></p>
    <p>県の形（共有した時の絵）: 地球地図日本（国土地理院）を加工して作成</p>
    <p>更新: {{{{UPDATED}}}}</p>
  </div>
</footer>
<script src="{up}assets/app.js"></script>
<script src="https://uniiqcode.com/assets/a2hs.js" data-app="宿の口コミ" defer></script>
<script src="https://uniiqcode.com/assets/home-guide.js" data-app="宿の口コミ" data-url="https://uniiqcode.com/yado-kuchikomi/" defer></script>
</body>
</html>'''


def funnel(steps):
    top = steps[0][0]
    return "".join(
        f'<div class="step"><div class="bar" style="width:{max(40, int(160 * (n / top) ** 0.5))}px">{n:,}</div><div class="lbl">{e(l)}</div></div>'
        for n, l in steps)


def build(out=os.path.join(ROOT, "_site")):
    items = load()
    prefs = load_prefs()
    images = load_images()
    today = datetime.datetime.now(JST).date().isoformat()
    yado_ids = {y["id"] for y in items}
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(os.path.join(ROOT, "site"), out)
    tabs = [("top", "トップ", "")] + [(p["slug"], p["pref"].rstrip("県"), f'{p["slug"]}/') for p in prefs] + [("henro", "遍路宿", "henro/")]
    pages = {}

    # トップ
    pref_cards = "".join(
        f'<a class="pc" href="{e(p["slug"])}/"><span class="n">{e(p["pref"])}</span>'
        f'<span class="t{" done" if any(c.get("pick") for c in p["candidates"]) else ""}">'
        f'{"紹介済み" if any(c.get("pick") for c in p["candidates"]) else "調べ中"}</span>'
        f'<p>{p["funnel"][0][0]:,}軒 → {len(p["candidates"])}軒。{e(p["status"])}</p></a>' for p in prefs)
    henro = [y for y in items if "henro" in y["marks"]]
    henro_names = "・".join(y["name"].replace("民宿 ", "").replace("古民家の宿 ", "") for y in henro)
    body = f'''<div class="wrap intro">
  <p class="catch">行ったことのない場所に、思いを馳せる。</p>
  <p>県ごとに宿のクチコミを読んで3軒を選び、「一人で行くならここ」「だれかと行くならここ」を紹介します。四国の遍路宿は、宿を応援したいので、お客の少ないオフシーズンに。</p>
  <p class="prnote">このページには、楽天アフィリエイトの広告（PR）のリンクがあります。リンクから予約されると、紹介した人に報酬が入ることがあります。</p>
  <h2 class="sec">県で探す</h2>
  <div class="prefs">{pref_cards}</div>
  <h2 class="sec">四国の遍路宿</h2>
  <div class="prefs"><a class="pc" href="henro/"><span class="n">遍路宿</span><span class="t done">{len(henro)}軒</span><p>{e(henro_names)}（オフシーズンに紹介）</p></a></div>
  <h2 class="sec">紹介した宿</h2>
</div>
<nav class="filters" aria-label="絞り込み">
  <div class="wrap">
    <button type="button" data-filter="all" aria-pressed="true">すべて</button>
    <button type="button" data-filter="solo" aria-pressed="false">一人旅</button>
    <button type="button" data-filter="henro" aria-pressed="false">遍路宿</button>
    <button type="button" data-filter="saved" aria-pressed="false">行ってみたい</button>
  </div>
</nav>
<main class="wrap">
  <p class="count" id="count">紹介した宿 {len(items)}軒（追加した順）</p>
  <div id="list">
{chr(10).join(card(y, images) for y in items)}
  </div>
  <p class="empty" id="empty" hidden>まだありません。「行ってみたい」を押すと、ここに集まります（このスマホの中だけに保存）。</p>
</main>'''
    pages["index.html"] = layout(
        title="宿の口コミ｜クチコミを読んで見つけた田舎の宿・遍路宿", desc=DESC, url=SITE_URL, depth=0, body=body,
        ld=json_ld("宿の口コミで紹介した宿", SITE_URL, [(y["name"], f'{SITE_URL}#{y["id"]}') for y in items]),
        tabs=tabs, current="top")

    # 県のページ
    for p in prefs:
        url = f'{SITE_URL}{p["slug"]}/'
        cands = p["candidates"]
        groups = p["areas"] or [""]
        sections = []
        # 行きたい宿の3軒を決めたら、いちばん上にまとめる（紹介した1軒を先頭に）。残りは地域ごと
        three = sorted((c for c in cands if c.get("three")), key=lambda c: not c.get("pick"))
        if three:
            sections.append(f'<h3 class="area">行きたい宿の{len(three)}軒<span>{len(three)}軒</span></h3>'
                            + "".join(cand_card(c, images, yado_ids) for c in three))
            if len(three) < len(cands):
                sections.append(f'<h3 class="area">ほかの候補<span>{len(cands) - len(three)}軒</span></h3>')
        rest = [c for c in cands if not c.get("three")]
        for a in groups:
            cs = [c for c in rest if c.get("area", "") == a] if a else rest
            if not cs:
                continue
            head = f'<h3 class="area">{e(a)}<span>{len(cs)}軒</span></h3>' if a else ""
            sections.append(head + "".join(cand_card(c, images, yado_ids) for c in cs))
        n_first = p["funnel"][0][0]
        title = f'{p["pref"]}の田舎の宿｜{n_first:,}軒から{len(cands)}軒へ｜宿の口コミ'
        desc = f'{p["pref"]}の楽天トラベルの宿{n_first:,}軒から、評価・夕食・田舎らしさ・行き方で{len(cands)}軒に絞りました。どう探したかと、候補の宿の写真・評価・行き方。'
        body = f'''<main class="wrap">
  <p class="crumb"><a href="../">宿の口コミ</a> ＞ {e(p["pref"])}</p>
  <h1 class="ph1">{e(p["pref"])}の田舎の宿</h1>
  <p class="count">{n_first:,}軒から{len(cands)}軒へ（{jp_date(p["checked"])}に調べました）</p>
  <p class="status">{e(p["status"])}</p>
  <p class="jump"><a href="#candidates">候補の{len(cands)}軒をすぐに見る ↓</a></p>
  <p class="prnote">このページには、楽天アフィリエイトの広告（PR）のリンクがあります。</p>
  <h2 class="sec">どうやって探したか</h2>
  <div class="funnel">{funnel(p["funnel"])}</div>
  <h2 class="sec" id="candidates">候補の{len(cands)}軒</h2>
  {"".join(sections)}
  <p class="credit-note">評価・件数・夕食の点は楽天トラベルの値（{jp_date(p["checked"])}時点）。行き方の印: ○ 駅から歩ける・バスや送迎で行ける／△ 要確認／? 見つからない。Googleマップの点数は載せていません（4.0以上であることだけ確かめました）。</p>
</main>'''
        has_card = make_cards.card(p, os.path.join(out, p["slug"], "og.jpg")) is not None
        if has_card:   # 段ごとのカードと、それを出すだけの小さなページ（投稿にはその日の段の URL を貼る）
            for k in range(1, len(make_cards.steps(p)) + 1):
                make_cards.card(p, os.path.join(out, p["slug"], f"og-s{k}.jpg"), stage=k)
                st, sd = stage_text(p, k)
                pages[f'{p["slug"]}/s{k}/index.html'] = stage_page(st, sd, f"{url}s{k}/", f"{url}og-s{k}.jpg")
        pages[f'{p["slug"]}/index.html'] = layout(
            title=title, desc=desc, url=url, depth=1, body=body, og=f"{url}og.jpg" if has_card else "",
            ld=json_ld(f'{p["pref"]}の田舎の宿の候補', url, [(c["name"], f'{url}#h{c["hotelNo"]}') for c in cands]),
            tabs=tabs, current=p["slug"])

    # 遍路宿のページ
    url = f"{SITE_URL}henro/"
    body = f'''<main class="wrap">
  <p class="crumb"><a href="../">宿の口コミ</a> ＞ 遍路宿</p>
  <h1 class="ph1">四国の遍路宿</h1>
  <p class="status">歩き遍路で泊まった宿や、道中の宿。宿を応援したいので、お客の少ないオフシーズンに紹介します。</p>
  <p class="prnote">このページには、楽天アフィリエイトの広告（PR）のリンクがあります。</p>
  <div id="list">
{chr(10).join(card(y, images) for y in henro)}
  </div>
</main>'''
    pages["henro/index.html"] = layout(
        title="四国の遍路宿｜宿の口コミ", desc="歩き遍路で泊まった宿や、道中の宿を、クチコミを読んで紹介します。宿を応援したいので、オフシーズンに。",
        url=url, depth=1, body=body,
        ld=json_ld("四国の遍路宿", url, [(y["name"], f'{url}#{y["id"]}') for y in henro]),
        tabs=tabs, current="henro")

    for path, page in pages.items():
        os.makedirs(os.path.dirname(os.path.join(out, path)) or out, exist_ok=True)
        with open(os.path.join(out, path), "w", encoding="utf-8") as f:
            f.write(page.replace("{{UPDATED}}", jp_date(today)))
    urls = [SITE_URL] + [f"{SITE_URL}{p.rsplit('/', 1)[0]}/" for p in pages
                         if p != "index.html" and not re.search(r"/s\d+/index\.html$", p)]
    with open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    return out


if __name__ == "__main__":
    print(build())
