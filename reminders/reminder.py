#!/usr/bin/env python3
"""CE Bonsai Garden -> Slack reminder planner.

Reads the garden's database dump (one folder per collection, one JSON file per
document, as ArtifactData list writes with out_dir) and prints a JSON plan:
  {"posts": [{"key": ..., "text": ...}], "meta": {...new meta/slack doc...}, "summary": "..."}
It never posts anything itself.

Usage: python3 reminder.py <dump_dir> [--daily HH:MM] [--tz America/New_York] [--url URL] [--now EPOCH_MS]
"""
import json, os, sys, argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HOUR = 3600e3
SPECIES = {
    "juniper": ("Juniper", "Juni"), "maple": ("Japanese maple", "Momiji"), "blackpine": ("Japanese black pine", "Kuro"),
    "sakura": ("Cherry blossom", "Haru"), "wisteria": ("Wisteria", "Fuji"), "ficus": ("Ficus", "Figgy"),
    "neuralnet": ("Neural net", "Neuro"), "phishhook": ("Phish-hook tree", "Hook"), "crystal": ("Crystal tree", "Quartz"),
    "ember": ("Ember tree", "Cinder"), "moonwillow": ("Moonlight willow", "Luna"), "cottoncandy": ("Cotton-candy tree", "Floss"),
    "startree": ("Star tree", "Nova"),
}
MODES = {
    "zen": ("Zen Garden", {"water": 36, "sun": 48, "prune": 96, "feed": 168}, False),
    "greenhouse": ("Greenhouse", {"water": 24, "sun": 36, "prune": 72, "feed": 120}, True),
    "arena": ("Arena", {"water": 36, "sun": 48, "prune": 96, "feed": 168}, False),
}
DUR = {"1h": "1-hour", "4h": "4-hour", "24h": "24-hour", "7d": "7-day"}
NEEDS = ["water", "sun", "prune", "feed"]
WEIGHT = {"water": 0.35, "sun": 0.25, "prune": 0.2, "feed": 0.2}
NEED_WORD = {"water": "water", "sun": "sunlight", "prune": "pruning", "feed": "fertilizer"}
NEED_EMOJI = {"water": ":droplet:", "sun": ":sunny:", "prune": ":scissors:", "feed": ":seedling:"}
STAGES = [(0, "Seed"), (15, "Sprout"), (50, "Seedling"), (120, "Sapling"), (250, "Pre-bonsai"), (450, "Young bonsai"),
          (700, "Shaped bonsai"), (1000, "Mature bonsai"), (1500, "Elder"), (2200, "Ancient"), (3000, "Legendary")]


def load(dump, col):
    out = {}
    d = os.path.join(dump, col)
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.endswith(".json"):
                with open(os.path.join(d, f)) as fh:
                    out[f[:-5]] = json.load(fh)
    return out


def stage_of(pts):
    i = 0
    while i + 1 < len(STAGES) and pts >= STAGES[i + 1][0]:
        i += 1
    return i, STAGES[i][1]


