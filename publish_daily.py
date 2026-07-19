#!/usr/bin/env python3
# Publie le post Locabus du jour sur Instagram ET Facebook (meme legende, memes images).
# Autonome : tourne dans GitHub Actions, independant de tout ordinateur.
# Idempotent par canal (last.json : {"ig": "YYYY-MM-DD", "fb": "YYYY-MM-DD"}) :
# si un canal a deja publie aujourd'hui il est saute ; l'autre peut quand meme partir/reessayer.
import json, os, time, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone

TOKEN   = os.environ["IG_TOKEN"]           # page access token permanent (sert IG + FB)
IG_ID   = os.environ["IG_USER_ID"]         # instagram business account id
FB_PAGE = os.environ.get("FB_PAGE_ID", "")  # page facebook id (optionnel : si absent, FB saute)
V = "v21.0"
BASE = f"https://graph.facebook.com/{V}/"

def api_post(path, params):
    params = dict(params); params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(BASE + path, data=data)
    try:
        return json.load(urllib.request.urlopen(req)), None
    except urllib.error.HTTPError as e:
        return None, e.read().decode()[:400]

def api_get(path, params):
    params = dict(params); params["access_token"] = TOKEN
    try:
        return json.load(urllib.request.urlopen(BASE + path + "?" + urllib.parse.urlencode(params))), None
    except urllib.error.HTTPError as e:
        return None, e.read().decode()[:400]

try:
    from zoneinfo import ZoneInfo
    today = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d")
except Exception:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

state = {}
if os.path.exists("last.json"):
    try: state = json.load(open("last.json"))
    except Exception: state = {}
# retro-compat ancien format {"last": ...}
if "ig" not in state and "last" in state:
    state = {"ig": state.get("last"), "fb": None}

posts = json.load(open("schedule.json", encoding="utf-8"))
todays = [p for p in posts if p["date"] == today]
if not todays:
    print("Aucun post prevu pour", today); raise SystemExit(0)
p = todays[0]; imgs = p["images"]; cap = p["caption"]
print(f"Jour {p.get('jour','?')} - {len(imgs)} image(s) - {today}")

ok_ig = state.get("ig") == today
ok_fb = state.get("fb") == today
errors = []

# ---------- INSTAGRAM ----------
if ok_ig:
    print("IG: deja publie aujourd'hui, saute.")
else:
    if len(imgs) == 1:
        r, err = api_post(f"{IG_ID}/media", {"image_url": imgs[0], "caption": cap})
        cid = r["id"] if r else None
    else:
        children = []; cid = None; err = None
        for u in imgs:
            r, e = api_post(f"{IG_ID}/media", {"image_url": u, "is_carousel_item": "true"})
            if e: err = e; break
            children.append(r["id"]); time.sleep(2)
        if not err:
            r, err = api_post(f"{IG_ID}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": cap})
            cid = r["id"] if r else None
    if err or not cid:
        errors.append("IG media: " + (err or "pas de creation_id")); print("IG ERREUR:", err)
    else:
        # attendre que le conteneur soit FINISHED
        ready = False
        for _ in range(24):
            r, e = api_get(cid, {"fields": "status_code"})
            st = (r or {}).get("status_code", "")
            if st == "FINISHED": ready = True; break
            if st == "ERROR": break
            time.sleep(5)
        if not ready:
            errors.append("IG conteneur non pret"); print("IG: conteneur non FINISHED")
        else:
            r, err = api_post(f"{IG_ID}/media_publish", {"creation_id": cid})
            if err: errors.append("IG publish: " + err); print("IG ERREUR publish:", err)
            else: state["ig"] = today; print("IG publie:", r)

# ---------- FACEBOOK ----------
if not FB_PAGE:
    print("FB: FB_PAGE_ID absent, canal Facebook ignore.")
elif ok_fb:
    print("FB: deja publie aujourd'hui, saute.")
else:
    if len(imgs) == 1:
        r, err = api_post(f"{FB_PAGE}/photos", {"url": imgs[0], "caption": cap, "published": "true"})
        if err: errors.append("FB photo: " + err); print("FB ERREUR:", err)
        else: state["fb"] = today; print("FB publie:", r)
    else:
        media = []; err = None
        for u in imgs:
            r, e = api_post(f"{FB_PAGE}/photos", {"url": u, "published": "false"})
            if e: err = e; break
            media.append(r["id"]); time.sleep(1)
        if err:
            errors.append("FB upload: " + err); print("FB ERREUR upload:", err)
        else:
            params = {"message": cap}
            for i, mid in enumerate(media):
                params[f"attached_media[{i}]"] = json.dumps({"media_fbid": mid})
            r, err = api_post(f"{FB_PAGE}/feed", params)
            if err: errors.append("FB feed: " + err); print("FB ERREUR feed:", err)
            else: state["fb"] = today; print("FB publie:", r)

json.dump(state, open("last.json", "w"))
if errors:
    raise SystemExit("Echecs: " + " | ".join(errors))
print("OK - IG + FB a jour pour", today)
