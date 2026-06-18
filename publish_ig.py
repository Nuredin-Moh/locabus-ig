#!/usr/bin/env python3
# Publie le post Instagram du jour (Locabus) via l'API Graph. Idempotent (1x/jour max).
import json, os, time, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone

TOKEN = os.environ["IG_TOKEN"]
IGID  = os.environ["IG_USER_ID"]
V = "v21.0"
BASE = f"https://graph.facebook.com/{V}/"

def api_post(path, params):
    params = dict(params); params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(BASE + path, data=data)
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        raise SystemExit("ERREUR API (POST " + path + "): " + e.read().decode()[:500])

def api_get(path, params):
    params = dict(params); params["access_token"] = TOKEN
    return json.load(urllib.request.urlopen(BASE + path + "?" + urllib.parse.urlencode(params)))

try:
    from zoneinfo import ZoneInfo
    today = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d")
except Exception:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# anti-doublon : ne publie qu'une fois par jour
state = {}
if os.path.exists("last.json"):
    try: state = json.load(open("last.json"))
    except Exception: state = {}
if state.get("last") == today:
    print("Deja publie aujourd'hui (" + today + "), rien a faire."); raise SystemExit(0)

posts = json.load(open("schedule.json", encoding="utf-8"))
todays = [p for p in posts if p["date"] == today]
if not todays:
    print("Aucun post prevu pour", today); raise SystemExit(0)

p = todays[0]; imgs = p["images"]; cap = p["caption"]
print(f"Jour {p['jour']} - {len(imgs)} image(s) - {today}")

if len(imgs) == 1:
    cid = api_post(f"{IGID}/media", {"image_url": imgs[0], "caption": cap})["id"]
else:
    children = []
    for u in imgs:
        children.append(api_post(f"{IGID}/media", {"image_url": u, "is_carousel_item": "true"})["id"])
        time.sleep(2)
    cid = api_post(f"{IGID}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": cap})["id"]

for _ in range(24):
    st = api_get(cid, {"fields": "status_code"}).get("status_code", "")
    if st == "FINISHED": break
    if st == "ERROR": raise SystemExit("Conteneur en ERREUR")
    time.sleep(5)

res = api_post(f"{IGID}/media_publish", {"creation_id": cid})
print("Publie sur Instagram:", res)
json.dump({"last": today, "jour": p["jour"]}, open("last.json", "w"))
