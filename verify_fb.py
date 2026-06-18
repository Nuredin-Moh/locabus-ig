import os, json, urllib.request, urllib.parse
T=os.environ["IG_TOKEN"]; PAGE="1166149983251207"; V="v21.0"
def g(p,par): 
    par["access_token"]=T
    return json.load(urllib.request.urlopen(f"https://graph.facebook.com/{V}/{p}?"+urllib.parse.urlencode(par)))
pub=g(f"{PAGE}/feed",{"fields":"id,created_time,message","limit":4})
print("=== DERNIERS POSTS PUBLIES SUR LA PAGE FB ===")
for p in pub.get("data",[]):
    print("PUB|", p.get("created_time"), "|", (p.get("message","") or "").replace(chr(10)," ")[:55])
sch=g(f"{PAGE}/scheduled_posts",{"fields":"id","limit":100})
print("PROGRAMMES_RESTANTS:", len(sch.get("data",[])))
