# Fact-mining brief (give this to each sub-agent)

Goal: for each person in your roster chunk, find 2-5 light, fun, verifiable personal facts from Slack that coworkers could use to guess who they are. Variety matters: hobbies, pets (species and names), hidden talents, past or odd jobs, travel, food opinions, sports teams, games, shows, music, collections, home region, "fun fact" intros, memorable non-work moments.

Load the Slack tools with a tool search first: user search, profile read, public search (and public-and-private search only if the host approved private channels), thread read, channel read.

## Sources, best first

1. **#all-welcome** Workday welcome posts. Format: "Welcome, NAME! ... A fun fact about NAME: ... In their free time they enjoy: ...". Look up the channel ID with a channel search, then search keywords `["Welcome", "First", "Last"]` filtered to that channel. Older posts read "Welcome NAME! They are joining as..."; try that too, and try the last name alone.
2. **The team's social channel** (find it with a channel search for words like random, social, fun, pets, the team's name). Search with the `from:` filter (the person's user ID in Slack mention form: at-sign plus ID, in angle brackets) and the `in:` filter for that channel, then keyword searches (dog, cat, weekend, trip, concert, game, favorite) with the same `from:` filter. Icebreaker threads ("favorite candy / color / dessert") and pet show-and-tell threads are gold: read the whole thread.
3. **Company-wide social channels** like #pets-of-abnormal.
4. **Team channels**: non-work banter only.
5. **Slack profile**: title, custom fields, timezone (region only).

If a roster entry has no Slack ID, find it with user search by full name or last name. Budget about 3-6 tool calls per person; mark people with nothing as `"facts": []` and move on.

## Rules

- Never invent or embellish. Every fact needs a short verbatim quote from a message or profile you actually read, written by that person about themselves. If a fact comes from someone else's post (contest results, "with the one and only X"), include it only if harmless and flag it in your reply.
- Follow `privacy.md`. When unsure, leave it out.
- Don't include facts about how someone works (queues, labels, performance).
- Discard any direct-message result; only channel posts and profiles count.
- Quote only the part of a message the fact needs. If the sentence also mentions family or anything else on the privacy list, cut that part out of the quote.
- Include the source as `#channel YYYY-MM-DD` and the permalink exactly as the tool returns it. If you build a link from a channel ID and timestamp, say so.

## Output

Write a JSON array to the path you were given:

    [{"name": "", "slack_id": "", "title": "", "team": "",
      "facts": [{"fact": "short third-person paraphrase", "category": "hobby|pet|talent|travel|food|job|sports|media|hometown|other",
                 "quote": "verbatim snippet", "source": "#channel YYYY-MM-DD", "permalink": ""}]}]

Reply with counts (people with 2+ facts, 1 fact, 0 facts), anything you left out as sensitive (in general terms), and any judgment calls. Keep the reply short; the file is the deliverable.
