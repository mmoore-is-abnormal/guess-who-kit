# Slack profile photos (optional)

Slack's image host (avatars.slack-edge.com) is blocked from the cloud workspace and from the Mac sandbox shell, so photos have to come through the host's own Chrome. The flow downloads one small grid image, which counts as a file download: confirm with the host first (file name, source, rough size).

1. **Get photo URLs.** Slack user search with the detailed response format returns `Profile Pic: [Photo](URL)` for each person. Pick the result whose user ID matches the roster, then save `avatars.json` keyed by the exact name used in data.json: `{"Full Name": {"id": "U...", "url": "..."}}`. A name that doesn't match exactly gets a grey tile, so check the photo script's `bad` list. A sub-agent can do the whole roster in one pass.
2. **Make the stitching script.** `python3 scripts/photo_script.py data.json avatars.json photos.js`. Set `cols`/`rows` in data.json to what it prints, and each person's `i` to their index in `people`.
3. **Chrome setting.** The host turns on Chrome's menu-bar **View → Developer → Allow JavaScript from Apple Events** (the macOS menu bar at the top of the screen, with their work Chrome window in front, not Chrome's three-dot menu). If it's grayed out, IT has locked it: fall back to initials.
4. **Run it.** With the Control Chrome tools on the host's Mac: open any one avatar URL in a new tab (so the script runs on that same origin and the canvas can export), run `photos.js` there, then poll `window.__res` until it reports `ok` and `bad`. Chrome saves `guess-who-avatars.jpg` to Downloads. Close the tab afterwards.
5. **Pick it up.** Ask for access to the Downloads folder, copy the file into another connected folder (downloads can be hardlinked, which staging refuses), stage the copy, and look at it to confirm the faces filled in. Pass it to the build as `--avatars`.
6. **Tell the host** they can turn the Chrome setting back off and delete the downloaded file; the photos are embedded in the game.

If Control Chrome reports Chrome isn't running even though a tab opened, that usually means the Apple Events setting is still off.
