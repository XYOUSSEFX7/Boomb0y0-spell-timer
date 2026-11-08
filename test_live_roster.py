"""اختبارات آلية لميزة "الجدول التلقائي" (Riot Live Client Data API).

بتشتغل من غير شاشة (offscreen) ومن غير نت حقيقي: بنعمل سيرفر HTTP وهمي محلي
وبنقارن النتيجة المتوقعة. مش بنعدل أي حاجة في إعدادات البرنامج الحقيقية.

شغّلها:
    python -m unittest -v test_live_roster
"""
import json
import os
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# لازم قبل إنشاء QApplication عشان الاختبار يشتغل من غير شاشة
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lol_timer as lt                      # noqa: E402
from PyQt6.QtCore import Qt                 # noqa: E402
from PyQt6.QtWidgets import QApplication, QLabel  # noqa: E402


# ----------------------------------------------------------------- بيانات وهمية
def player(champ, pos, team, one, two):
    return {
        "championName": champ,
        "position": pos,
        "team": team,
        "riotId": "{}#EUW".format(champ),
        "summonerName": champ,
        "summonerSpells": {
            "summonerSpellOne": {"displayName": one, "rawDisplayName": one},
            "summonerSpellTwo": {"displayName": two, "rawDisplayName": two},
        },
    }


PLAYERS = [
    # فريقي (ORDER)
    player("Garen", "TOP", "ORDER", "Flash", "Teleport"),
    player("Lee Sin", "JUNGLE", "ORDER", "Flash", "Smite"),
    player("Ahri", "MIDDLE", "ORDER", "Flash", "Ignite"),
    player("Jinx", "BOTTOM", "ORDER", "Flash", "Heal"),
    player("Thresh", "UTILITY", "ORDER", "Flash", "Exhaust"),
    # الخصم (CHAOS) - مربوط بترتيب مختلف عن ترتيب اللين عمدًا
    player("Morgana", "UTILITY", "CHAOS", "Flash", "Mark"),           # Mark مش مدعوم
    player("Caitlyn", "BOTTOM", "CHAOS", "Flash", "Unleashed Teleport"),
    player("Darius", "TOP", "CHAOS", "Flash", "Teleport"),
    player("Vi", "JUNGLE", "CHAOS", "Smite", "Flash"),
    player("Lux", "MIDDLE", "CHAOS", "Flash", "Ignite"),
]
ACTIVE_MINE = {"riotId": "Garen#EUW", "summonerName": "Garen"}

EXPECTED_ENEMY = [
    ("TOP:Darius", "Top Darius", ["Flash", "Teleport"]),
    ("JUNGLE:Vi", "Jng Vi", ["Smite", "Flash"]),
    ("MIDDLE:Lux", "Mid Lux", ["Flash", "Ignite"]),
    ("BOTTOM:Caitlyn", "ADC Caitlyn", ["Flash", "Unleashed TP"]),
    ("UTILITY:Morgana", "Sup Morgana", ["Flash"]),      # Mark اتشال
]


class StubSpeaker:
    def __init__(self):
        self.said = []
        self.closed = False

    def say(self, text):
        self.said.append(text)
        return True

    def close(self):
        self.closed = True


class FakeIcons:
    """بيقلد الأيقونات من غير ملفات ولا نت (بيختبر مسار النص كمان)."""

    def __init__(self):
        self.pix = {}

    def complete(self):
        return True

    def get(self, spell):
        return None


