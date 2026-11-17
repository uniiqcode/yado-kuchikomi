# 宿の口コミ｜読んで見つけた良いところ

Threads `@yado_kuchikomi` で紹介した宿を、1ページにまとめたサイト。県ごとに宿のクチコミを読んで3軒を選び、「一人で行くならここ」「だれかと行くならここ」を紹介する。四国の遍路宿は、宿を応援したいのでオフシーズンに紹介する。

- 正式な URL: **https://uniiqcode.com/yado-kuchikomi/**（GitHub Pages）
- 運用の本体（宿の選定・クチコミの分析・投稿・台帳）は private リポジトリ `uniiqcode/affiliate-ops`。このリポジトリは公開するページだけ
- 参考にしたもの: `uniiqcode/gyosu-sakaba`（業スー酒場）のつくり

## 方針

| 項目 | 内容 |
|------|------|
| 載せるもの | 宿の名前・場所・印（一人旅・遍路宿）、クチコミを読んでまとめた良いところ・合わない人がいそうな点・冬・行き方、楽天トラベルのリンク（PR）、楽天トラベルの API の宿の写真（左下にクレジット）。県ごとのページには、どうやって探したか（絞り込みの段）と候補の宿 |
| 載せないもの | クチコミの文章、楽天のページからダウンロードした画像・スクリーンショット、Google の画像と点数、料金 |
| 並び | トップの紹介した宿は追加した順（先着順）。県ごとのページ（`/wakayama/` など）と遍路宿のページ（`/henro/`）がある |
| 更新 | 週1回ほど、人が宿を決めて Threads に投稿した後に、`data/yado.json` に足す PR を作り、人がマージする（自動では集めない） |
| 収益 | 楽天アフィリエイト。ページの上とリンクのそばに「PR（楽天アフィリエイト）」を書く |

## ファイル

| 場所 | 中身 |
|---|---|
| `data/yado.json` | 紹介した宿（トップ・遍路宿のページ） |
| `data/prefs/<県>.json` | 県のページ（調べた日・絞り込みの段・候補の宿） |
| `data/rakuten.json` | 宿の写真と楽天トラベルのページの URL（`scripts/fetch_images.py` が API で取る） |
| `scripts/build_site.py` | `data/` から `_site/` を作る（トップ・県のページ・遍路宿のページ。一覧は HTML に書き込む） |
| `scripts/fetch_images.py` | 楽天トラベルの API で宿の写真の URL を取る（キーが要る。Claude が手元で動かして `data/rakuten.json` をコミット） |
| `scripts/make_icons.py` | `design/logo-source.png` からアイコンと共有用の絵を作る（Pillow が必要） |
| `site/` | CSS・JavaScript・manifest・アイコン |
| `docs/weekly.md` | 宿を足す手順 |
| `docs/seo.md` | 検索対策 |

経緯と決まっていないことは `STATUS.md` を読む。
