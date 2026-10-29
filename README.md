# Team Bonsai Garden

A shared bonsai the CE team grows together. Everyone waters, gives sunlight, prunes and feeds the same trees, and they grow from a seed to a Legendary bonsai over weeks of team care.

![The welcome screen and vote](docs/welcome.png)

The project has three parts:

| | Where it runs | Status |
|---|---|---|
| [`web/`](web/) | A shared page on claude.ai (Claude Artifact with a shared database) | Live |
| [`slack-app/`](slack-app/) | A Slack app: `/bonsai` posts the tree with care buttons (earlier three-pot design) | Needs Slack admin approval and a host |
| [`reminders/`](reminders/) | Plans the daily Slack reminders and vote alerts | Runs as a scheduled Claude task |

The web page and the Slack app keep separate data.

## How it works

The team grows **one tree at a time**.

1. **Vote.** Anyone can start a vote on the Welcome screen and choose how long it stays open: 1 hour, 4 hours, 24 hours or 7 days. Everyone picks a tree and a mode, and the top tree and top mode win (ties go to whichever got there first).
2. **Plant.** When the vote closes, the winner is planted from seed. The species is locked until the next vote; the old tree retires to the **Hall of Fame** with its final stage and top caretakers.
3. **Tend.** Everyone waters, gives sunlight, prunes and feeds it. Needs drain over time. Whoever starts a vote picks whether the next tree's needs pause on weekends or keep draining every day. Cooldowns: water and sun every 4 hours per person, prune every 12, feed once a day. Tending a need that's running low earns the most growth.
4. **Talk to it.** "Talk to the tree" is always available in every mode and earns 1 growth point once an hour. The tree answers in a thought bubble.
5. **Decorate.** Growth milestones unlock 15 cosmetic treasures (mushrooms, a lantern, a sleepy cat…), one per spot. They stay with the tree in the Hall of Fame.

### Modes and difficulty

- **Zen Garden (easy):** the tree never dies. It tells you exactly what it needs, actions you've just done are greyed out until their cooldown ends, and Water is greyed out while the soil is still damp.
- **Greenhouse (hard, light stakes):** needs drain faster. If health falls below 30%, pests move in and growth stops until three different teammates treat them.
- **Arena (hard, competitive):** a weekday streak of 3+ earns a bonus point per action, and the top caretakers earn titles (Head Gardener, Water Bearer, Sun Chaser, Shear Genius, Soil Whisperer, Pest Patrol, Longest streak).

In the hard modes the tree only hints at its mood, and nothing is greyed out. Acting before your cooldown ends earns no points.

**Waterlogging:** watering while the soil is still wet counts as overwatering. Two overwaterings within 12 hours waterlog the tree and growth pauses. Two different teammates can **drain the pot**, or it dries out on its own after 24 hours without water (12 if someone gives it sunlight).

### Thoughts and sound

The tree has a thought bubble that changes every so often and reacts to care. Thoughts depend on how it's doing (cute and whimsical when it's thriving, somber or sad when it's neglected, worried when it's waterlogged or has pests), its species, the time of day and day of the week, the season, and holidays. Holidays include Halloween, Thanksgiving, winter holidays, New Year, Valentine's Day, Earth Day, Arbor Day, Lunar New Year, Cybersecurity Awareness Month and the end of each Abnormal fiscal quarter. In Zen Garden the thoughts are clear hints; in the hard modes they're cryptic.

Every action has a synthesized sound effect (no audio files). There's a Sound on/off switch under the title, remembered per browser.

### Animation studio

A preview-only tab to play every care animation (water, sunlight, prune, feed, pests, drain, talk, grow) on any species, stage and pot, and to try on treasures. Nothing there changes the shared garden.

### Trees

13 species in three groups:

- **Real:** juniper, Japanese maple, Japanese black pine, cherry blossom, wisteria, ficus
- **Team-themed:** neural net (glowing node leaves), phish-hook tree (fish leaves and one suspicious hook)
- **Fantasy:** crystal tree, ember tree, moonlight willow, cotton-candy tree, star tree

![Some of the species](docs/species.png)

Stages: Seed → Sprout → Seedling → Sapling → Pre-bonsai → Young bonsai → Shaped bonsai → Mature bonsai → Elder → Ancient → Legendary.

### Admin

The page owner and editors get an **Admin** tab with:

- **Activity log:** every water, vote, vote started/closed/cancelled, rename and pest event, with who and when. Only admins can read it; each person's entries can only be written by that person.
- **Leaderboard switch:** show or hide the leaderboard for the team. Points keep counting either way, and admins always see it.
- **Vote controls:** close the open vote early (the current leader is planted) or cancel it (the current tree stays).
- **Retire tree now:** ends the current tree early. It moves to the Hall of Fame and the pot stays empty until someone starts a vote.

## Web version

`web/bonsai-garden.html` is the source of the claude.ai page. It's a single file with no build step, written for Claude Artifacts, and uses two runtime capabilities:

- `db` keeps the shared state: `polls` (votes, closing times and the weekends choice), `ballots` (one per person), `carers` (each person's points and care times per tree), `seasons` (each tree's name, pest, waterlogging and retirement status, plus one record per decorated spot), `settings` (leaderboard visibility), `activity` (the admin log) and `meta` (Slack reminder bookkeeping). Which tree is growing is derived from the closed polls, so there is no separate "current tree" record to get out of sync.
- `user` gives each person's id and display name, and whether they're an admin (page owner or editor).

This copy keeps the full HTML wrapper so it also works in Glean; the claude.ai copy drops the wrapper (claude.ai adds its own) and loads the Google Fonts. Opened anywhere else, the page shows a read-only view. To give teammates access, share the page from its Share menu at Contributor level.

## Slack reminders

`reminders/reminder.py` plans the Slack posts. It reads a dump of the page's database and prints the messages that are due: a daily check-in (weekdays, or every day for a tree that counts weekends), vote opened / closing soon / winner announcements, and a needs-care nudge when health drops low, pests arrive or the tree gets waterlogged. A scheduled Claude task runs it hourly on weekdays and posts the results to the team channel.

## Slack version

The Slack app still follows the earlier three-pot design (one tree per mode, species switching per mode); it hasn't been updated to the single-tree voting model yet. See [`slack-app/README.md`](slack-app/README.md) for setup and what to send IT. In short: Bolt for JavaScript in Socket Mode, three bot scopes (`commands`, `chat:write`, `users:read`), one JSON data file, Node 20.6+.

```bash
cd slack-app
npm install
npm test
cp .env.example .env   # add your Slack tokens
npm start
```

## Ideas for later

- A prize mode where points count toward real team prizes, with points recomputed from the care log against the cooldown rules and winners confirmed by an admin
- Bring the Slack app in line with the single-tree voting model
