# 宿の口コミ｜読んで見つけた良いところ

Threads `@yado_kuchikomi` で紹介した宿を、1ページにまとめたサイト。県ごとに宿のクチコミを読んで3軒を選び、「一人で行くならここ」「だれかと行くならここ」を紹介する。四国の遍路宿は、宿を応援したいのでオフシーズンに紹介する。

- 正式な URL: **https://uniiqcode.com/yado-kuchikomi/**（GitHub Pages）
- 運用の本体（宿の選定・クチコミの分析・投稿・台帳）は private リポジトリ `uniiqcode/affiliate-ops`。このリポジトリは公開するページだけ
- 参考にしたもの: `uniiqcode/gyosu-sakaba`（業スー酒場）のつくり

## 方針

| 項目 | 内容 |
|------|------|
| 載せるもの | 宿の名前・場所・印（一人旅・遍路宿）、クチコミを読んでまとめた良いところ・合わない人がいそうな点・冬・行き方、楽天トラベルのリンク（PR） |
| 載せないもの | クチコミの文章、宿の写真（楽天・Google の画像）、料金 |
| 並び | 追加した順（先着順）。将来は県で選べるようにする |
| 更新 | 週1回ほど、人が宿を決めて Threads に投稿した後に、`data/yado.json` に足す PR を作り、人がマージする（自動では集めない） |
| 収益 | 楽天アフィリエイト。ページの上とリンクのそばに「PR（楽天アフィリエイト）」を書く |

## ファイル

| 場所 | 中身 |
|---|---|
| `data/yado.json` | 載せる宿 |
| `scripts/build_site.py` | `data/yado.json` と `site/template.html` から `_site/` を作る（宿の一覧は HTML に書き込む） |
| `scripts/make_icons.py` | `design/logo-source.png` からアイコンと共有用の絵を作る（Pillow が必要） |
| `site/` | ページのひな形・manifest・アイコン |
| `docs/weekly.md` | 宿を足す手順 |
| `docs/seo.md` | 検索対策 |

経緯と決まっていないことは `STATUS.md` を読む。
