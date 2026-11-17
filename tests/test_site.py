"""ネットにつながないテスト: データの形と、作ったページの中身を確かめる。"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_site  # noqa: E402

NEED = ["id", "name", "pref", "area", "kind", "marks", "added", "lead", "rating", "good", "caveat", "access", "link"]
PREF_NEED = ["slug", "pref", "checked", "status", "areas", "funnel", "candidates"]
CAND_NEED = ["hotelNo", "name", "place", "lead", "rating", "access", "link"]


class TestData(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "data", "yado.json"), encoding="utf-8") as f:
            self.items = json.load(f)

    def test_fields(self):
        ids = set()
        for y in self.items:
            for k in NEED:
                self.assertIn(k, y, f'{y.get("id")} に {k} がない')
            self.assertNotIn(y["id"], ids, f'id が重なっている: {y["id"]}')
            ids.add(y["id"])
            self.assertIn(y["kind"], ("田舎の宿", "遍路の宿"))
            for m in y["marks"]:
                self.assertIn(m, build_site.MARKS)

    def test_links_are_rakuten_affiliate(self):
        # リンクは人が楽天アフィリエイトで作ったものだけ（台帳 affiliate-ops/data/ledger.csv と同じもの）
        for y in self.items:
            if y["link"]:
                self.assertTrue(y["link"].startswith("https://hb.afl.rakuten.co.jp/"), y["id"])
            else:
                self.assertTrue(y.get("note"), f'{y["id"]}: リンクが無い宿は note に予約の仕方を書く')


class TestPrefs(unittest.TestCase):
    def test_prefs(self):
        prefs = build_site.load_prefs()
        self.assertTrue(prefs)
        images = build_site.load_images()
        for p in prefs:
            for k in PREF_NEED:
                self.assertIn(k, p, f'{p.get("slug")} に {k} がない')
            nums = [n for n, _ in p["funnel"]]
            self.assertEqual(nums, sorted(nums, reverse=True), f'{p["slug"]}: 絞り込みの数が減っていない')
            self.assertEqual(nums[-1], len(p["candidates"]), f'{p["slug"]}: 最後の段の数と候補の数が違う')
            for c in p["candidates"]:
                for k in CAND_NEED:
                    self.assertIn(k, c, f'{p["slug"]} {c.get("name")} に {k} がない')
                if p["areas"]:
                    self.assertIn(c["area"], p["areas"])
                if c["link"]:
                    self.assertTrue(c["link"].startswith("https://hb.afl.rakuten.co.jp/"))
                self.assertIn(str(c["hotelNo"]), images, f'{c["name"]} の画像が data/rakuten.json にない')

    def test_images_are_rakuten(self):
        for no, v in build_site.load_images().items():
            if v.get("image"):
                self.assertTrue(v["image"].startswith("https://img.travel.rakuten.co.jp/"), no)


class TestBuild(unittest.TestCase):
    def test_page(self):
        out = build_site.build(os.path.join(tempfile.mkdtemp(), "_site"))
        with open(os.path.join(out, "index.html"), encoding="utf-8") as f:
            page = f.read()
        self.assertNotIn("{{", page)
        for y in build_site.load():
            self.assertIn(y["name"], page)          # 宿の名前が HTML に書き込まれている（検索対策）
        self.assertIn("PR（楽天アフィリエイト）", page)
        self.assertIn('rel="canonical" href="https://uniiqcode.com/yado-kuchikomi/"', page)
        self.assertTrue(os.path.exists(os.path.join(out, "sitemap.xml")))
        self.assertTrue(os.path.exists(os.path.join(out, "manifest.webmanifest")))
        self.assertIn("Supported by Rakuten Developers", page)
        self.assertIn("<figcaption>楽天トラベル</figcaption>", page)   # 写真の左下のクレジット
        for p in build_site.load_prefs():
            with open(os.path.join(out, p["slug"], "index.html"), encoding="utf-8") as f:
                sub = f.read()
            self.assertNotIn("{{", sub)
            self.assertIn(f'rel="canonical" href="https://uniiqcode.com/yado-kuchikomi/{p["slug"]}/"', sub)
            for c in p["candidates"]:
                self.assertIn(c["name"], sub)
        self.assertTrue(os.path.exists(os.path.join(out, "henro", "index.html")))


if __name__ == "__main__":
    unittest.main()
