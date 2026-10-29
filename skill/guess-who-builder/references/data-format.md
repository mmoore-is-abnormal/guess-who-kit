# data.json format

`assets/sample-data.json` is a complete working example (fictional people).

    {
      "meta": {
        "title": "Platform Guess Who",          page and tab name
        "eyebrow": "Platform Team · Icebreaker", small line above the big title
        "everyone": "Whole Platform org",        label for the all-people deck
        "slug": "platform",                      storage key; lowercase letters, keeps games separate
        "sources": "Every clue came from a real Slack post (#all-welcome, #platform-random). Unmask to see each clue's source link.",
        "scout": {"server": "Slack", "since": "2026-10-29", "everyHours": 6,
                  "channels": [{"id": "C0123456789", "name": "platform-random"}]}   optional, see below
      },
      "teams": {"core": "Core Pod", "infra": "Infra Pod"},
      "cols": 10, "rows": 4,
      "people": [
        {"n": "Full Name", "t": "core", "ti": "Job title", "i": 0, "sid": "U0123456789",
         "c": ["vague clue", "middle clue", "near-giveaway clue"],
         "cs": [{"s": "#all-welcome 2025-01-06", "u": "https://...slack.com/archives/...", "q": "short verbatim quote"}, ...]}
      ]
    }

- `teams` keys are short ids of lowercase letters a-z only (the game code uses them, so no digits or dashes); their order sets board order and colors (8 colors, then they repeat). Team names show on the board and as the last clue.
- `c` and `cs` line up one-to-one. `c: []` makes the person a board-only decoy.
- `cols`, `rows` and `i` are only needed with photos. `i` is the person's tile in the grid (build.py fills it with the `people` index when missing); `cols`/`rows` must match the grid, and the photo script prints them.
- Keep quotes under about 160 characters; they show in the host view.
- `sid` is the person's Slack user ID. The new-intel scout only uses posts written by someone on the board, matched by this ID.
- `meta.scout` turns on the new-intel scout (Claude artifact only): when an editor opens the game, at most every `everyHours`, it searches the listed channels for posts after the last check (first check starts at `since`, set it to the build date), skips posts already used or seen, has Claude draft clues under the same privacy rules, drops any clue whose quote isn't in the post or that overlaps an existing clue, and saves the rest as pending cards. Nothing joins the deck until an editor approves it in the host view. Leave `scout` out to turn it off.
- The deck is a seeded shuffle of the playable people sorted by name, so the same game code always gives the same order for the same data.
