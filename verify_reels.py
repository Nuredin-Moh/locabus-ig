#!/usr/bin/env python3
import json, os, urllib.request, urllib.parse, urllib.error
TOKEN=os.environ["IG_TOKEN"]; V="v21.0"; BASE=f"https://graph.facebook.com/{V}/"
def g(path, fields):
    try:
        return json.load(urllib.request.urlopen(BASE+path+"?"+urllib.parse.urlencode({"fields":fields,"access_token":TOKEN}),timeout=60))
    except urllib.error.HTTPError as e:
        return {"erreur": e.read().decode()[:300]}
etat=json.load(open("reels_state.json"))
for cle, f in etat.items():
    print("=== ", cle)
    if f.get("fb"):
        print(" FB :", json.dumps(g(f["fb"], "id,permalink_url,status,published,scheduled_publish_time,description,length,thumbnails{uri,is_preferred}"), ensure_ascii=False)[:700])
    if f.get("ig"):
        print(" IG :", json.dumps(g(f["ig"], "id,permalink,media_type,caption,thumbnail_url,timestamp"), ensure_ascii=False)[:500])
