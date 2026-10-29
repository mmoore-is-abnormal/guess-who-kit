"""Build a Guess Who game page from template.html + a data file (+ optional photo grid).

Usage:
  python3 build.py                       # data.json -> index.html (initials)
  python3 build.py --avatars avatars.jpg # with the photo grid
  python3 build.py --data my.json --avatars grid.jpg --out game.html
  python3 build.py --artifact --host-link "https://claude.ai/artifact/ID#host" --out page.html

--artifact writes page content without the <!doctype>/<html>/<body> wrapper (for publishing as a
Claude artifact, which adds its own). Without it the output is a standalone file you can double-click.
--host-link sets where the "Host view" button points. Default "#host" (same file, host mode).

The photo grid is a JPEG of square tiles, `cols` wide, in data.json `people` order; each person's
`i` is their tile index. Set `cols`/`rows` in data.json (defaults 10x10). Omit the grid to use initials.
"""
import argparse, base64, json, pathlib

here = pathlib.Path(__file__).parent
ap = argparse.ArgumentParser()
ap.add_argument("--data", default="data.json")
ap.add_argument("--avatars", default=None, help="photo grid JPEG; photos are off unless given")
ap.add_argument("--template", default=str(here / "template.html"))
ap.add_argument("--out", default="index.html")
ap.add_argument("--artifact", action="store_true")
ap.add_argument("--host-link", default="#host")
a = ap.parse_args()

data = json.loads(pathlib.Path(a.data).read_text())
data.setdefault("cols", 10)
data.setdefault("rows", 10)
for k, p in enumerate(data["people"]):
    p.setdefault("c", [])
    p.setdefault("cs", [])
av = pathlib.Path(a.avatars) if a.avatars else None
if av and av.exists():
    data["sprite"] = "data:image/jpeg;base64," + base64.b64encode(av.read_bytes()).decode()
    for k, p in enumerate(data["people"]):
        p.setdefault("i", k)
else:
    data.pop("sprite", None)
    for p in data["people"]:
        p.pop("i", None)

title = (data.get("meta") or {}).get("title", "Guess Who")
page = (pathlib.Path(a.template).read_text()
        .replace("__TITLE__", title)
        .replace("__HOSTLINK__", a.host_link)
        .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
if not a.artifact:
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '</head>\n<body>\n' + page + '\n</body>\n</html>\n')
pathlib.Path(a.out).write_text(page)
playable = sum(1 for p in data["people"] if p.get("c") or p.get("x"))
print(f"wrote {a.out}: {len(page)//1024} KB, {len(data['people'])} on the board, {playable} playable, "
      f"photos {'on' if 'sprite' in data else 'off'}")
