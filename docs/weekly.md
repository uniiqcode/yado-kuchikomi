# 宿を足す手順（週1回ほど）

1. affiliate-ops で、宿を決めてクチコミを分析し、Threads に投稿する（今までどおり）
2. 人が「サイトに足して」と頼む
3. Claude が `data/yado.json` の最後に1軒を足す
   - `id`: 英数字の短い名前（ページの中の `#id` になる。あとで変えない）
   - `kind`: 「田舎の宿」か「遍路の宿」
   - `marks`: `solo`（一人旅）・`henro`（遍路宿）。だれかと行く宿は空でよい
   - `added`: Threads に投稿した日
   - `rating`: 出所（楽天トラベル・Googleマップ）・評価・件数・見た日
   - `good`（3つ）・`caveat`（1〜2つ）・`winter`・`access`: Threads の投稿と同じ中身（3件以上・2年以内の声）
   - `own`: 人の体験（人が書いたものだけ。無ければ空）
   - `link`: affiliate-ops の台帳の `affiliate_url` をそのまま。楽天に無い宿は空にして、`note` に予約の仕方を書く
4. `python3 -m unittest discover -s tests` と `python3 scripts/build_site.py` で確かめ、PR を作る
5. 人がマージする → GitHub Pages が更新される
