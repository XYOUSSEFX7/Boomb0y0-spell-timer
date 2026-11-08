"""
Boomb0y0 spell timer  (نسخة PyQt6 - أوفرلاي شفاف حقيقي)

- كليك شمال على الأيقونة: يبدأ الكول داون
- كليك يمين على الأيقونة: قايمة (إلغاء التايمر + تغيير السبيل)
- زرار AH بجنب كل خط: بيلف على 0 / 12 / 18 / 30 (Ability Haste بتاع العدو)
- زرار الإعدادات (الترس فوق على اليمين) فيه كل الباقي:
  الحجم A-/A+ ، Reset ، الصوت ، شفاف/غامق ، Top ، اختصار الإخفاء والإظهار ،
  إخفاء ، خروج
- اختصار الإخفاء/الإظهار: انت اللي بتختار الزرار من الإعدادات
- Ctrl + عجلة الماوس بيكبّر ويصغّر برضو
- اسحب النافذة من اسم الخط أو من العنوان
- أول تشغيل محتاج نت عشان ينزّل الأيقونات (مرة واحدة)
<<<<<<< HEAD
- وانت في ماتش: البرنامج بيقرا بيانات الماتش من الـ Live Client Data API
  (API رسمي من Riot، محلي، مش محتاج مفتاح) ويملأ صفوف الخصوم لوحده:
  التشامبيون + الدور + السبلات بتاعته. لو مفيش ماتش بيفضل الوضع اليدوي.
=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
- محتاج:  pip install PyQt6
"""
import ctypes
import json
import os
<<<<<<< HEAD
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
=======
import subprocess
import sys
import time
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
import urllib.request
from functools import partial

try:
    import winsound
except ImportError:
    winsound = None

from PyQt6.QtCore import (
<<<<<<< HEAD
    QAbstractNativeEventFilter, QObject, QPoint, QPointF, QRectF, QSize, Qt,
    QTimer, pyqtSignal,
=======
    QAbstractNativeEventFilter, QPoint, QPointF, QRectF, QSize, Qt, QTimer,
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
)
from PyQt6.QtGui import (
    QColor, QFont, QGuiApplication, QIcon, QKeySequence, QPainter, QPainterPath,
    QPen, QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QMenu,
    QMessageBox, QPushButton, QSystemTrayIcon, QVBoxLayout, QWidget,
)

APP_NAME = "Boomb0y0 spell timer"
<<<<<<< HEAD
APP_VERSION = "1.0.3"       # ← غيّر الرقم هنا بس عند كل إصدار
=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
SHOW_NAME_LABEL = True      # False لو عايز تشيل الاسم اللي فوق الأيقونات

# الكول داون الأساسي بالثواني (ممكن يتغير مع الباتشات، عدّله هنا)
SPELLS = {
    "Flash": 300,
    "Ignite": 180,
    "Teleport": 360,
    "Unleashed TP": 240,
    "Heal": 240,
    "Barrier": 180,
    "Exhaust": 210,
    "Cleanse": 240,
    "Ghost": 240,
    "Smite": 90,
}

# اسم ملف الأيقونة في Data Dragon (المصدر الرسمي من Riot)
ICON_KEYS = {
    "Flash": "SummonerFlash",
    "Ignite": "SummonerDot",
    "Teleport": "SummonerTeleport",
    "Unleashed TP": "SummonerTeleport",
    "Heal": "SummonerHeal",
    "Barrier": "SummonerBarrier",
    "Exhaust": "SummonerExhaust",
    "Cleanse": "SummonerBoost",
    "Ghost": "SummonerHaste",
    "Smite": "SummonerSmite",
}

# الكلام اللي بيتقال بالصوت
SPELL_SAY = {"Unleashed TP": "Unleashed Teleport"}
ROLE_SAY = {"ADC": "A D C"}

ROLES = [
    ("Top", ["Flash", "Teleport", "Ignite"]),
    ("Jungle", ["Flash", "Smite"]),
    ("Mid", ["Flash", "Ignite"]),
    ("Support", ["Flash", "Exhaust"]),
    ("ADC", ["Flash", "Heal"]),
]

# قيم الـ Ability Haste اللي الزرار بيلف عليها
HASTE_STEPS = [0, 12, 18, 30]

<<<<<<< HEAD
AH_TIP = ("Ability Haste بتاع العدو: 0 / 12 (Ionian Boots) / "
          "18 (Cosmic Insight) / 30 (الاتنين)")

=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
GREEN = "#2e7d32"
RED = "#c62828"
IDLE_BORDER = "#666666"

# أرقام عادية (int) لـ drawText عشان تشتغل مع كل إصدارات PyQt6
ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter.value
ALIGN_CENTER_WRAP = ALIGN_CENTER | Qt.TextFlag.TextWordWrap.value

DEFAULT_PX = 40   # حجم الأيقونة بالبكسل
MIN_PX = 20
MAX_PX = 120
STEP_PX = 4

# ---------------------------------------------------------------- المسارات
# لما يتحول لبرنامج .exe: الإعدادات والكاش بتتحفظ في AppData (مكان ثابت)
# والأيقونات المدمجة جوه الـ exe بتتقرا من هناك
if getattr(sys, "frozen", False):
    APP_DIR = os.path.join(
        os.environ.get("APPDATA", os.path.expanduser("~")), "LoLSpellTimer"
    )
    BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = APP_DIR
try:
    os.makedirs(APP_DIR, exist_ok=True)
except OSError:
    pass
ICON_DIR = os.path.join(APP_DIR, "spell_icons")
BUNDLED_ICON_DIR = os.path.join(BUNDLE_DIR, "spell_icons")
SETTINGS_FILE = os.path.join(APP_DIR, "lol_timer_settings.json")


def load_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_settings(data):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


# ---------------------------------------------------------------- الصوت
class Speaker:
    """صوت بدون تثبيت حاجة: بيستخدم صوت ويندوز الجاهز (System.Speech).
    بيفتح PowerShell واحد في الخلفية مرة واحدة، وكل جملة بتتبعت له فورًا."""

    def __init__(self):
        self.proc = None
        if os.name != "nt":
            return
        script = (
            "Add-Type -AssemblyName System.Speech;"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            "while (($l = [Console]::In.ReadLine()) -ne $null) "
            "{ if ($l) { $s.Speak($l) } }"
        )
        try:
            self.proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", script],
                stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, text=True,
                creationflags=0x08000000,  # من غير نافذة سوداء
            )
        except Exception:
            self.proc = None

    def say(self, text):
        """بترجع True لو الجملة اتبعتت للصوت."""
        if self.proc is not None and self.proc.poll() is None:
            try:
                self.proc.stdin.write(text + "\n")
                self.proc.stdin.flush()
                return True
            except Exception:
                pass
        return False

    def close(self):
        if self.proc is not None:
            try:
                self.proc.terminate()
            except Exception:
                pass