# ----------------------------------------------------------------- الـ API
class TestBuildEnemyRows(unittest.TestCase):
    def test_picks_enemy_team_and_orders_by_lane(self):
        rows = lt.build_enemy_rows(PLAYERS, ACTIVE_MINE)
        self.assertEqual([r["key"] for r in rows], [e[0] for e in EXPECTED_ENEMY])
        self.assertEqual([r["label"] for r in rows], [e[1] for e in EXPECTED_ENEMY])
        self.assertEqual([r["spells"] for r in rows], [e[2] for e in EXPECTED_ENEMY])

    def test_only_enemy_team_is_used(self):
        rows = lt.build_enemy_rows(PLAYERS, ACTIVE_MINE)
        self.assertNotIn("Garen", [r["key"] for r in rows])
        self.assertEqual(len(rows), 5)

    def test_works_when_i_am_on_chaos(self):
        active = {"riotId": "Darius#EUW"}
        rows = lt.build_enemy_rows(PLAYERS, active)
        self.assertEqual(len(rows), 5)
        self.assertIn("TOP:Garen", [r["key"] for r in rows])

    def test_unleashed_teleport_maps_to_unleashed_tp(self):
        row = [r for r in lt.build_enemy_rows(PLAYERS, ACTIVE_MINE)
               if r["key"] == "BOTTOM:Caitlyn"][0]
        self.assertIn("Unleashed TP", row["spells"])

    def test_unknown_spell_is_skipped(self):
        row = [r for r in lt.build_enemy_rows(PLAYERS, ACTIVE_MINE)
               if r["key"] == "UTILITY:Morgana"][0]
        self.assertEqual(row["spells"], ["Flash"])

    def test_duplicate_spells_deduped(self):
        players = [player("Sona", "UTILITY", "CHAOS", "Flash", "Flash"),
                   player("Garen", "TOP", "ORDER", "Flash", "Teleport")]
        rows = lt.build_enemy_rows(players, ACTIVE_MINE)
        self.assertEqual(rows[0]["spells"], ["Flash"])

    def test_tip_has_lane_and_riot_id(self):
        row = lt.build_enemy_rows(PLAYERS, ACTIVE_MINE)[0]
        self.assertEqual(row["tip"], "Top - Darius#EUW")

    def test_unknown_active_player_returns_none(self):
        self.assertIsNone(lt.build_enemy_rows(PLAYERS, {"riotId": "Nobody#EUW"}))
        self.assertIsNone(lt.build_enemy_rows(PLAYERS, {}))

    def test_garbage_input_returns_none(self):
        for bad in (None, [], {}, "nope", [None, 1]):
            self.assertIsNone(lt.build_enemy_rows(bad, ACTIVE_MINE), repr(bad))

    def test_all_players_same_team_returns_none(self):
        only_allies = [p for p in PLAYERS if p["team"] == "ORDER"]
        self.assertIsNone(lt.build_enemy_rows(only_allies, ACTIVE_MINE))


class _Handler(BaseHTTPRequestHandler):
    payloads = {}

    def do_GET(self):
        body = self.payloads.get(self.path)
        if body is None:
            self.send_error(404)
            return
        data = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def start_mock_server():
    """سيرفر بيقلد الـ Live Client Data API. بيرجع (httpd, base_url)."""
    handler = type("Handler", (_Handler,), {"payloads": {
        "/liveclientdata/playerlist": PLAYERS,
        "/liveclientdata/activeplayer": ACTIVE_MINE,
    }})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, "http://127.0.0.1:{}".format(httpd.server_address[1])


def start_json_server(path, payload):
    """سيرفر صغير بيرجّع نفس الـ JSON على المسار المطلوب (لفحص التحديث)."""
    handler = type("Handler", (_Handler,), {"payloads": {path: payload}})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, "http://127.0.0.1:{}{}".format(httpd.server_address[1], path)


class TestLiveGameAPIOverHTTP(unittest.TestCase):
    """اختبار حقيقي عبر HTTP (سيرفر وهمي محلي) مش مجرد مونكي باتش."""

    @classmethod
    def setUpClass(cls):
        cls.httpd, cls.base = start_mock_server()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_fetch_returns_enemy_rows(self):
        rows = lt.LiveGameAPI(self.base).fetch_enemy_rows()
        self.assertEqual([r["key"] for r in rows], [e[0] for e in EXPECTED_ENEMY])
        self.assertEqual([s for r in rows for s in r["spells"]],
                         [s for e in EXPECTED_ENEMY for s in e[2]])

    def test_missing_endpoint_returns_none(self):
        self.assertIsNone(lt.LiveGameAPI(self.base + "/wrong").fetch_enemy_rows())

    def test_server_down_returns_none(self):
        # بورت مقفول: لازم يرجع None بسرعة مش يعلّق البرنامج
        t0 = time.time()
        self.assertIsNone(lt.LiveGameAPI("http://127.0.0.1:1").fetch_enemy_rows())
        self.assertLess(time.time() - t0, 5)

    def test_https_scheme_smoke(self):
        # نفس المسار بتاع اللعبة الحقيقي (https + شهادة محلية): البورت مقفول
        # فالمفروض يرجع None من غير أي استثناء (مش نسيب الشهادة تكسّر الكود).
        self.assertIsNone(lt.LiveGameAPI("https://127.0.0.1:1").fetch_enemy_rows())

    def test_poller_emits_result_on_background_thread(self):
        seen = []
        done = threading.Event()
        poller = lt.LivePoller(self.base, interval_ms=500)
        poller.updated.connect(
            lambda rows: (seen.append(rows), done.set()),
            Qt.ConnectionType.DirectConnection,   # عشان نستلم من الثريد فورًا
        )
        try:
            poller.start()
            self.assertTrue(done.wait(10), "الـ poller مبعتش نتيجة")
        finally:
            poller.stop()
        self.assertEqual([r["key"] for r in seen[0]], [e[0] for e in EXPECTED_ENEMY])


