"""Write the JavaScript that stitches Slack profile photos into one grid image in Chrome.

Usage: python3 photo_script.py data.json avatars.json out.js
  data.json    the game data (people order decides tile order)
  avatars.json {"Full Name": {"url": "https://avatars.slack-edge.com/..."}}  (from Slack user search, detailed format)
Run out.js in a Chrome tab that is showing one of the avatar URLs (same origin, so the canvas can export).
It downloads guess-who-avatars.jpg and sets window.__res = {"ok":N,"bad":[indexes]}.
People without a URL get a grey tile; set their `i` anyway so the grid stays aligned, or drop photos for them.
"""
import json, math, sys
data, av, out = sys.argv[1:4]
people = json.load(open(data))["people"]
urls = json.load(open(av))
U = [(urls.get(p["n"]) or {}).get("url") or "" for p in people]
cols = 10
rows = math.ceil(len(U) / cols)
js = f"""(async()=>{{const U={json.dumps(U)};const S=96,C={cols},R={rows};
const cv=document.createElement('canvas');cv.width=S*C;cv.height=S*R;const g=cv.getContext('2d');g.fillStyle='#ccc';g.fillRect(0,0,cv.width,cv.height);
const load=u=>new Promise((res,rej)=>{{const i=new Image();i.onload=()=>res(i);i.onerror=rej;i.src=u;}});
let ok=0,bad=[];
await Promise.all(U.map(async(u,k)=>{{if(!u){{bad.push(k);return;}}let im;try{{im=await load(u.replace('_original.','_192.'));}}catch(e){{try{{im=await load(u);}}catch(e2){{bad.push(k);return;}}}}
const s=Math.min(im.naturalWidth,im.naturalHeight);g.drawImage(im,(im.naturalWidth-s)/2,(im.naturalHeight-s)/2,s,s,(k%C)*S,Math.floor(k/C)*S,S,S);ok++;}}));
const b=await new Promise(r=>cv.toBlob(r,'image/jpeg',0.86));const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='guess-who-avatars.jpg';document.body.appendChild(a);a.click();
window.__res=JSON.stringify({{ok,bad,size:b.size}});}})();'started';"""
open(out, "w").write(js)
print(f"wrote {out}: {len(U)} people, grid {cols}x{rows}. Set data.json cols={cols}, rows={rows}, and each person's i = their index.")
