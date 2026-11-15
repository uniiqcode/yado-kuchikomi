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


if __name__ == "__main__":
    unittest.main()