# ---------------------------------------------------------------- الأيقونات
class Icons:
    """بيحمّل أيقونات السبلات (مرة واحدة): من الكاش، أو المدمجة، أو بينزّلها."""

    def __init__(self):
        self.pix = {}
        self._load_all()

    @staticmethod
    def _latest_version():
        try:
            url = "https://ddragon.leagueoflegends.com/api/versions.json"
            with urllib.request.urlopen(url, timeout=6) as r:
                return json.load(r)[0]
        except Exception:
            return None

    @staticmethod
    def _download(version, key, path):
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{key}.png"
        try:
            with urllib.request.urlopen(url, timeout=6) as r:
                data = r.read()
            with open(path, "wb") as f:
                f.write(data)
        except Exception:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def _load_all(self):
        try:
            os.makedirs(ICON_DIR, exist_ok=True)
        except OSError:
            pass
        version = None
        version_checked = False
        for key in set(ICON_KEYS.values()):
            path = None
            for folder in (ICON_DIR, BUNDLED_ICON_DIR):
                p = os.path.join(folder, key + ".png")
                if os.path.exists(p):
                    path = p
                    break
            if path is None:
                if not version_checked:
                    version = self._latest_version()
                    version_checked = True
                if version is None:
                    continue
                path = os.path.join(ICON_DIR, key + ".png")
                self._download(version, key, path)
            if os.path.exists(path):
                pm = QPixmap(path)
                if not pm.isNull():
                    self.pix[key] = pm

    def complete(self):
        return all(k in self.pix for k in ICON_KEYS.values())

    def get(self, spell):
        return self.pix.get(ICON_KEYS.get(spell))


def make_eye_icon(slashed):
    """أيقونة العين: مفتوحة = شفاف، عليها شرطة حمرا = خلفية غامقة."""
    size = 64
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor("white"), 5)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(4, 16, 56, 32))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("white"))
    p.drawEllipse(QPointF(32, 32), 9, 9)
    if slashed:
        pen = QPen(QColor(255, 90, 90), 5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(10, 56), QPointF(54, 8))
    p.end()
    return QIcon(pm)


def make_app_icon():
    """أيقونة البرنامج في شريط المهام (مرسومة بالكود)."""
    pm = QPixmap(64, 64)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#1b1b1b"))
    p.drawRoundedRect(QRectF(2, 2, 60, 60), 14, 14)
    pen = QPen(QColor("#43a047"), 6)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(QRectF(13, 13, 38, 38), 90 * 16, -270 * 16)
    pen = QPen(QColor("white"), 4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawLine(QPointF(32, 32), QPointF(32, 20))
    p.drawLine(QPointF(32, 32), QPointF(42, 32))
    p.end()
    return QIcon(pm)


def make_gear_icon():
    """أيقونة الترس (مرسومة بالكود)."""
    size = 64
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.translate(size / 2, size / 2)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("white"))
    for i in range(8):
        p.save()
        p.rotate(i * 45)
        p.drawRoundedRect(QRectF(-6, -29, 12, 14), 2, 2)
        p.restore()
    p.drawEllipse(QPointF(0, 0), 21, 21)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
    p.drawEllipse(QPointF(0, 0), 9, 9)
    p.end()
    return QIcon(pm)


<<<<<<< HEAD
# ------------------------------------------------- بيانات الماتش الحالي (Riot Live Client Data API)
# الـ API الرسمي من Riot: بيشتغل محلي وانت في ماتش، مش محتاج مفتاح ولا نت.
# بياخد قايمة اللاعبين (تشامبيون + دور + سبلات) ويملأ صفوف الخصوم لوحده.
LIVE_API_BASE = "https://127.0.0.1:2999"
LIVE_POLL_MS = 5000
LIVE_TIMEOUT = 1.5

POSITION_ORDER = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
POSITION_LABEL = {
    "TOP": "Top", "JUNGLE": "Jungle", "MIDDLE": "Mid",
    "BOTTOM": "ADC", "UTILITY": "Support",
}
POSITION_SHORT = {
    "TOP": "Top", "JUNGLE": "Jng", "MIDDLE": "Mid",
    "BOTTOM": "ADC", "UTILITY": "Sup",
}

# اسم السبيل من الـ API (displayName) -> الاسم اللي البرنامج بيستعمله
API_SPELL_NAMES = {
    "flash": "Flash",
    "ignite": "Ignite",
    "teleport": "Teleport",
    "unleashed teleport": "Unleashed TP",
    "heal": "Heal",
    "barrier": "Barrier",
    "exhaust": "Exhaust",
    "cleanse": "Cleanse",
    "ghost": "Ghost",
    "smite": "Smite",
}


def _player_name(p):
    """اسم اللاعب من رد الـ API (riotId أو summonerName) بحروف صغيرة."""
    if not isinstance(p, dict):
        return ""
    return str(p.get("riotId") or p.get("summonerName") or "").strip().lower()


def _my_team(players, active):
    """فريق اللاعب بتاعي (ORDER/CHAOS)، أو None لو مش عارف يتأكد."""
    me = _player_name(active)
    if not me:
        return None
    for p in players:
        if not isinstance(p, dict):
            continue
        name = _player_name(p)
        if not name:
            continue
        if name == me or name.split("#")[0] == me.split("#")[0]:
            team = str(p.get("team") or "").upper()
            if team in ("ORDER", "CHAOS"):
                return team
    return None


def build_enemy_rows(players, active):
    """(دالة نقية) بتحوّل رد الـ API لصفوف الخصوم.
    بترجع None لو البيانات مش كفاية، وفي الحالة دي البرنامج يفضل على الوضع اليدوي."""
    if not isinstance(players, list) or not players:
        return None
    my_team = _my_team(players, active)
    if my_team is None:
        return None
    enemy_team = "CHAOS" if my_team == "ORDER" else "ORDER"
    enemies = [
        p for p in players
        if isinstance(p, dict) and str(p.get("team") or "").upper() == enemy_team
    ]
    if not enemies:
        return None
    enemies.sort(key=lambda p: POSITION_ORDER.index(str(p.get("position") or "").upper())
                 if str(p.get("position") or "").upper() in POSITION_ORDER
                 else len(POSITION_ORDER))
    rows = []
    for p in enemies:
        champ = str(p.get("championName") or "").strip() or "?"
        pos = str(p.get("position") or "").upper()
        spells = []
        ss = p.get("summonerSpells") or {}
        for slot in ("summonerSpellOne", "summonerSpellTwo"):
            display = str((ss.get(slot) or {}).get("displayName") or "").strip().lower()
            mapped = API_SPELL_NAMES.get(display)
            if mapped and mapped in SPELLS and mapped not in spells:
                spells.append(mapped)
        rows.append({
            "key": "{}:{}".format(pos or "?", champ),
            "label": "{} {}".format(POSITION_SHORT.get(pos, ""), champ).strip(),
            "say": champ,
            "tip": "{} - {}".format(
                POSITION_LABEL.get(pos, pos or "?"),
                p.get("riotId") or p.get("summonerName") or "?",
            ),
            "spells": spells,
        })
    return rows


