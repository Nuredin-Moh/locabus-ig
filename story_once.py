#!/usr/bin/env python3
# Ponctuel : partage en Story (IG + FB) d'une image deja publiee. Fichier a supprimer apres usage.
import json, os, time, urllib.request, urllib.parse, urllib.error
TOKEN=os.environ["IG_TOKEN"]; IG_ID=os.environ["IG_USER_ID"]; FB_PAGE=os.environ.get("FB_PAGE_ID","")
BASE="https://graph.facebook.com/v21.0/"
URL="https://raw.githubusercontent.com/Nuredin-Moh/locabus-ig/main/images/2026-q4/x2711-garagiste-movano/story.jpg"
def post(path,params):
    params=dict(params); params["access_token"]=TOKEN
    try: return json.load(urllib.request.urlopen(urllib.request.Request(BASE+path,data=urllib.parse.urlencode(params).encode()))),None
    except urllib.error.HTTPError as e: return None,e.read().decode()[:400]
def get(path,params):
    params=dict(params); params["access_token"]=TOKEN
    try: return json.load(urllib.request.urlopen(BASE+path+"?"+urllib.parse.urlencode(params))),None
    except urllib.error.HTTPError as e: return None,e.read().decode()[:400]
errs=[]
r,e=post(f"{IG_ID}/media",{"image_url":URL,"media_type":"STORIES"})
if e: errs.append("IG: "+e); print("IG ERREUR",e)
else:
    cid=r["id"]
    for _ in range(24):
        s,_e=get(cid,{"fields":"status_code"})
        if (s or {}).get("status_code")=="FINISHED": break
        time.sleep(5)
    r,e=post(f"{IG_ID}/media_publish",{"creation_id":cid})
    print("IG story:", r or e)
    if e: errs.append("IG publish: "+e)
if FB_PAGE:
    r,e=post(f"{FB_PAGE}/photos",{"url":URL,"published":"false"})
    if e: errs.append("FB upload: "+e); print("FB ERREUR",e)
    else:
        r,e=post(f"{FB_PAGE}/photo_stories",{"photo_id":r["id"]})
        print("FB story:", r or e)
        if e: errs.append("FB story: "+e)
if errs: raise SystemExit(" | ".join(errs))
print("OK stories")
