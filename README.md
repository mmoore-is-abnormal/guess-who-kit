# Guess Who Kit

Build a "Guess Who" icebreaker about your own team. Claude pulls real fun facts from Slack, turns them into clues that go from vague to giveaway, and builds a screen-share game: a flip-down suspect board, a scoreboard, a timer, a private host view with the answers, and a link from every clue to the Slack post it came from.

This repo has no real people in it. `demo/index.html` runs on made-up sample data so you can see how it plays.

## Make your own (with Claude)

1. Download `skill/guess-who-builder.zip`.
2. In Claude (Cowork), go to **Customize → Skills → + Create skill → Upload a skill** and upload the zip.
3. Start a new task and say something like "build a guess who game for my team" (or run `/guess-who-builder`).

Claude will ask:

- **Who's in the game**: a manager's whole org, your immediate team, a Slack channel's members, or a list of names.
- **Where to look**: #all-welcome intros, social channels, Slack profiles, team-channel banter. It asks separately before searching any private channel.
- **Photos**: optional Slack profile pictures (needs a one-time Chrome setting on your Mac; otherwise the board uses initials).
- **Team names**: whether there's an official page with pod or team names to use.

It can also turn on a **new-intel scout**: each time you open the published game, it looks for new Slack posts from people on the board, drafts clues, skips anything already used or overlapping, and holds them for your approval in the host view.

Then it builds the roster from Glean, mines Slack, leaves out anything sensitive (health, family, relationships, religion, politics, money and similar), and publishes the game to you as a private Claude artifact. Skim the clues before game day; they're about your coworkers.

Your finished game contains coworkers' names, photos and quotes. Keep it in a private artifact or a private repo, not this one.

## Play

- **Space** reveals the next clue. Guessing after clue 1 is worth 3 points, clue 2 is 2, later clues 1. The last clue is always the person's team.
- **Enter** unmasks. Each clue then links to its Slack post.
- **→** next suspect. **T** starts or pauses the per-suspect timer (30-90 sec or Off). **G** starts or pauses the game clock (5-20 min or Off), which ends on a Time's up screen with final standings.
- Click tiles to flip people down. **Flip down other teams** clears everyone outside the revealed team.
- **Host view ↗** opens the answers in a second window: keep it off the shared screen. In the same browser it follows the game automatically. Anywhere else, type the **game code** shown at the top of the game screen and use ◀ ▶ to match the suspect number.

## Build by hand

    python3 engine/build.py --data engine/sample-data.json --out index.html

Add `--avatars grid.jpg` for photos, or `--artifact` to output page content for publishing as a Claude artifact. The data format is in `skill/guess-who-builder/references/data-format.md`.

## Layout

    engine/            template.html, build.py, sample-data.json
    demo/index.html    the sample game
    skill/             the guess-who-builder skill (folder and zip)
