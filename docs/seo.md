# 検索対策（SEO）

2026-11-17。`uniiqcode/claude-skills` の `seo-uniiqcode` スキルの手順に沿って入れた。正式な URL は **https://uniiqcode.com/yado-kuchikomi/**。

| スキルの手順 | 中身 | 場所 |
|---|---|---|
| 1. 正式な URL | `https://uniiqcode.com/yado-kuchikomi/`（canonical・OGP・サイトマップ・構造化データ） | `site/template.html`、`scripts/build_site.py` の `SITE_URL` |
| 2. 中身を HTML に | 宿の一覧（名前・場所・良いところ・注意点・行き方）をビルドの時に HTML に書き込む。絞り込みは JavaScript で出し入れ | `scripts/build_site.py` の `card()` |
| 3. 基本の META | title「宿の口コミ｜クチコミを読んで見つけた田舎の宿・遍路宿」、description（約90文字）、canonical、`lang="ja"`、h1、アイコンの alt・大きさ | `site/template.html` |
| 4. 共有した時の表示 | OGP と X のカード。絵は柿色の中央にアイコン（1200×630、`og.jpg`） | `site/template.html`、`scripts/make_icons.py` |
| 5. サイトマップ | `sitemap.xml`（日付は作った日）。ページを毎日 0:05 に作り直す | `scripts/build_site.py`、`.github/workflows/pages.yml` |
| 6. 構造化データ | `WebSite` と `ItemList`（宿の名前とページの中の `#id`）。宿の評価（★）は自分の評価ではないので `AggregateRating` は使わない | `scripts/build_site.py` の `json_ld` |
| 7. 速さ | 大きな絵は無い。フォントは読み込まない（端末の明朝・ゴシック） | — |

## 公開後に人がすること（スキルの手順8）

1. Google Search Console（`uniiqcode.com` のドメインプロパティは登録済み）で `https://uniiqcode.com/yado-kuchikomi/sitemap.xml` を送信する
2. 「URL 検査」で `https://uniiqcode.com/yado-kuchikomi/` の登録をリクエストする
3. `uniiqcode/uniiqcode.github.io` の `robots.txt` に `Sitemap: https://uniiqcode.com/yado-kuchikomi/sitemap.xml` を1行足す（トップの一覧に足すかは人が決める）

2026-11-18: 1〜3 は済み（サイトマップは「成功しました」・6ページ、トップの登録をリクエスト、robots.txt は uniiqcode.github.io #37）。県のページを足すとサイトマップに自動で入る
