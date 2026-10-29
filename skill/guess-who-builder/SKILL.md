---
name: guess-who-builder
description: Builds a "Guess Who" icebreaker game about a team from real Slack fun facts, with progressive clues, a flip-down suspect board, scoreboard, timer, host view and per-clue source links. Use when someone wants a team icebreaker, a "guess who" or "who said it" game about coworkers, a fun-facts game for a team meeting or chill hour, or wants to turn Slack intros into a team game.
user_invocable: true
---

# Guess Who Builder

Build a screen-share game where clues about a coworker are revealed one at a time and players guess who it is. The engine (`assets/template.html` + `scripts/build.py`) is finished; the work is gathering good, safe, verifiable facts and turning them into clues.

What makes the game land: clues that are true, specific and a little surprising, ordered from vague to giveaway, and every one traceable to the person's own Slack post. What ruins it: an invented or embellished fact, or a sensitive one. Accuracy and safety beat volume, so it's fine to end up with a short deck.

## 1. Interview

Ask with multiple-choice questions (one round), before searching anything heavy. Search lightly first if it helps make options concrete (for example, look up the person's org in Glean so the pool options name real teams).

- **Pool**: who's in the game. Options: a manager's whole org (resolve with Glean `employee_search` using `reportsto:"Name"`, recursing through sub-managers), just the host's immediate team, the members of a Slack channel, or a list of names the host types.
- **Sources** (multi-select): public social channels and #all-welcome intros; Slack profiles; team channels (non-work banter only). Private channels need explicit consent: ask separately ("Can I search private channels you're in, like #team-random?") and only use `slack_search_public_and_private` after a yes.
- **Photos**: offer Slack profile photos as optional. They need a one-time Chrome setting on the host's Mac (see `references/photos.md`); otherwise the board uses colored initials.
- **Team names**: ask whether there's an official page listing pod or team names (Confluence, a doc). If yes, read it and use those names; otherwise group by manager ("Team NAME").

Leave the host out of the deck, since they're running the game. Tell them up front that the game will contain coworkers' names, photos and quotes, so it should stay private (private artifact, private repo). For very large orgs (over about 100 people), suggest a smaller pool: the game plays better and it exposes less.

Suggest the host give the pool a heads-up before game day ("I'm making a Guess Who from our Slack intros, tell me if you'd rather sit out"). Anyone who opts out is removed from the data entirely, not kept as a decoy.

## 2. Roster

Build the roster from Glean `employee_search` (name, title, email, manager, and the Slack profile link, which carries the user ID when Glean has it). Use each person's preferred name as shown in Glean or Slack. Group people into teams by manager or by the official names from step 1. Save it as working JSON in the same shape the fact-mining output uses (name, slack_id, title, team), leaving slack_id empty where Glean has none.

## 3. Mine Slack for facts

Split the roster into chunks of about 20-25 people and run sub-agents in parallel, each given `references/fact-mining.md` (sources, search patterns, output format) and `references/privacy.md` (what to leave out). One agent per chunk keeps each run within tool budgets and returns a JSON file per chunk. Give each agent the absolute paths of those two files, its roster chunk, an output path in the working folder, and whether private-channel search was approved.

After they finish, read every fact yourself. Drop or fix anything that fails `references/privacy.md`, anything not backed by a quote from that person, and anything about someone else's life. Agents sometimes paraphrase a sentence that also mentions a spouse or kid; keep only the separable part, and trim the stored quote the same way, since the host view shows it.

## 4. Curate clues

For each person, write 2-4 clues ordered vague to specific. The engine appends the team as the final clue automatically.

- First clue should fit several people (a region, a common hobby, a snack opinion); the last should nearly give it away (a named pet, an unusual past job, a talent). Overlaps between people (two people with the same hobby, several in the same city) make the game better, so keep them.
- Use they/their for people, since pronouns usually aren't stated.
- Say only what the quote supports. "Has a pet named Biscuit" stays vague if the species was never given. Use the region, not a small hometown.
- Link each clue to the fact it came from (`cs`: channel and date, permalink, short quote). If a fact came from someone else's post (a contest results post), keep it only if it's harmless and say so to the host.
- Private-channel facts: use them only from channels most players are in (the team's own social channel). The source label shows on the shared screen after the unmask, so keep it to the channel and date.
- People with nothing usable stay on the board as decoys (`c: []`). A single strong clue is fine; the team clue becomes the second.

Write `data.json` in the format in `references/data-format.md`. Then have a sub-agent review it against this skill and `references/privacy.md`: every clue traceable to its quote, nothing sensitive, nothing embellished, order runs vague to specific. Fix what it flags.

Fill any missing permalinks before building (search with the `from:` filter set to the person's Slack user ID in mention form, plus `on:YYYY-MM-DD` and a keyword from the quote). Use links exactly as Slack returns them.

## 5. Photos (optional)

Follow `references/photos.md`. Skip this step cleanly if the host declined, the Chrome setting is locked, or the browser isn't reachable; the game works with initials.

## 6. Build and publish

Work in the user's working folder (resolve the path at runtime; don't assume a folder name) and call this skill's `scripts/build.py` by its absolute path; it finds `assets/template.html` on its own. Photos are only included when you pass `--avatars`.

- Standalone file to share or put in a repo: `python3 SKILL_DIR/scripts/build.py --data data.json --avatars avatars.jpg --out index.html` (omit `--avatars` for initials).
- Claude artifact: build with `--artifact`, publish the output as-is (it's already a finished design; use the icon "game"), then rebuild with `--host-link "ARTIFACT_URL#host"` and publish again to the same file so the Host view button opens the artifact in a new tab.

Check once in a browser (Playwright is fine): the page loads without console errors, Space reveals, Enter unmasks and shows source links, and `#host` with the game code loads the same deck.

## 7. Hand off

Tell the host, briefly:

- How to run it: share the game window; open **Host view** in a second window off-screen. In the same browser it links automatically; anywhere else, type the game code from the top of the game screen and use the arrows to match the suspect number.
- Counts: how many playable people, how many decoys and why, and any judgment calls they should glance at (facts from someone else's post, uncertain wording).
- Ask them to skim the clues once before game day, since these are their coworkers.

Then clean up the working files that hold raw Slack data (chunk JSONs, avatars.json, the downloaded photo grid) unless the host wants to keep them for edits.

## Gotchas

- #all-welcome intro posts only exist for people who joined after the welcome bot started (roughly 2022+), and the earliest ones use a different format ("Welcome NAME! They are joining as..."). Long-tenured people usually need social channels instead.
- Welcome posts can use a legal first name that differs from the name someone goes by. Search the last name too, and always display the preferred name: never put a legal name from a welcome post into the name, a clue or a quote.
- Slack's image server (avatars.slack-edge.com) is blocked from the cloud workspace and the Mac sandbox; only the host's Chrome can reach it.
- A file Chrome downloads can be hardlinked and refuse to stage. Copy it inside a connected folder first, then stage the copy.
- Two windows that don't share browser storage (Claude app panel vs. a browser tab) can't live-sync. The game code is what keeps the host view aligned there, so always mention it.
- The deck order comes from the game code. If `data.json` changes between building the game and opening the host view, rebuild both from the same file.
