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

## 新しい県のページ（県の候補を調べた時）

1. affiliate-ops で田舎の宿のスキームを回し、候補の CSV（`data/candidates/<日付>_<県>_inaka.csv`）ができる
2. Claude が `data/prefs/<県の英字>.json` を作る: 調べた日、今の段階（`status`）、絞り込みの段（`funnel`。最後の段の数＝候補の数）、地域（`areas`）、候補の宿（名前は楽天の登録名を整える、一言はウェブで確かめた内容を自分の言葉で、評価・件数・夕食は API の値と日付、行き方の印、人のリンクがあれば `link`）
3. `python3 scripts/fetch_images.py` で写真の URL を取る（`data/rakuten.json`）
4. 3軒・1軒が決まったら `status` を書き換え、紹介した宿に `pick`（`data/yado.json` の id）を付ける
5. テスト・ビルド → PR → 人がマージ