class LiveGameAPI:
    """بيسحب بيانات الماتش الحالي من الـ Live Client Data API (محلي)."""

    def __init__(self, base_url=None):
        self.base = (base_url or LIVE_API_BASE).rstrip("/")

    def _get(self, path):
        # الشهادة محلية وموقعة من Riot نفسه، فبنتخطى التحقق (زي أي أداة رسمية).
        ctx = None
        if self.base.lower().startswith("https"):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            self.base + path, headers={"Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=LIVE_TIMEOUT, context=ctx) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            e.close()       # نقفل الاتصال بدل ما نسيبها معلقة (بنقرا كل 5ث)
            raise

    def fetch_enemy_rows(self):
        """صفوف الخصوم لو فيه ماتش شغال، أو None (مفيش ماتش / اللعبة مقفولة)."""
        try:
            players = self._get("/liveclientdata/playerlist")
        except Exception:
            return None
        try:
            active = self._get("/liveclientdata/activeplayer")
        except Exception:
            active = {}
        return build_enemy_rows(players, active)


class LivePoller(QObject):
    """بيقرا الـ API في ثريد في الخلفية كل شوية (مش بيوقف الواجهة)."""

    updated = pyqtSignal(object)   # list[dict] لو فيه ماتش، أو None

    def __init__(self, base_url=None, interval_ms=LIVE_POLL_MS):
        super().__init__()
        self.api = LiveGameAPI(base_url)
        self.interval = max(500, int(interval_ms)) / 1000.0
        self._stop = threading.Event()
        self._thread = None
        self._last = "<unset>"      # سنتينل عشان أول قراءة توصل حتى لو None

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def poll_once(self):
        """قراءة واحدة متزامنة (بنستخدمها في الاختبارات)."""
        return self.api.fetch_enemy_rows()

    def _run(self):
        while not self._stop.is_set():
            rows = self.api.fetch_enemy_rows()
            if rows != self._last:
                self._last = rows
                try:
                    self.updated.emit(rows)
                except RuntimeError:
                    return          # الأبلكيشن قفل
            self._stop.wait(self.interval)


# ---------------------------------------------------------------- تحديث البرنامج
# فحص بسيط: بيقرا ملف latest.json من جيت هاب ويقارن الأرقام.
# بلّغ بس — مش بينزّل ولا بيستبدل أي ملف (أأمن حاجة، ومفيش أي لمسة للعبة).
UPDATE_MANIFEST_URL = (
    "https://raw.githubusercontent.com/XYOUSSEFX7/"
    "Boomb0y0-spell-timer/main/latest.json"
)
RELEASES_PAGE = "https://github.com/XYOUSSEFX7/Boomb0y0-spell-timer/releases/latest"


def version_tuple(text):
    """'1.2.3' -> (1, 2, 3). أرقام بس، وأي حاجة غريبة بتتجاهل."""
    parts = []
    for chunk in str(text or "").strip().lstrip("vV").split("."):
        digits = ""
        for ch in chunk:
            if ch.isdigit():
                digits += ch
            else:
                break
        parts.append(int(digits) if digits else 0)
    return tuple(parts) or (0,)


def is_newer(remote, local):
    """True لو النسخة اللي على جيت هاب أحدث من اللي عندنا."""
    r, l = version_tuple(remote), version_tuple(local)
    n = max(len(r), len(l))
    return r + (0,) * (n - len(r)) > l + (0,) * (n - len(l))


def fetch_latest(url):
    """بيقرا latest.json ويرجّع dict، أو None لو مفيش لينك / فشل الاتصال."""
    if not url:
        return None
    try:
        req = urllib.request.Request(
            url, headers={"Accept": "application/json",
                          "User-Agent": "Boomb0y0/{}".format(APP_VERSION)}
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


class UpdateChecker(QObject):
    """بيفحص التحديث في ثريد في الخلفية. بيبلّغ بس (مش بينزّل حاجة)."""

    found = pyqtSignal(str, str)   # (رقم النسخة الجديدة، لينك التحميل)

    def __init__(self, url=UPDATE_MANIFEST_URL):
        super().__init__()
        self.url = url

    def start(self):
        if not self.url:
            return
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        data = fetch_latest(self.url)
        if not data:
            return
        ver = str(data.get("version") or "")
        if not ver or not is_newer(ver, APP_VERSION):
            return
        link = str(data.get("url") or RELEASES_PAGE)
        try:
            self.found.emit(ver, link)
        except RuntimeError:
            pass            # الأبلكيشن قفل


# ---------------------------------------------------------------- اختصار الكيبورد
HOTKEY_ID = 1
WM_HOTKEY = 0x0312
MOD_NOREPEAT = 0x4000   # من غير تكرار لو الزرار فضل مضغوط (ويندوز)
=======
# ---------------------------------------------------------------- اختصار الكيبورد
HOTKEY_ID = 1
WM_HOTKEY = 0x0312
MOD_NOREPEAT = 0x4000
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5


class _MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.c_void_p), ("message", ctypes.c_uint),
        ("wParam", ctypes.c_size_t), ("lParam", ctypes.c_ssize_t),
        ("time", ctypes.c_uint), ("pt_x", ctypes.c_long), ("pt_y", ctypes.c_long),
    ]


