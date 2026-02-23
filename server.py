import os
os.environ.setdefault("EVENTLET_HUB", "poll")  # macOS kqueue 버그 우회
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import json
from datetime import datetime, timedelta

app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet")

players = {}  # sid -> dict

# ── 메뉴 캐시 ──────────────────────────────────────────
_menu_cache = {}  # key -> (data, expires_at)
_CACHE_TTL = timedelta(hours=1)

# 식당별 데이터 소스 설정
_SOURCES = {
    "r3":      ("welstory", "r3"),
    "r4":      ("welstory", "r4"),
    "r5":      ("welstory", "r5"),
    "together": ("cj",      "6413"),
}

def _fetch_welstory(hall: str, date_str: str):
    """삼성웰스토리 API (R3/R4/R5). date_str = YYYYMMDD"""
    url = "http://www.samsungwelstory.com/menu/getSuwonMenuList.do?"
    try:
        r = requests.post(url, data={
            "sDate": date_str, "dt": date_str,
            "hallNm": hall, "oFlag": "R", "engYn": "N", "sFlag": "",
        }, timeout=10)
        items = r.json()
        meals = {"breakfast": [], "lunch": [], "dinner": []}
        meal_map = {"1": "breakfast", "2": "lunch", "3": "dinner"}
        for item in items:
            # 세트 대표 메뉴(first_row_yn=Y)만 드롭다운에 표시
            if item.get("first_row_yn") != "Y":
                continue
            key = meal_map.get(str(item.get("menu_meal_type", "")))
            name = (item.get("set_menu_name") or item.get("menu_name", "")).strip()
            if key and name:
                meals[key].append(name)
        return meals
    except Exception:
        return None


def _fetch_cj(store_idx: str, date_str: str):
    """CJ프레시밀 API (투게더홀). date_str = YYYYMMDD"""
    url = (
        f"https://front.cjfreshmeal.co.kr/meal/v1/today-all-meal"
        f"?storeIdx={store_idx}&date={date_str}"
    )
    try:
        r = requests.get(url, timeout=10, headers={"Accept": "application/json"})
        raw = r.json().get("data", {})
        meal_map = {"1": "breakfast", "2": "lunch", "3": "dinner"}
        meals = {"breakfast": [], "lunch": [], "dinner": []}
        for cd, entries in raw.items():
            key = meal_map.get(str(cd))
            if key and isinstance(entries, list):
                for entry in entries:
                    name   = entry.get("name", "").strip()
                    corner = entry.get("corner", "").strip()
                    if name:
                        label = f"[{corner}] {name}" if corner else name
                        meals[key].append(label)
        return meals
    except Exception:
        return None


def _get_menu(restaurant: str, date_str: str):
    cache_key = f"{restaurant}:{date_str}"
    now = datetime.now()
    if cache_key in _menu_cache:
        data, exp = _menu_cache[cache_key]
        if now < exp:
            return data

    source = _SOURCES.get(restaurant)
    if not source:
        return None

    kind, param = source
    result = _fetch_welstory(param, date_str) if kind == "welstory" else _fetch_cj(param, date_str)
    if result:
        _menu_cache[cache_key] = (result, now + _CACHE_TTL)
    return result


@app.route("/api/menus")
def api_menus():
    restaurant = request.args.get("restaurant", "").lower()
    date_str   = request.args.get("date", datetime.now().strftime("%Y%m%d"))
    menu = _get_menu(restaurant, date_str)
    if not menu:
        return jsonify({"error": "no data"}), 404
    return jsonify({"restaurant": restaurant, "date": date_str, "meals": menu})


# ── 소켓 이벤트 ─────────────────────────────────────────
def broadcast():
    socketio.emit("player_list", {"players": list(players.values())})


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def on_join(data):
    players[request.sid] = {
        "name": data["name"],
        "emoji": data["emoji"],
        "going": False,
        "meal_time": "regular",
        "meet_time": "11:50",
        "restaurant": "",
        "custom_place": "",
        "menu": "",
    }
    broadcast()


@socketio.on("update")
def on_update(data):
    sid = request.sid
    if sid in players:
        players[sid]["going"]      = data.get("going", False)
        players[sid]["meal_time"]  = data.get("meal_time", "regular")
        players[sid]["meet_time"]  = data.get("meet_time", "11:50")
        players[sid]["restaurant"] = data.get("restaurant", "")
        players[sid]["custom_place"] = data.get("custom_place", "")
        players[sid]["menu"]       = data.get("menu", "")
        broadcast()


@socketio.on("disconnect")
def on_disconnect():
    if request.sid in players:
        del players[request.sid]
        broadcast()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    socketio.run(app, host="0.0.0.0", port=port)
