#!/usr/bin/env python3
# Publie automatiquement le post Instagram du jour (Locabus) via l'API Graph.
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
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    return json.load(urllib.request.urlopen(url))

# Date du jour (heure de Zurich)
try:
    from zoneinfo import ZoneInfo
    today = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d")
except Exception:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

posts = json.load(open("schedule.json", encoding="utf-8"))
todays = [p for p in posts if p["date"] == today]
if not todays:
    print("Aucun post prevu pour", today); raise SystemExit(0)

p = todays[0]; imgs = p["images"]; cap = p["caption"]
print(f"Jour {p['jour']} - {len(imgs)} image(s) - {today}")

# 1) creer le conteneur
if len(imgs) == 1:
    cid = api_post(f"{IGID}/media", {"image_url": imgs[0], "caption": cap})["id"]
else:
    children = []
    for u in imgs:
        children.append(api_post(f"{IGID}/media", {"image_url": u, "is_carousel_item": "true"})["id"])
        time.sleep(2)
    cid = api_post(f"{IGID}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": cap})["id"]

# 2) attendre que le conteneur soit pret
for _ in range(24):
    st = api_get(cid, {"fields": "status_code"}).get("status_code", "")
    if st == "FINISHED": break
    if st == "ERROR": raise SystemExit("Conteneur en ERREUR")
    time.sleep(5)

# 3) publier
res = api_post(f"{IGID}/media_publish", {"creation_id": cid})
print("Publie sur Instagram:", res)