class HotkeyFilter(QAbstractNativeEventFilter):
    """بيسمع لضغطة الاختصار من ويندوز نفسه (من غير ما يراقب الكيبورد)."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def nativeEventFilter(self, eventType, message):
        try:
            if bytes(eventType) == b"windows_generic_MSG":
                msg = _MSG.from_address(int(message))
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    QTimer.singleShot(0, self.callback)
        except Exception:
            pass
        return False, 0


def register_hotkey(vk, mods):
    """True لو اتسجّل (أو اتشال) بنجاح، False لو الزرار مستخدم في برنامج تاني."""
    if os.name != "nt":
        return False
    try:
        user32 = ctypes.windll.user32
        user32.UnregisterHotKey(None, HOTKEY_ID)
        if not vk:
            return True
        return bool(user32.RegisterHotKey(None, HOTKEY_ID, mods | MOD_NOREPEAT, vk))
    except Exception:
        return False


class HotkeyDialog(QDialog):
    """نافذة صغيرة: اضغط الزرار (أو مجموعة زي Ctrl+F8) اللي عايزه."""

    def __init__(self):
        super().__init__(None, Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(APP_NAME)
        self.picked = None   # (vk, mods, name)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(
            "Press the key you want for Show / Hide\n"
            "(a single key like F8, or a combo like Ctrl+F8).\n\n"
            "Esc = cancel        Delete = remove the hotkey"
        ))

    def keyPressEvent(self, e):
        key = e.key()
        if key == Qt.Key.Key_Escape:
            self.reject()
            return
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt,
                   Qt.Key.Key_Meta, Qt.Key.Key_AltGr):
            return  # استنى الزرار الأساسي
        mods = e.modifiers()
        no_mods = not (mods & (Qt.KeyboardModifier.ControlModifier
                               | Qt.KeyboardModifier.AltModifier
                               | Qt.KeyboardModifier.ShiftModifier
                               | Qt.KeyboardModifier.MetaModifier))
        if key == Qt.Key.Key_Delete and no_mods:
            self.picked = (0, 0, "")
            self.accept()
            return
        vk = e.nativeVirtualKey()
        if not vk:
            return
        m = 0
        names = []
        if mods & Qt.KeyboardModifier.ControlModifier:
            m |= 0x2
            names.append("Ctrl")
        if mods & Qt.KeyboardModifier.AltModifier:
            m |= 0x1
            names.append("Alt")
        if mods & Qt.KeyboardModifier.ShiftModifier:
            m |= 0x4
            names.append("Shift")
        if mods & Qt.KeyboardModifier.MetaModifier:
            m |= 0x8
            names.append("Win")
        names.append(QKeySequence(key).toString() or f"Key {vk}")
        self.picked = (int(vk), m, "+".join(names))
        self.accept()


# ---------------------------------------------------------------- لوحة الإعدادات
PANEL_CSS = """
QFrame#panel { background: #1e1e1e; border: 1px solid #555; }
QLabel { color: #dddddd; font: 12px 'Segoe UI'; }
QLabel#hint { color: #f0a050; }
<<<<<<< HEAD
QLabel#version { color: #888888; font: 11px 'Segoe UI'; }
QLabel#update { color: #7fd17f; font: 12px 'Segoe UI'; }
=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
QPushButton {
    color: white; background: #333333; border: none; border-radius: 4px;
    padding: 5px 10px; font: 12px 'Segoe UI';
}
QPushButton:hover { background: #4a4a4a; }
QPushButton#danger { background: #7a2020; }
QPushButton#danger:hover { background: #a02a2a; }
"""


class SettingsPanel(QFrame):
    """كل الإعدادات في مكان واحد. بتفتح من زرار الترس وبتفضل مفتوحة
    لحد ما تدوس بره."""

    def __init__(self, ov):
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.ov = ov
        self.setObjectName("panel")
        self.setStyleSheet(PANEL_CSS)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(6)

        row = QHBoxLayout()
        row.setSpacing(6)
        row.addWidget(QLabel("Size"))
        row.addWidget(self.btn("A-", lambda: ov.change_size(-STEP_PX)))
        row.addWidget(self.btn("A+", lambda: ov.change_size(STEP_PX)))
        lay.addLayout(row)

        lay.addWidget(self.btn("Reset all timers", ov.reset_all))
<<<<<<< HEAD
        self.auto = self.btn("", ov.toggle_auto_roster)
        lay.addWidget(self.auto)
        self.live = QLabel("")
        self.live.setObjectName("hint")
        self.live.setWordWrap(True)
        self.live.setMaximumWidth(250)
        lay.addWidget(self.live)
=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
        self.voice = self.btn("", ov.toggle_voice)
        lay.addWidget(self.voice)
        self.bg = self.btn("", ov.toggle_solid)
        lay.addWidget(self.bg)
        self.top = self.btn("", ov.toggle_on_top)
        lay.addWidget(self.top)

        row = QHBoxLayout()
        row.setSpacing(6)
        row.addWidget(QLabel("Show / Hide key"))
        self.hk = self.btn("", ov.choose_hotkey)
        row.addWidget(self.hk)
        lay.addLayout(row)
        self.hint = QLabel("")
        self.hint.setObjectName("hint")
        self.hint.setWordWrap(True)
        self.hint.setMaximumWidth(250)
        lay.addWidget(self.hint)

        lay.addWidget(self.btn("Hide now", ov.hide_overlay))
<<<<<<< HEAD
        self.ver = QLabel("")
        self.ver.setObjectName("version")
        lay.addWidget(self.ver)
        self.upd = QLabel("")
        self.upd.setObjectName("update")
        self.upd.setOpenExternalLinks(True)   # اللينك بيفتح في المتصفح
        self.upd.setWordWrap(True)
        self.upd.setMaximumWidth(250)
        lay.addWidget(self.upd)
=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
        quit_btn = self.btn("Exit", ov.close)
        quit_btn.setObjectName("danger")
        lay.addWidget(quit_btn)

    @staticmethod
    def btn(text, callback):
        b = QPushButton(text)
        b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(lambda checked=False, f=callback: f())
        return b

    def refresh(self):
        ov = self.ov
<<<<<<< HEAD
        self.auto.setText("Auto roster: ON" if ov.auto_roster else "Auto roster: OFF")
        self.live.setText(ov.live_msg)
=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
        self.voice.setText("Voice: ON" if ov.voice_on else "Voice: OFF")
        self.bg.setIcon(make_eye_icon(slashed=ov.solid))
        self.bg.setIconSize(QSize(18, 18))
        self.bg.setText("Background: Dark" if ov.solid else "Background: Transparent")
        self.top.setText("Always on top: ON" if ov.on_top else "Always on top: OFF")
        self.hk.setText(ov.hk_name or "Not set")
        if os.name != "nt":
            hint = "The hotkey works on Windows only."
        elif not ov.hk_name:
            hint = "Pick a key to quickly show / hide the overlay while you play."
        elif not ov.hk_ok:
            hint = ("Another app owns this key as a Windows hotkey, "
                    "so key-scan mode is used (it should still work).")
        else:
            hint = ""
        self.hint.setText(hint)
        self.hint.setVisible(bool(hint))
<<<<<<< HEAD
        self.ver.setText("v{}".format(APP_VERSION))
        if ov.update_version:
            self.upd.setText(
                'Update available: v{} — <a href="{}">download</a>'.format(
                    ov.update_version, ov.update_link
                )
            )
            self.upd.setVisible(True)
        else:
            self.upd.setVisible(False)
=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
        self.adjustSize()


# ---------------------------------------------------------------- زرار السبيل
class SpellSlot(QWidget):
<<<<<<< HEAD
    def __init__(self, overlay, key, say, spell):
        super().__init__()
        self.overlay = overlay
        self.key = key        # مفتاح الصف (بيحدد قيم الـ Ability Haste بتاعته)
        self.role = say       # الاسم اللي بيتقال في الصوت
=======
    def __init__(self, overlay, role, spell):
        super().__init__()
        self.overlay = overlay
        self.role = role
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
        self.name = spell
        self.end = None
        self._secs = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_size()

    def apply_size(self):
        self.setFixedSize(self.overlay.px, self.overlay.px)
        self.update()

    # ---------- منطق التايمر
    def start(self):
        base = SPELLS[self.name]
<<<<<<< HEAD
        haste = self.overlay.haste.get(self.key, 0)
=======
        haste = self.overlay.haste.get(self.role, 0)
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
        self.end = time.time() + base * 100 / (100 + haste)
        self.overlay.wake()

    def cancel(self):
        self.end = None
        self.tick(time.time())

    def set_spell(self, spell):
        self.name = spell
        self.end = None
        self._secs = None
        self.update()

    def announce(self):
        """الكول داون خلص: يقول مثلاً (Top Flash is back) أو يعمل بيب."""
        spoken = False
        if self.overlay.voice_on:
            phrase = "{} {} is back".format(
                ROLE_SAY.get(self.role, self.role),
                SPELL_SAY.get(self.name, self.name),
            )
            spoken = self.overlay.speaker.say(phrase)
        if not spoken and winsound:
            try:
                winsound.Beep(1000, 200)
            except Exception:
                pass

    def tick(self, now):
        if self.end is not None and now >= self.end:
            self.end = None
            self.announce()
        secs = None if self.end is None else int(self.end - now + 0.999)
        if secs != self._secs:
            self._secs = secs
            self.update()

    # ---------- الماوس
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.start()
        elif e.button() == Qt.MouseButton.RightButton:
            self.show_menu(e.globalPosition().toPoint())
        e.accept()

    def show_menu(self, pos):
        menu = QMenu(self)
        if self.end is not None:
            menu.addAction("Cancel timer").triggered.connect(
                lambda checked=False: self.cancel()
            )
            menu.addSeparator()
        for sp in SPELLS:
            pm = self.overlay.icons.get(sp)
            act = menu.addAction(QIcon(pm), sp) if pm else menu.addAction(sp)
            act.triggered.connect(
                lambda checked=False, s=sp: self.set_spell(s)
            )
        menu.exec(pos)

    # ---------- الرسم
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        running = self._secs is not None

        path = QPainterPath()
        path.addRoundedRect(r, 6, 6)
        p.setClipPath(path)

        pm = self.overlay.icons.get(self.name)
        font = self.overlay.timer_font
        if pm is not None:
            p.drawPixmap(r, pm, QRectF(pm.rect()))
        else:
            # وضع النص لو الأيقونات مش موجودة
            p.fillRect(r, QColor(RED if running else GREEN))
            if not running:
                p.setPen(QColor("white"))
                small = QFont(font)
                small.setPixelSize(max(8, int(font.pixelSize() * 0.7)))
                p.setFont(small)
                p.drawText(r, ALIGN_CENTER_WRAP, self.name)

        if running:
            p.fillRect(r, QColor(0, 0, 0, 165))
            p.setPen(QColor("white"))
            p.setFont(font)
            m, s = divmod(self._secs, 60)
            p.drawText(r, ALIGN_CENTER, f"{m}:{s:02d}")

        p.setClipping(False)
        pen = QPen(QColor(RED if running else IDLE_BORDER), 2)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 6, 6)


# ---------------------------------------------------------------- النافذة
class Overlay(QWidget):
    def __init__(self, settings, icons, speaker):
        self.on_top = bool(settings.get("on_top", True))
        flags = Qt.WindowType.FramelessWindowHint
        if self.on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        super().__init__(None, flags)

        self.icons = icons
        self.speaker = speaker
        self.voice_on = bool(settings.get("voice", True))
        self.solid = bool(settings.get("solid", False))
        px = settings.get("icon_px", DEFAULT_PX)
        self.px = max(MIN_PX, min(MAX_PX, px)) if isinstance(px, int) else DEFAULT_PX
<<<<<<< HEAD
        self.haste = {}
        # صفوف الخصوم: الوضع اليدوي (ROLES) أو اللي جاي من الـ Live Client API
        self.manual_rows = [
            {"key": role, "label": role, "say": role, "tip": "", "spells": list(spells)}
            for role, spells in ROLES
        ]
        self.rows = list(self.manual_rows)
        self.live_rows = None          # آخر صفوف جاية من الـ API (None = مفيش ماتش)
        self.auto_active = False       # بنعرض صفوف الـ API دلوقتي؟
        self.live_msg = "Live game: not detected (manual roster)"
        self.live_base = settings.get("live_api_base") or LIVE_API_BASE
        self.auto_roster = bool(settings.get("auto_roster", True))
        self.poller = None
        # فحص التحديث: في الـ exe بس (المصدر/الاختبارات مش بيعمل نت)
        self.update_url = settings.get(
            "update_url",
            UPDATE_MANIFEST_URL if getattr(sys, "frozen", False) else "",
        )
        self.update_version = ""       # نسخة أحدث متاحة؟ (فاضية = مفيش)
        self.update_link = RELEASES_PAGE
        self.update_checker = None
        self._drag = None
        self.timer_font = QFont("Segoe UI")

        self.setWindowTitle("{} v{}".format(APP_NAME, APP_VERSION))
=======
        self.haste = {role: 0 for role, _ in ROLES}
        self._drag = None
        self.timer_font = QFont("Segoe UI")

        self.setWindowTitle(APP_NAME)
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
        # شفافية حقيقية لكل بكسل + ما ياخدش تركيز من اللعبة وقت الفتح
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

<<<<<<< HEAD
        # العنوان فوق + جدول الخصوم تحته (الجدول لوحده بنعيد بناءه لما الماتش يتغير)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 6, 8, 6)
        outer.setSpacing(4)

        head = QHBoxLayout()
        head.setSpacing(4)
        if SHOW_NAME_LABEL:
            title = QLabel(APP_NAME)
            title.setObjectName("chip")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            head.addWidget(title, 1)
        else:
            head.addStretch(1)
        self.gear = self.make_btn("", self.toggle_panel, "Settings")
        head.addWidget(self.gear, 0)
        outer.addLayout(head)

        self.roster_box = QWidget(self)
        self.grid = QGridLayout(self.roster_box)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(4)
        self.grid.setVerticalSpacing(4)
        outer.addWidget(self.roster_box)
=======
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(8, 6, 8, 6)
        self.grid.setHorizontalSpacing(4)
        self.grid.setVerticalSpacing(4)
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5

        # اختصار الإخفاء/الإظهار (انت اللي بتختاره من الإعدادات)
        vk = settings.get("hk_vk", 0)
        mods = settings.get("hk_mods", 0)
        self.hk_vk = vk if isinstance(vk, int) else 0
        self.hk_mods = mods if isinstance(mods, int) else 0
        self.hk_name = str(settings.get("hk_name", "")) if self.hk_vk else ""
        self.hk_ok = True
        self.hk_filter = None
        self.overlay_hidden = False

<<<<<<< HEAD
        self.slots = []
        self.haste_btns = {}
        self.rebuild_roster(self.manual_rows)
=======
        # صف العنوان: الاسم + زرار الإعدادات (الترس) على اليمين
        if SHOW_NAME_LABEL:
            title = QLabel(APP_NAME)
            title.setObjectName("chip")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(title, 0, 0, 1, 4)
        self.gear = self.make_btn("", self.toggle_panel, "Settings")
        self.grid.addWidget(self.gear, 0, 4, alignment=Qt.AlignmentFlag.AlignRight)

        self.slots = []
        self.haste_btns = {}
        for i, (role, spells) in enumerate(ROLES):
            lbl = QLabel(role)
            lbl.setObjectName("chip")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setMinimumWidth(64)
            self.grid.addWidget(lbl, i + 1, 0)
            for j, sp in enumerate(spells):
                slot = SpellSlot(self, role, sp)
                self.grid.addWidget(slot, i + 1, 1 + j)
                self.slots.append(slot)
            hb = self.make_btn("AH 0", partial(self.cycle_haste, role),
                               "Ability Haste بتاع العدو: 0 / 12 (Ionian Boots) / "
                               "18 (Cosmic Insight) / 30 (الاتنين)")
            self.haste_btns[role] = hb
            self.grid.addWidget(hb, i + 1, 4)
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5

        # لوحة الإعدادات (بتفتح من الترس)
        self.panel = SettingsPanel(self)
        self._hk_down = False       # الزرار مضغوط دلوقتي؟ (للمسح الدوري)
        self._hk_last = 0.0         # آخر مرة اشتغل فيها الاختصار (منع التكرار)
        self._hk_dialog = False
        if os.name == "nt":
            self.hk_filter = HotkeyFilter(self.trigger_hotkey)
            QApplication.instance().installNativeEventFilter(self.hk_filter)
            if self.hk_vk:
                self.hk_ok = register_hotkey(self.hk_vk, self.hk_mods)
            # طريقة تانية: مسح حالة الزرار كل لحظة. بتشتغل حتى لو اللعبة بتاخد
            # الضغطات قبل ما تعدّي لنظام الاختصارات العادي.
            self.poll_timer = QTimer(self)
            self.poll_timer.timeout.connect(self.poll_hotkey)
            self.poll_timer.start(60)

        # أيقونة جنب الساعة (زي سبوتيفاي): كليك شمال = إخفاء/إظهار، كليك يمين = قايمة
        self.tray = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = QSystemTrayIcon(make_app_icon(), self)
            self.tray.setToolTip(APP_NAME)
            self.tray_menu = QMenu()
            self.tray_menu.addAction("Show / Hide").triggered.connect(
                lambda checked=False: self.toggle_visible())
            self.tray_menu.addAction("Exit").triggered.connect(
                lambda checked=False: self.close())
            self.tray.setContextMenu(self.tray_menu)
            self.tray.activated.connect(self.on_tray)
            self.tray.show()

        self.restyle()
        self.update_gear_icon()
        self.panel.refresh()
        self.adjustSize()
        self.restore_position(settings)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

        # بعد ما النافذة تظهر: رجّعها لشريط المهام والـ Alt+Tab
        QTimer.singleShot(150, self.setup_taskbar)

<<<<<<< HEAD
        # قارئ بيانات الماتش (Live Client API) في الخلفية
        if self.auto_roster:
            self.start_poller()

        # فحص التحديث (بلّغ بس - مفيش تحميل ولا استبدال)
        if self.update_url:
            self.update_checker = UpdateChecker(self.update_url)
            self.update_checker.found.connect(self.on_update_found)
            self.update_checker.start()

    # ---------- بيانات الماتش الحالي (Live Client API)
    def start_poller(self):
        if self.poller is None:
            self.poller = LivePoller(self.live_base)
            self.poller.updated.connect(self.on_live_update)
        self.poller.start()

    def stop_poller(self):
        if self.poller is not None:
            self.poller.stop()
            self.poller = None

    def on_live_update(self, rows):
        """بيتنده من ثريد الـ API: إما صفوف خصوم جديدة، أو None (مفيش ماتش)."""
        rows = rows or None
        if rows == self.live_rows:
            return
        self.live_rows = rows
        if rows:
            self.auto_active = True
            self.live_msg = "Live game: {} enemies auto-loaded".format(len(rows))
            self.rebuild_roster(rows)
        else:
            self.live_msg = "Live game: not detected (manual roster)"
            if self.auto_active:
                self.auto_active = False
                self.rebuild_roster(self.manual_rows)
        self.panel.refresh()
        self.adjustSize()

    def toggle_auto_roster(self):
        self.auto_roster = not self.auto_roster
        if self.auto_roster:
            self.start_poller()
        else:
            self.stop_poller()
            self.on_live_update(None)
        self.save_state()
        self.panel.refresh()

    def on_update_found(self, version, link):
        """في نسخة أحدث على جيت هاب: نعرضها في الإعدادات + رسالة صغيرة جنب الساعة."""
        self.update_version = version
        self.update_link = link or RELEASES_PAGE
        self.panel.refresh()
        if self.tray is not None:
            try:
                self.tray.showMessage(
                    APP_NAME, "New version v{} is available".format(version)
                )
            except Exception:
                pass

    def rebuild_roster(self, rows):
        """(إعادة) بناء صفوف الخصوم: الاسم + أيقونات السبلات + زرار الـ Ability Haste."""
        self.rows = list(rows)
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.hide()
                w.setParent(None)
                w.deleteLater()
        self.slots = []
        self.haste_btns = {}
        max_spells = max([len(r["spells"]) for r in self.rows] + [1])
        for i, row in enumerate(self.rows):
            key = row["key"]
            self.haste.setdefault(key, 0)
            lbl = QLabel(row["label"])
            lbl.setObjectName("chip")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setMinimumWidth(64)
            if row.get("tip"):
                lbl.setToolTip(row["tip"])
            self.grid.addWidget(lbl, i, 0)
            for j, sp in enumerate(row["spells"]):
                slot = SpellSlot(self, key, row["say"], sp)
                self.grid.addWidget(slot, i, 1 + j)
                self.slots.append(slot)
            hb = self.make_btn("AH {}".format(self.haste[key]),
                               partial(self.cycle_haste, key), AH_TIP)
            self.haste_btns[key] = hb
            self.grid.addWidget(hb, i, 1 + max_spells)

=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
    # ---------- بناء الواجهة
    def make_btn(self, text, callback, tip=None):
        b = QPushButton(text)
        b.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # ما ياخدش تركيز الكيبورد
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(lambda checked=False, f=callback: f())
        if tip:
            b.setToolTip(tip)
        return b

    def restyle(self):
        """بيظبط الخطوط والستايل على حسب الحجم الحالي."""
        px = self.px
        timer = max(10, int(px * 0.30))
        label = max(11, int(px * 0.32))
        small = max(10, int(px * 0.27))
        self.timer_font = QFont("Segoe UI")
        self.timer_font.setPixelSize(timer)
        self.timer_font.setBold(True)
        self.setStyleSheet(f"""
            QLabel#chip {{
                color: white; background: rgba(0,0,0,150);
                border-radius: 5px; padding: 2px 6px;
                font: bold {label}px 'Segoe UI';
            }}
            QFrame#bar {{ background: rgba(0,0,0,150); border-radius: 6px; }}
            QPushButton {{
                color: white; background: rgba(34,34,34,225);
                border: none; border-radius: 4px; padding: 2px 6px;
                font: {small}px 'Segoe UI';
            }}
            QPushButton:hover {{ background: rgba(75,75,75,240); }}
            QToolTip {{ color: white; background: #222; border: 1px solid #555; }}
        """)

    def restore_position(self, settings):
        x, y = settings.get("x"), settings.get("y")
        if isinstance(x, int) and isinstance(y, int):
            for scr in QGuiApplication.screens():
                if scr.availableGeometry().contains(QPoint(x + 20, y + 20)):
                    self.move(x, y)
                    return
        scr = QGuiApplication.primaryScreen()
        if scr is not None:
            g = scr.availableGeometry()
            self.move(g.right() - self.width() - 20, g.top() + 120)

    # ---------- نافذة ويندوز: شريط المهام + Top
    def apply_window_mode(self):
        """Top ON  : فوق اللعبة + بدون تركيز (NOACTIVATE) + يظهر في شريط المهام.
        Top OFF : نافذة عادية تتفعّل وتتخبى ورا زي أي برنامج."""
        if os.name != "nt":
            return
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = int(self.winId())
            GWL_EXSTYLE = -20
            ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ex = (ex & ~0x00000080) | 0x00040000      # شيل TOOLWINDOW وحط APPWINDOW
            if self.on_top:
                ex |= 0x08000000                       # NOACTIVATE
            else:
                ex &= ~0x08000000
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex)
            # SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED
            user32.SetWindowPos(hwnd, -1 if self.on_top else -2,
                                0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x0020)
        except Exception:
            pass

    def setup_taskbar(self):
        self.apply_window_mode()
        # إخفاء وإظهار سريع عشان ويندوز يحدّث شريط المهام
        self.hide()
        QTimer.singleShot(40, self.show)

    # ---------- التايمرات
    def tick(self):
        now = time.time()
        busy = False
        for s in self.slots:
            s.tick(now)
            if s.end is not None:
                busy = True
        # لما مفيش تايمر شغال بيفحص كل ثانية بس (أخف على الجهاز)
        self.timer.setInterval(250 if busy else 1000)

    def wake(self):
        self.timer.setInterval(250)
        self.tick()

    def reset_all(self):
        for s in self.slots:
            s.cancel()

    # ---------- الأزرار
<<<<<<< HEAD
    def cycle_haste(self, key):
        cur = self.haste.get(key, 0)
        nxt = HASTE_STEPS[(HASTE_STEPS.index(cur) + 1) % len(HASTE_STEPS)] \
            if cur in HASTE_STEPS else 0
        self.haste[key] = nxt
        self.haste_btns[key].setText(f"AH {nxt}")
=======
    def cycle_haste(self, role):
        cur = self.haste.get(role, 0)
        nxt = HASTE_STEPS[(HASTE_STEPS.index(cur) + 1) % len(HASTE_STEPS)] \
            if cur in HASTE_STEPS else 0
        self.haste[role] = nxt
        self.haste_btns[role].setText(f"AH {nxt}")
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5

    def change_size(self, delta):
        new = max(MIN_PX, min(MAX_PX, self.px + delta))
        if new == self.px:
            return
        self.px = new
        self.restyle()
        for s in self.slots:
            s.apply_size()
        self.update_gear_icon()
        self.grid.activate()
        self.adjustSize()

    def update_voice_btn(self):
        self.panel.refresh()

    def toggle_voice(self):
        self.voice_on = not self.voice_on
        self.update_voice_btn()
        if self.voice_on:
            self.speaker.say("Voice on")  # تجربة سريعة للصوت

    def update_eye_icon(self):
        self.panel.refresh()

    def update_gear_icon(self):
        h = max(14, int(self.px * 0.30) + 4)
        self.gear.setIcon(make_gear_icon())
        self.gear.setIconSize(QSize(h, h))

    def toggle_solid(self):
        self.solid = not self.solid
        self.update_eye_icon()
        self.update()

    def update_top_btn(self):
        self.panel.refresh()

    def toggle_on_top(self):
        self.on_top = not self.on_top
        self.apply_window_mode()
        self.update_top_btn()

    # ---------- لوحة الإعدادات + الإخفاء/الإظهار + الاختصار
    def toggle_panel(self):
        if self.panel.isVisible():
            self.panel.hide()
            return
        self.panel.refresh()
        h, w = self.panel.height(), self.panel.width()
        gpos = self.gear.mapToGlobal(QPoint(0, self.gear.height() + 4))
        scr = QGuiApplication.screenAt(gpos) or QGuiApplication.primaryScreen()
        x, y = gpos.x() + self.gear.width() - w, gpos.y()
        if scr is not None:
            g = scr.availableGeometry()
            x = max(g.left(), min(x, g.right() - w))
            if y + h > g.bottom():   # مفيش مكان تحت: افتحها فوق الترس
                y = self.gear.mapToGlobal(QPoint(0, 0)).y() - h - 4
            y = max(g.top(), y)
        self.panel.move(x, y)
        self.panel.show()

    def toggle_visible(self):
        """إخفاء/إظهار البرنامج بالكامل (من غير ما ياخد تركيز من اللعبة).
        وهو مخفي اللعبة بترجع لسرعتها الكاملة. لو نسيت الاختصار: أيقونة
        البرنامج جنب الساعة (System Tray) بترجّعه."""
        # لازم نستخدم hide/show بتوع Qt نفسه. لو أخفينا النافذة بـ ويندوز مباشرة،
        # Qt بيفضل شايفها ظاهرة، وبعد الإظهار بتطلع فاضية (شفافة بالكامل).
        if self.overlay_hidden:
            self.show()                 # بيظهرها من غير ما ياخد تركيز
            self.overlay_hidden = False
            self.update()
            self.force_top()
            # تأكيد بعد لحظة عشان اللعبة ما تغطيش عليها
            QTimer.singleShot(120, self.reassert_top)
            QTimer.singleShot(600, self.reassert_top)
        else:
            self.hide()
            self.overlay_hidden = True

    def force_top(self):
        """نزّلها من الـ topmost وارفعها تاني عشان تبقى فعلًا فوق كل النوافذ."""
        if os.name == "nt" and self.on_top:
            try:
                u = ctypes.windll.user32
                # SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
                u.SetWindowPos(int(self.winId()), -2, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)
            except Exception:
                pass
        self.apply_window_mode()

    def reassert_top(self):
        if not self.overlay_hidden:
            self.apply_window_mode()

    def on_tray(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visible()

    def trigger_hotkey(self):
        """بيتنده من الطريقتين (نظام الاختصارات + المسح الدوري). لو الاتنين
        اشتغلوا مع بعض بيتحسب مرة واحدة بس."""
        now = time.time()
        if now - self._hk_last < 0.35:
            return
        self._hk_last = now
        self.toggle_visible()

    def poll_hotkey(self):
        """بيسأل ويندوز كل 60 جزء من الثانية: الزرار مضغوط ولا لأ؟"""
        if not self.hk_vk or self._hk_dialog:
            self._hk_down = False
            return
        try:
            u = ctypes.windll.user32
            down = bool(u.GetAsyncKeyState(self.hk_vk) & 0x8000)
            if down:
                # لازم الـ Ctrl / Alt / Shift يطابقوا اللي اخترته بالظبط
                for flag, vk in ((0x2, 0x11), (0x1, 0x12), (0x4, 0x10)):
                    want = bool(self.hk_mods & flag)
                    have = bool(u.GetAsyncKeyState(vk) & 0x8000)
                    if want != have:
                        down = False
                        break
            if down and (self.hk_mods & 0x8):
                win = (u.GetAsyncKeyState(0x5B) | u.GetAsyncKeyState(0x5C)) & 0x8000
                down = bool(win)
        except Exception:
            return
        if down and not self._hk_down:
            self.trigger_hotkey()
        self._hk_down = down

    def hide_overlay(self):
        self.panel.hide()
        self.toggle_visible()

    def choose_hotkey(self):
        self.panel.hide()
        self._hk_dialog = True      # وقّف المسح وانت بتختار
        dlg = HotkeyDialog()
        ok = dlg.exec() == QDialog.DialogCode.Accepted
        self._hk_dialog = False
        if ok and dlg.picked is not None:
            self.apply_hotkey(*dlg.picked)

    def apply_hotkey(self, vk, mods, name):
        self.hk_vk, self.hk_mods, self.hk_name = vk, mods, name
        self.hk_ok = register_hotkey(vk, mods)
        self._hk_down = True        # الزرار لسه مضغوط من الاختيار: ما يتحسبش ضغطة
        self.save_state()
        self.panel.refresh()

    # ---------- الرسم + السحب + عجلة الماوس
    def paintEvent(self, e):
        if self.solid:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(20, 20, 20, 235))
            p.drawRoundedRect(QRectF(self.rect()), 10, 10)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag is not None and (e.buttons() & Qt.MouseButton.LeftButton):
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None

    def wheelEvent(self, e):
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            d = e.angleDelta().y()
            if d:
                self.change_size(STEP_PX if d > 0 else -STEP_PX)
            e.accept()
        else:
            e.ignore()

    # ---------- الحفظ والإغلاق
    def save_state(self):
        save_settings({
            "icon_px": self.px,
            "voice": self.voice_on,
            "solid": self.solid,
            "on_top": self.on_top,
<<<<<<< HEAD
            "auto_roster": self.auto_roster,
=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
            "hk_vk": self.hk_vk,
            "hk_mods": self.hk_mods,
            "hk_name": self.hk_name,
            "x": self.x(),
            "y": self.y(),
        })

    def closeEvent(self, e):
        self.save_state()
<<<<<<< HEAD
        self.stop_poller()
=======
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
        self.panel.hide()
        if self.tray is not None:
            self.tray.hide()
        register_hotkey(0, 0)   # شيل الاختصار من ويندوز
        self.speaker.close()
        e.accept()
        QApplication.quit()


def boost_priority():
    """أولوية أعلى من العادي شوية. البرنامج خفيف وبينام أغلب الوقت، فمش هيأثر
    على اللعبة. لكن لو الأولوية قليلة واللعبة واخدة المعالج كله (وهي مخفية
    بتشتغل بأقصى سرعة)، الاختصار والصوت بيتأخروا ويبان إنهم مش شغالين."""
    try:
        k = ctypes.windll.kernel32
        k.SetPriorityClass(k.GetCurrentProcess(), 0x00008000)  # ABOVE_NORMAL
    except Exception:
        pass


def main():
    boost_priority()
    if os.name == "nt":
        try:
            import ctypes
            # أيقونة وتجميع مستقلين في شريط المهام (مش مع Python)
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "Boomb0y0.SpellTimer")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # بنقفل بنفسنا من closeEvent
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(make_app_icon())

    settings = load_settings()
    icons = Icons()
    speaker = Speaker()

    if not icons.complete():
        QMessageBox.warning(
            None, APP_NAME,
            "Could not download the spell icons.\n"
            "Check your internet and restart.\n\n"
            "Running in text mode for now.",
        )

    win = Overlay(settings, icons, speaker)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
