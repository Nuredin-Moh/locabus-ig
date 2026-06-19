import os, time, json, urllib.request, urllib.parse, urllib.error
TOKEN=os.environ["IG_TOKEN"]; IGID=os.environ["IG_USER_ID"]; PAGE="1166149983251207"
V="v21.0"; BASE=f"https://graph.facebook.com/{V}/"
IMG="https://raw.githubusercontent.com/Nuredin-Moh/locabus-ig/main/images/nouveaute_camera_recul.png"
CAP=("Nouveauté sur notre Opel Movano : il est désormais équipé d'une caméra de recul.\n\n"
     "Manœuvres, créneaux et stationnement deviennent simples et sûrs, même dans les espaces les plus serrés. "
     "Un vrai plus de confort et de sérénité pour vos déménagements et transports.\n\n"
     "Réservez votre van en ligne, 7j/7, sur locabus.ch.\n\n"
     "#Locabus #Moutier #Demenagement #LocationUtilitaire #OpelMovano #CameraDeRecul")
def post(path, params):
    params=dict(params); params["access_token"]=TOKEN
    return json.load(urllib.request.urlopen(urllib.request.Request(BASE+path, data=urllib.parse.urlencode(params).encode())))
def get(path, params):
    params=dict(params); params["access_token"]=TOKEN
    return json.load(urllib.request.urlopen(BASE+path+"?"+urllib.parse.urlencode(params)))
# Instagram
try:
    cid=post(f"{IGID}/media", {"image_url":IMG,"caption":CAP})["id"]
    for _ in range(30):
        st=get(cid,{"fields":"status_code"}).get("status_code","")
        if st=="FINISHED": break
        if st=="ERROR": print("IG_FAIL container ERROR"); break
        time.sleep(5)
    print("IG_OK", post(f"{IGID}/media_publish", {"creation_id":cid}))
except urllib.error.HTTPError as e:
    print("IG_FAIL", e.read().decode()[:600])
# Facebook page
try:
    print("FB_OK", post(f"{PAGE}/photos", {"url":IMG,"caption":CAP,"published":"true"}))
except urllib.error.HTTPError as e:
    print("FB_FAIL", e.read().decode()[:600])
