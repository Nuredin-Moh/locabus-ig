import os, json, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone
T=os.environ["IG_TOKEN"]; PAGE="1166149983251207"; V="v21.0"
def g(p,par):
    par=dict(par); par["access_token"]=T
    try: return json.load(urllib.request.urlopen(f"https://graph.facebook.com/{V}/{p}?"+urllib.parse.urlencode(par)))
    except urllib.error.HTTPError as e: return {"_err": e.read().decode()[:160]}
sch=g(f"{PAGE}/scheduled_posts",{"fields":"id,scheduled_publish_time","limit":100})
if "_err" in sch: print("scheduled ERR:",sch["_err"])
else:
    d=sch.get("data",[]); print("PROGRAMMES_RESTANTS:",len(d))
    ts=sorted(x["scheduled_publish_time"] for x in d if x.get("scheduled_publish_time"))
    if ts: print("PROCHAIN_PROGRAMME:",datetime.fromtimestamp(ts[0],timezone.utc).strftime("%d %b %H:%M UTC"))
for edge in ["feed","posts","published_posts"]:
    r=g(f"{PAGE}/{edge}",{"fields":"created_time,message","limit":2})
    if "_err" in r: print(edge,"ERR:",r["_err"][:80])
    else:
        for p in r.get("data",[]): print(edge.upper()+"|",p.get("created_time"),"|",(p.get("message","") or "").replace(chr(10)," ")[:45])
        break