def biz_ms(a, b, tz, weekends=False):
    """Milliseconds between a and b, not counting Saturdays and Sundays in tz (unless the tree counts weekends)."""
    if b <= a:
        return 0
    if weekends:
        return b - a
    t = datetime.fromtimestamp(a / 1000, tz)
    end = datetime.fromtimestamp(b / 1000, tz)
    total = 0.0
    while t < end:
        nxt = (t + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seg_end = min(nxt, end)
        if t.weekday() < 5:
            total += (seg_end - t).total_seconds() * 1000
        t = seg_end
    return total


def tally(poll, ballots):
    tree, mode, tfirst, mfirst, voters = {}, {}, {}, {}, 0
    for b in ballots.values():
        v = (b.get("votes") or {}).get(poll["id"])
        if not v or not (v.get("at", 0) <= poll["closesAt"]):
            continue
        voters += 1
        if v.get("tree") in SPECIES:
            tree[v["tree"]] = tree.get(v["tree"], 0) + 1
            tfirst[v["tree"]] = min(tfirst.get(v["tree"], 1e18), v["at"])
        if v.get("mode") in MODES:
            mode[v["mode"]] = mode.get(v["mode"], 0) + 1
            mfirst[v["mode"]] = min(mfirst.get(v["mode"], 1e18), v["at"])
    top = lambda c, f: sorted(c, key=lambda k: (-c[k], f[k]))[0] if c else None
    return {"tree": tree, "mode": mode, "voters": voters, "treeWin": top(tree, tfirst), "modeWin": top(mode, mfirst)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dump")
    ap.add_argument("--daily", default="10:00")
    ap.add_argument("--tz", default="America/New_York")
    ap.add_argument("--url", default="https://claude.ai/artifact/RL5XhtNbiSULLaMs3nKL8F")
    ap.add_argument("--now", type=float, default=None)
    a = ap.parse_args()
    tz = ZoneInfo(a.tz)
    now = a.now or datetime.now(tz).timestamp() * 1000
    local = datetime.fromtimestamp(now / 1000, tz)
    today = local.strftime("%Y-%m-%d")
    fmt = lambda ms: datetime.fromtimestamp(ms / 1000, tz).strftime("%a %b %-d, %-I:%M %p").replace(":00 ", " ")

    polls = load(a.dump, "polls")
    for k, p in polls.items():
        p["id"] = k
    ballots, carers, seasons_docs = load(a.dump, "ballots"), load(a.dump, "carers"), load(a.dump, "seasons")
    meta = load(a.dump, "meta").get("slack") or {}
    meta = {"lastDaily": meta.get("lastDaily", ""), "lastNudge": meta.get("lastNudge", ""),
            "announced": dict(meta.get("announced") or {}), "closingSoon": dict(meta.get("closingSoon") or {}),
            "winners": dict(meta.get("winners") or {})}

    live = sorted([p for p in polls.values() if p.get("openedAt") and p.get("closesAt") and not p.get("cancelled")], key=lambda p: p["openedAt"])
    seasons, open_poll = [], None
    for p in live:
        if p["closesAt"] <= now:
            t = tally(p, ballots)
            p["_t"] = t
            if t["treeWin"]:
                seasons.append({"id": p["id"], "sp": t["treeWin"], "mode": t["modeWin"] or "zen", "planted": p["closesAt"], "weekends": bool(p.get("weekends")), "poll": p})
        elif open_poll is None or p["closesAt"] < open_poll["closesAt"]:
            open_poll = p
    seasons.sort(key=lambda s: s["planted"])
    for i, s in enumerate(seasons):
        ends = [x for x in [seasons[i + 1]["planted"] if i + 1 < len(seasons) else None, (seasons_docs.get(s["id"]) or {}).get("retiredAt")] if x and x <= now]
        s["retired"] = min(ends) if ends else None

    def derive(s, until):
        label, decay, stakes = MODES[s["mode"]]
        last = {n: s["planted"] - 0.4 * decay[n] * HOUR for n in NEEDS}
        growth, rescuers = 0, []
        doc = seasons_docs.get(s["id"]) or {}
        for uid, c in carers.items():
            md = (c.get("seasons") or {}).get(s["id"])
            if not md:
                continue
            growth += md.get("pts", 0)
            for n in NEEDS:
                last[n] = max(last[n], (md.get("last") or {}).get(n, 0))
            if doc.get("infestedAt") and (md.get("last") or {}).get("rescue", 0) > doc["infestedAt"]:
                rescuers.append(uid)
        wk = s.get("weekends", False)
        levels = {n: max(0.0, min(1.0, 1 - biz_ms(last[n], until, tz, wk) / (decay[n] * HOUR))) for n in NEEDS}
        soggy, drainers = False, 0
        if doc.get("soggyAt"):
            sa, wet, sun_after = doc["soggyAt"], doc["soggyAt"], False
            for c in carers.values():
                l = ((c.get("seasons") or {}).get(s["id"]) or {}).get("last") or {}
                if l.get("drain", 0) > sa:
                    drainers += 1
                wet = max(wet, l.get("water", 0))
                sun_after = sun_after or l.get("sun", 0) > sa
            soggy = drainers < 2 and biz_ms(wet, until, tz, wk) < (12 if sun_after else 24) * HOUR
        if soggy:
            levels["water"] = 1.0
        health = sum(WEIGHT[n] * (0.15 if n == "water" and soggy else levels[n]) for n in NEEDS)
        infested = bool(stakes and doc.get("infestedAt") and len(rescuers) < 3)
        si, sname = stage_of(growth)
        return {"name": doc.get("name") or SPECIES[s["sp"]][1], "species": SPECIES[s["sp"]][0], "mode": label, "stakes": stakes,
                "levels": levels, "health": health, "growth": growth, "stage": si + 1, "stageName": sname,
                "infested": infested, "rescuers": len(rescuers), "pestsLikely": bool(stakes and not infested and health < 0.3),
                "soggy": soggy, "drainers": drainers, "weekends": wk}

    cur = seasons[-1] if seasons and not seasons[-1]["retired"] else None
    d = derive(cur, now) if cur else None
    posts = []

    def leader_line(p):
        t = tally(p, ballots)
        if not t["treeWin"]:
            return "No votes yet."
        return "Leading: *%s* in *%s* mode (%d %s so far)." % (SPECIES[t["treeWin"]][0], MODES[t["modeWin"] or "zen"][0], t["voters"], "vote" if t["voters"] == 1 else "votes")

    # 1. vote results (only for votes that closed in the last 3 days, so old ones are never re-announced)
    for p in live:
        if p["closesAt"] <= now and p["id"] not in meta["winners"] and now - p["closesAt"] < 3 * 24 * HOUR:
            t = p["_t"]
            if t["treeWin"]:
                idx = next(i for i, s in enumerate(seasons) if s["id"] == p["id"])
                prev = seasons[idx - 1] if idx > 0 else None
                text = ":seedling: *The votes are in!* We're growing a *%s* in *%s* mode (%d %s). It was just planted from seed, so come give it its first watering: %s" % (
                    SPECIES[t["treeWin"]][0], MODES[t["modeWin"] or "zen"][0], t["voters"], "voter" if t["voters"] == 1 else "voters", a.url)
                if prev:
                    pd = derive(prev, prev["retired"] or p["closesAt"])
                    text += "\n:trophy: %s the %s retires to the Hall of Fame at %s with %d growth points." % (pd["name"], pd["species"].lower(), pd["stageName"], pd["growth"])
            else:
                text = ":ballot_box_with_ballot: The vote for our next tree closed with no votes, so nothing changed. Anyone can start a new one: %s" % a.url
            posts.append({"key": "winner:" + p["id"], "text": text})
            meta["winners"][p["id"]] = int(now)

    # 2. a vote opened
    if open_poll and open_poll["id"] not in meta["announced"]:
        posts.append({"key": "open:" + open_poll["id"], "text": ":ballot_box_with_ballot: *A %s vote for our next tree is open* until %s ET. Pick a tree and a mode: %s\n%s" % (
            DUR.get(open_poll.get("dur"), "new"), fmt(open_poll["closesAt"]), a.url, leader_line(open_poll))})
        meta["announced"][open_poll["id"]] = int(now)
        if open_poll["closesAt"] - now <= 75 * 60e3:
            meta["closingSoon"][open_poll["id"]] = int(now)  # the opening post already says it closes soon

    # 3. a vote is about to close
    if open_poll and open_poll["id"] not in meta["closingSoon"] and open_poll["closesAt"] - now <= 75 * 60e3:
        mins = max(1, round((open_poll["closesAt"] - now) / 60e3))
        posts.append({"key": "closing:" + open_poll["id"], "text": ":alarm_clock: *Voting closes in about %d minutes* (%s ET). %s Last call: %s" % (mins, fmt(open_poll["closesAt"]), leader_line(open_poll), a.url)})
        meta["closingSoon"][open_poll["id"]] = int(now)

    # 4. daily status (weekdays, at or after the daily time)
    hh, mm = (int(x) for x in a.daily.split(":"))
    workday = local.weekday() < 5 or bool(d and d["weekends"])
    daily_due = workday and (local.hour, local.minute) >= (hh, mm) and meta["lastDaily"] != today
    if daily_due:
        if d:
            low = min(NEEDS, key=lambda n: d["levels"][n])
            status = ("Waterlogged" if d["soggy"] else "Pests!" if d["infested"] else "Wilting" if d["health"] < 0.3 else "Thriving" if d["health"] >= 0.75 else "Content" if d["health"] >= 0.5 else "Needs care")
            text = ":deciduous_tree: *Daily check-in: %s the %s* (%s mode): *%s*, stage %d/11 · %s\n%s" % (
                d["name"], d["species"].lower(), d["mode"], status, d["stage"], d["stageName"],
                "   ".join("%s %d%%" % (NEED_EMOJI[n], round(d["levels"][n] * 100)) for n in NEEDS))
            if d["soggy"]:
                text += "\n:droplet: Waterlogged! %d of 2 teammates have drained the pot. Please don't water it; sunlight helps it dry." % d["drainers"]
            elif d["infested"]:
                text += "\n:bug: Pests! %d of 3 teammates have treated it. Growth is paused until 3 different people do." % d["rescuers"]
            elif d["levels"][low] < 0.5:
                text += "\nIt could really use some %s." % NEED_WORD[low]
            else:
                text += "\nLooking good. Keep it up, team!"
        else:
            text = ":seedling: *The CE Bonsai Garden pot is empty.* Start a vote to pick our next tree."
        if open_poll:
            text += "\n:ballot_box_with_ballot: A vote for the next tree closes %s ET. %s" % (fmt(open_poll["closesAt"]), leader_line(open_poll))
        text += "\n" + a.url
        posts.append({"key": "daily:" + today, "text": text})
        meta["lastDaily"] = today

    # 5. needs-care nudge (at most once a day, and not on top of the daily post)
    if d and meta["lastNudge"] != today and not daily_due and workday and (d["health"] < 0.4 or d["infested"] or d["pestsLikely"] or d["soggy"]):
        low = min(NEEDS, key=lambda n: d["levels"][n])
        if d["soggy"]:
            text = ":droplet: *%s is waterlogged!* Two teammates can drain the pot (%d of 2 so far). Please don't water it: %s" % (d["name"], d["drainers"], a.url)
        elif d["infested"]:
            text = ":bug: *%s has pests!* %d of 3 teammates have treated it. Two minutes is all it takes: %s" % (d["name"], d["rescuers"], a.url)
        else:
            text = ":wilted_flower: *%s needs help.* Health is down to %d%%; it really needs %s. %s" % (d["name"], round(d["health"] * 100), NEED_WORD[low], a.url)
            if d["pestsLikely"]:
                text += "\nPests are likely moving in, so whoever tends it next should treat them."
        posts.append({"key": "nudge:" + today, "text": text})
        meta["lastNudge"] = today
    elif daily_due:
        meta["lastNudge"] = today if d and d["health"] < 0.4 else meta["lastNudge"]

    # keep the bookkeeping small
    for k in ("announced", "closingSoon", "winners"):
        meta[k] = dict(sorted(meta[k].items(), key=lambda kv: kv[1])[-30:])

    summary = ("%s the %s, %s mode, health %d%%" % (d["name"], d["species"], d["mode"], round(d["health"] * 100))) if d else "no tree planted"
    if open_poll:
        summary += "; vote open until " + fmt(open_poll["closesAt"])
    print(json.dumps({"posts": posts, "meta": meta, "summary": summary}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