# ----------------------------------------------------------------- الواجهة
class TestOverlayRoster(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        # auto_roster=False عشان الاختبار ما يشغّلش ثريد نت
        self.ov = lt.Overlay({"auto_roster": False}, FakeIcons(), StubSpeaker())
        self.ov.show()
        self.app.processEvents()

    def tearDown(self):
        self.ov.stop_poller()
        self.ov.hide()

    def test_manual_roster_is_default(self):
        self.assertEqual(len(self.ov.rows), len(lt.ROLES))
        self.assertEqual(len(self.ov.slots), sum(len(s) for _, s in lt.ROLES))
        self.assertEqual(len(self.ov.haste_btns), len(lt.ROLES))
        self.assertFalse(self.ov.auto_active)

    def test_live_rows_replace_manual_roster(self):
        rows = lt.build_enemy_rows(PLAYERS, ACTIVE_MINE)
        self.ov.on_live_update(rows)
        self.assertTrue(self.ov.auto_active)
        self.assertEqual(len(self.ov.rows), 5)
        self.assertEqual(len(self.ov.slots), sum(len(e[2]) for e in EXPECTED_ENEMY))
        slot_names = [s.name for s in self.ov.slots]
        self.assertEqual(slot_names, [s for e in EXPECTED_ENEMY for s in e[2]])
        self.assertEqual(sorted(self.ov.haste_btns), sorted(e[0] for e in EXPECTED_ENEMY))
        self.assertIn("5 enemies", self.ov.live_msg)

    def test_label_shows_lane_and_champion(self):
        rows = lt.build_enemy_rows(PLAYERS, ACTIVE_MINE)
        self.ov.on_live_update(rows)
        labels = [
            w.text() for i in range(self.ov.grid.count())
            if isinstance(w := self.ov.grid.itemAt(i).widget(), QLabel)
        ]
        self.assertEqual(labels, [e[1] for e in EXPECTED_ENEMY])

    def test_reverting_to_manual_when_game_ends(self):
        self.ov.on_live_update(lt.build_enemy_rows(PLAYERS, ACTIVE_MINE))
        self.ov.on_live_update(None)
        self.assertFalse(self.ov.auto_active)
        self.assertEqual(len(self.ov.rows), len(lt.ROLES))
        self.assertEqual(len(self.ov.slots), sum(len(s) for _, s in lt.ROLES))
        self.assertIn("not detected", self.ov.live_msg)

    def test_same_rows_do_not_rebuild(self):
        rows = lt.build_enemy_rows(PLAYERS, ACTIVE_MINE)
        self.ov.on_live_update(rows)
        first = self.ov.slots[0]
        self.ov.on_live_update(rows)          # نفس البيانات: المفروض ما يعملش حاجة
        self.assertIs(self.ov.slots[0], first)

    def test_haste_button_cycles(self):
        key = self.ov.rows[0]["key"]
        self.assertEqual(self.ov.haste[key], 0)
        self.ov.cycle_haste(key)
        self.assertEqual(self.ov.haste[key], 12)
        self.assertEqual(self.ov.haste_btns[key].text(), "AH 12")
        for _ in range(3):
            self.ov.cycle_haste(key)
        self.assertEqual(self.ov.haste[key], 0)

    def test_haste_changes_cooldown(self):
        """Flash 300ث مع 18 Ability Haste = 300*100/118 = 254.2ث."""
        key = "TOP:Darius"
        self.ov.on_live_update(lt.build_enemy_rows(PLAYERS, ACTIVE_MINE))
        slot = [s for s in self.ov.slots if s.key == key and s.name == "Flash"][0]
        self.ov.haste[key] = 18
        t0 = time.time()
        slot.start()
        self.assertAlmostEqual(slot.end - t0, 300 * 100 / 118, delta=0.4)

    def test_cooldown_finishes_and_announces(self):
        self.ov.on_live_update(lt.build_enemy_rows(PLAYERS, ACTIVE_MINE))
        self.ov.voice_on = True
        speaker = StubSpeaker()
        self.ov.speaker = speaker
        slot = [s for s in self.ov.slots if s.key == "TOP:Darius" and s.name == "Flash"][0]
        slot.start()
        self.assertIsNotNone(slot.end)
        self.assertEqual(slot._secs, 300)          # Flash من غير Ability Haste
        slot.end = time.time() - 1                 # خلص الكول داون
        slot.tick(time.time())
        self.assertIsNone(slot.end)
        self.assertIn("Darius Flash is back", speaker.said)

    def test_reset_all_clears_every_timer(self):
        self.ov.on_live_update(lt.build_enemy_rows(PLAYERS, ACTIVE_MINE))
        for s in self.ov.slots:
            s.start()
        self.assertTrue(all(s.end is not None for s in self.ov.slots))
        self.ov.reset_all()
        self.assertTrue(all(s.end is None for s in self.ov.slots))

    def test_version_is_shown(self):
        self.assertEqual(self.ov.windowTitle(),
                         "{} v{}".format(lt.APP_NAME, lt.APP_VERSION))
        self.assertEqual(self.ov.panel.ver.text(), "v" + lt.APP_VERSION)

    def test_live_api_base_from_settings(self):
        ov = lt.Overlay({"auto_roster": False, "live_api_base": "http://127.0.0.1:9"},
                        FakeIcons(), StubSpeaker())
        try:
            self.assertEqual(ov.live_base, "http://127.0.0.1:9")
        finally:
            ov.stop_poller()

    def test_size_change_keeps_roster(self):
        self.ov.on_live_update(lt.build_enemy_rows(PLAYERS, ACTIVE_MINE))
        self.ov.change_size(lt.STEP_PX)
        self.assertEqual(len(self.ov.slots), sum(len(e[2]) for e in EXPECTED_ENEMY))
        self.assertTrue(all(s.width() == self.ov.px for s in self.ov.slots))


# ----------------------------------------------------------------- من الآخر للآخر
class TestAutoRosterEndToEnd(unittest.TestCase):
    """ثريد الـ API -> سيجنال -> إعادة بناء الواجهة، كلها مع بعض."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.httpd, cls.base = start_mock_server()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_overlay_autofills_itself_from_live_api(self):
        ov = lt.Overlay({"auto_roster": True, "live_api_base": self.base},
                        FakeIcons(), StubSpeaker())
        try:
            deadline = time.time() + 10
            while time.time() < deadline and not ov.auto_active:
                self.app.processEvents()
                time.sleep(0.05)
            self.assertTrue(ov.auto_active, "الواجهة ملاتش الجدول من الـ API")
            self.assertEqual([r["key"] for r in ov.rows],
                             [e[0] for e in EXPECTED_ENEMY])
            self.assertEqual(len(ov.slots), sum(len(e[2]) for e in EXPECTED_ENEMY))
            self.assertIn("5 enemies", ov.live_msg)
        finally:
            ov.stop_poller()
            ov.hide()


# ----------------------------------------------------------------- الاختصار
class TestHotkeyRegistration(unittest.TestCase):
    def test_mod_norepeat_is_defined(self):
        # كان فيه باگ: الثابت ده كان مستخدم ومش معرّف، فـ register_hotkey
        # كان بيرجع False دايمًا (الاختصار مش بيتسجّل خالص).
        self.assertEqual(lt.MOD_NOREPEAT, 0x4000)

    def test_register_hotkey_does_not_raise(self):
        result = lt.register_hotkey(0, 0)   # 0 = شيل الاختصار
        self.assertIsInstance(result, bool)
        if os.name == "nt":
            self.assertTrue(result)


# ----------------------------------------------------------------- فحص التحديث
class TestUpdateCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_version_tuple(self):
        self.assertEqual(lt.version_tuple("1.2.3"), (1, 2, 3))
        self.assertEqual(lt.version_tuple("v1.10"), (1, 10))
        self.assertEqual(lt.version_tuple(""), (0,))
        self.assertEqual(lt.version_tuple("2.0-beta"), (2, 0))

    def test_is_newer(self):
        self.assertTrue(lt.is_newer("1.1.0", "1.0.2"))
        self.assertTrue(lt.is_newer("2.0", "1.9.9"))
        self.assertFalse(lt.is_newer("1.0.2", "1.0.2"))
        self.assertFalse(lt.is_newer("1.0.0", "1.0.2"))
        self.assertFalse(lt.is_newer("", "1.0.2"))

    def test_fetch_latest_parses_and_fails_safe(self):
        httpd, url = start_json_server(
            "/latest.json", {"version": "9.9.9", "url": "http://x/y"})
        try:
            self.assertEqual(lt.fetch_latest(url)["version"], "9.9.9")
        finally:
            httpd.shutdown()
            httpd.server_close()
        self.assertIsNone(lt.fetch_latest("http://127.0.0.1:1/latest.json"))
        self.assertIsNone(lt.fetch_latest(""))

    def test_checker_emits_when_newer(self):
        httpd, url = start_json_server(
            "/latest.json",
            {"version": "99.0.0", "url": "https://example.com/dl"})
        got = []
        done = threading.Event()
        chk = lt.UpdateChecker(url)
        chk.found.connect(lambda v, u: (got.append((v, u)), done.set()),
                          Qt.ConnectionType.DirectConnection)
        try:
            chk.start()
            self.assertTrue(done.wait(10), "الـ checker مبعتش إشعار")
        finally:
            httpd.shutdown()
            httpd.server_close()
        self.assertEqual(got[0], ("99.0.0", "https://example.com/dl"))

    def test_checker_silent_when_same_version(self):
        httpd, url = start_json_server(
            "/latest.json", {"version": lt.APP_VERSION})
        got = []
        chk = lt.UpdateChecker(url)
        chk.found.connect(lambda v, u: got.append(v),
                          Qt.ConnectionType.DirectConnection)
        try:
            chk.start()
            time.sleep(1.5)
        finally:
            httpd.shutdown()
            httpd.server_close()
        self.assertEqual(got, [])

    def test_panel_shows_update_link_after_notice(self):
        ov = lt.Overlay({"auto_roster": False}, FakeIcons(), StubSpeaker())
        try:
            self.assertTrue(ov.panel.upd.isHidden())
            ov.on_update_found("1.2.0", "https://example.com/dl")
            self.assertEqual(ov.update_version, "1.2.0")
            self.assertIn("1.2.0", ov.panel.upd.text())
            self.assertIn("https://example.com/dl", ov.panel.upd.text())
            self.assertFalse(ov.panel.upd.isHidden())
        finally:
            ov.stop_poller()
            ov.hide()


# ----------------------------------------------------------------- الإعدادات والأصول
class TestSettingsAndAssets(unittest.TestCase):
    def setUp(self):
        self._orig = lt.SETTINGS_FILE
        self.tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "_test_settings.json")
        lt.SETTINGS_FILE = self.tmp

    def tearDown(self):
        lt.SETTINGS_FILE = self._orig
        if os.path.exists(self.tmp):
            os.remove(self.tmp)

    def test_save_load_round_trip_with_auto_roster(self):
        lt.save_settings({"auto_roster": False, "icon_px": 56})
        data = lt.load_settings()
        self.assertEqual(data, {"auto_roster": False, "icon_px": 56})

    def test_broken_settings_file_is_safe(self):
        with open(self.tmp, "w", encoding="utf-8") as f:
            f.write("{not json")
        self.assertEqual(lt.load_settings(), {})

    def test_every_spell_has_icon_key(self):
        for spell in lt.SPELLS:
            self.assertIn(spell, lt.ICON_KEYS, spell)

    def test_api_spell_names_map_to_real_spells(self):
        for display, spell in lt.API_SPELL_NAMES.items():
            self.assertIn(spell, lt.SPELLS, display)

    def test_icon_files_present_on_disk(self):
        missing = [
            key for key in set(lt.ICON_KEYS.values())
            if not any(os.path.exists(os.path.join(d, key + ".png"))
                       for d in (lt.ICON_DIR, lt.BUNDLED_ICON_DIR))
        ]
        self.assertEqual(missing, [], "أيقونات ناقصة: {}".format(missing))


if __name__ == "__main__":
    unittest.main(verbosity=2)
