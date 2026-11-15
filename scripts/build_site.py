"""data/yado.json と site/template.html から、公開するページ _site/ を作る。

使い方: python3 scripts/build_site.py
- 宿の一覧は HTML に書き込む（検索エンジンが読めるように。seo-uniiqcode スキルの手順2）。
  絞り込み（一人旅・遍路宿・保存）は、書き込んだ HTML を JavaScript で出し入れする
- 並びは追加した順（先着順。added が古いものから）
- sitemap.xml も作る（日付は作った日）
"""
import datetime
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://uniiqcode.com/yado-kuchikomi/"   # 正式な URL（seo-uniiqcode スキル）
THREADS_URL = "https://www.threads.com/@yado_kuchikomi"
MARKS = {"solo": "一人旅", "henro": "遍路宿"}
JST = datetime.timezone(datetime.timedelta(hours=9))


def load():
    with open(os.path.join(ROOT, "data", "yado.json"), encoding="utf-8") as f:
        items = json.load(f)
    return sorted(items, key=lambda y: (y["added"], y["id"]))   # 先着順


def jp_date(s):
    d = datetime.date.fromisoformat(s)
    return f"{d.year}年{d.month}月{d.day}日"


def card(y):
    e = html.escape
    marks = "".join(f'<span class="mark mark-{m}">{MARKS[m]}</span>' for m in y["marks"] if m in MARKS)
    good = "".join(f"<li>{e(g)}</li>" for g in y["good"])
    caveat = "".join(f"<li>{e(c)}</li>" for c in y["caveat"])
    r = y["rating"]
    rows = []
    if y.get("winter"):
        rows.append(f'<div class="row"><dt>冬</dt><dd>{e(y["winter"])}</dd></div>')
    if y.get("access"):
        rows.append(f'<div class="row"><dt>行き方</dt><dd>{e(y["access"])}</dd></div>')
    own = f'<p class="own">{e(y["own"])}</p>' if y.get("own") else ""
    note = f'<p class="note">{e(y["note"])}</p>' if y.get("note") else ""
    if y.get("link"):
        link = (f'<p class="link"><a href="{e(y["link"])}" target="_blank" rel="nofollow sponsored noopener">'
                f'楽天トラベルで見る</a><span class="pr">PR（楽天アフィリエイト）</span></p>')
    else:
        link = ""
    marks_attr = " ".join(y["marks"])
    return f'''<article class="yado" id="{e(y["id"])}" data-id="{e(y["id"])}" data-marks="{e(marks_attr)}" data-added="{e(y["added"])}">
  <div class="head">
    <p class="where"><span class="kind">{e(y["kind"])}</span>{e(y["pref"])}・{e(y["area"])}</p>
    <h2>{e(y["name"])}</h2>
    <p class="marks">{marks}</p>
    <button class="save" type="button" aria-pressed="false" aria-label="{e(y["name"])}を行ってみたいに保存">行ってみたい</button>
  </div>
  <p class="lead">{e(y["lead"])}</p>
  {own}
  <p class="src">{e(r["source"])}のクチコミ{r["count"]:,}件・評価{e(r["score"])}（{jp_date(r["checked"])}時点）を読んで</p>
  <h3>良いところ</h3>
  <ul class="good">{good}</ul>
  <h3>合わない人がいそうな点</h3>
  <ul class="caveat">{caveat}</ul>
  <dl>{"".join(rows)}</dl>
  {note}
  {link}
  <p class="added">{jp_date(y["added"])}に追加</p>
</article>'''


def json_ld(items):
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "name": "宿の口コミ", "url": SITE_URL, "inLanguage": "ja"},
            {"@type": "ItemList", "name": "宿の口コミで紹介した宿", "itemListOrder": "https://schema.org/ItemListOrderAscending",
             "numberOfItems": len(items),
             "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "name": y["name"], "url": f'{SITE_URL}#{y["id"]}'}
                 for i, y in enumerate(items)]},
        ],
    }
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def build(out=os.path.join(ROOT, "_site")):
    items = load()
    today = datetime.datetime.now(JST).date().isoformat()
    with open(os.path.join(ROOT, "site", "template.html"), encoding="utf-8") as f:
        page = f.read()
    prefs = []
    for y in items:
        if y["pref"] not in prefs:
            prefs.append(y["pref"])
    page = (page.replace("{{CARDS}}", "\n".join(card(y) for y in items))
                .replace("{{COUNT}}", str(len(items)))
                .replace("{{PREFS}}", html.escape("・".join(prefs)))
                .replace("{{JSON_LD}}", json_ld(items))
                .replace("{{SITE_URL}}", SITE_URL)
                .replace("{{THREADS_URL}}", THREADS_URL)
                .replace("{{UPDATED}}", jp_date(today)))
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(os.path.join(ROOT, "site"), out, ignore=shutil.ignore_patterns("template.html"))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                f"  <url><loc>{SITE_URL}</loc><lastmod>{today}</lastmod></url>\n"
                "</urlset>\n")
    return out


if __name__ == "__main__":
    print(build())
