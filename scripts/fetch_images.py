"""楽天トラベル施設検索API（SimpleHotelSearch）で、宿の画像の URL と楽天トラベルのページの URL を取る。

使い方: python3 scripts/fetch_images.py
- data/yado.json と data/prefs/*.json に出てくる hotelNo をまとめて調べ、data/rakuten.json に書く
- 環境変数 RAKUTEN_APP_ID・RAKUTEN_ACCESS_KEY・RAKUTEN_REFERER が要る（楽天ウェブサービスのアプリ。キーはコミットしない）
- 画像はダウンロードしない。API が返す URL をそのままページに出す（楽天トラベルの「ご利用上の注意」:
  API の画像はクレジットを左下に付け、テキストリンクと一緒に、その宿への誘導だけに使う。SNS には使わない）
- アフィリエイトIDは渡さない。ページに出すリンクは、人が作った楽天アフィリエイトのリンク（data の link）を優先する
- 1秒に1回までしかリクエストしない。標準ライブラリだけで動く
"""
import datetime
import glob
import json
import os
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENDPOINT = "https://openapi.rakuten.co.jp/engine/api/Travel/SimpleHotelSearch/20260731"
JST = datetime.timezone(datetime.timedelta(hours=9))


def hotel_numbers():
    nos = []
    with open(os.path.join(ROOT, "data", "yado.json"), encoding="utf-8") as f:
        nos += [str(y["hotelNo"]) for y in json.load(f) if y.get("hotelNo")]
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "prefs", "*.json"))):
        with open(path, encoding="utf-8") as f:
            nos += [str(c["hotelNo"]) for c in json.load(f)["candidates"]]
    return list(dict.fromkeys(nos))


def fetch(nos):
    ref = os.environ["RAKUTEN_REFERER"]
    parts = urllib.parse.urlsplit(ref)
    q = {"format": "json", "formatVersion": "2", "hotelNo": ",".join(nos),
         "applicationId": os.environ["RAKUTEN_APP_ID"], "accessKey": os.environ["RAKUTEN_ACCESS_KEY"]}
    req = urllib.request.Request(f"{ENDPOINT}?{urllib.parse.urlencode(q)}", headers={
        "User-Agent": "yado-kuchikomi/0.1", "Referer": ref, "Origin": f"{parts.scheme}://{parts.netloc}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    out = {}
    for h in data.get("hotels", []):
        b = h[0]["hotelBasicInfo"] if isinstance(h, list) else h["hotelBasicInfo"]
        out[str(b["hotelNo"])] = {"image": b.get("hotelImageUrl", ""), "url": b.get("hotelInformationUrl", "")}
    return out


def main():
    nos = hotel_numbers()
    result = {}
    for i in range(0, len(nos), 15):   # 1回に15軒まで
        result.update(fetch(nos[i:i + 15]))
        time.sleep(1)
    today = datetime.datetime.now(JST).date().isoformat()
    for v in result.values():
        v["fetched"] = today
    missing = [n for n in nos if n not in result]
    with open(os.path.join(ROOT, "data", "rakuten.json"), "w", encoding="utf-8") as f:
        json.dump(dict(sorted(result.items(), key=lambda kv: int(kv[0]))), f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(result)}軒の画像を記録" + (f"。見つからない: {missing}" if missing else ""))


if __name__ == "__main__":
    main()
