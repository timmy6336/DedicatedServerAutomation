# Testing Checklist — feature/electron-react-ui

## Setup

```bash
cd electron-app
npm install
npm run dev
```

---

## 1. App Shell

- [ ] App launches without errors
- [ ] Custom titlebar renders (no native frame)
- [ ] Minimize button works
- [ ] Maximize / restore button works
- [ ] Close button exits the app
- [ ] Window has a minimum size (can't shrink below ~900×600)
- [ ] Dark background (#09090b) with no white flash on load

---

## 2. Sidebar — Game & Instance Tree

- [ ] All 10 games appear: Palworld, Valheim, Rust, Don't Starve Together, Minecraft, ARK: Survival Evolved, 7 Days to Die, Project Zomboid, V Rising, Enshrouded
- [ ] Each game shows its instance count badge
- [ ] Clicking a game header expands / collapses its section
- [ ] "New server" button appears when a game is expanded
- [ ] Empty state shown in main panel when no instance is selected
- [ ] Sidebar scrolls when all 10 games are expanded

---

## 3. Creating Server Instances

- [ ] Clicking "New server" opens the **New Server modal**
- [ ] Modal shows the correct game name in the title
- [ ] Pressing Enter submits (same as clicking Create)
- [ ] Cancel closes modal without creating anything
- [ ] Create with a blank name is disabled (button greyed out)
- [ ] After creation the new instance appears in the sidebar
- [ ] The new instance is auto-selected and shown in the main panel
- [ ] Create a **second instance** for the same game — both appear in sidebar
- [ ] Each instance has its own entry; selecting one updates the main panel

---

## 4. Server Panel — Overview Tab

- [ ] Instance name shown as heading, game name shown as subtitle
- [ ] Genre and status badge visible in the hero header
- [ ] Status badge shows "Checking…" briefly on load
- [ ] Status badge shows "Not Installed" for a brand-new instance
- [ ] "Install Server" button appears when not installed
- [ ] "Start Server" + "Configure" appear when installed but stopped
- [ ] "Stop Server" + "Configure" appear when server is running
- [ ] Spinner shown on Start/Stop while action is pending
- [ ] Status auto-refreshes every 10 seconds (no manual refresh needed)
- [ ] Port list renders correctly for each game
- [ ] Platform badges (Windows / Linux / macOS) shown correctly
- [ ] Switching between instances resets the tab back to Overview

---

## 5. Install Wizard — Steam Games (Palworld, Valheim, Rust, DST, ARK, 7DTD, Zomboid, V Rising, Enshrouded)

- [ ] Clicking "Install Server" opens the wizard
- [ ] Wizard title shows correct game name and Steam App ID
- [ ] Cancel button closes wizard before install starts
- [ ] "Start Installation" button begins the process
- [ ] **Step 0** — SteamCMD download progress bar animates (0→100%)
- [ ] If SteamCMD is already present, Step 0 skips to "already installed"
- [ ] **Step 1** — Server files progress bar parses SteamCMD output
- [ ] Live log panel streams SteamCMD output lines with auto-scroll
- [ ] Steps 0 and 1 show a green "Done" checkmark when complete
- [ ] **Step 2** shows "Complete" with green checkmark on success
- [ ] "Done" button appears after successful install; closes wizard
- [ ] On failure, an error message is shown in red; "Close" button appears
- [ ] After closing, server status refreshes (should now show "Stopped")

---

## 6. Install Wizard — Minecraft (Mojang flow)

- [ ] Wizard shows custom step labels: "Check Java & fetch version", "Download server JAR", "Configure & finalize"
- [ ] **Step 0** — checks for Java; if missing, shows error with link to adoptium.net
- [ ] **Step 0** — fetches version manifest, logs "Minecraft X.XX.X"
- [ ] **Step 1** — downloads server.jar with progress bar (shows MB size in log)
- [ ] **Step 2** — writes eula.txt and server.properties; logs confirmation
- [ ] After install, `server.jar` exists in the instance directory
- [ ] `eula.txt` contains `eula=true`
- [ ] `server.properties` has sensible defaults

---

## 7. Configure Modal

- [ ] Opens for any installed server (stopped or running)
- [ ] Fields pre-populated with defaults on first open
- [ ] Saved values reload correctly on re-open
- [ ] **String** fields accept text input
- [ ] **Password** fields mask input (dots)
- [ ] **Int** fields show a number spinner with min/max enforced
- [ ] **Bool** fields show a working toggle switch
- [ ] **Choice** fields show a dropdown with correct options
- [ ] Required fields marked with a red asterisk
- [ ] Fields with `helpUrl` (e.g. DST cluster token) show a clickable "Get token" link
- [ ] **Discord Webhook URL** field appears in every game's config
- [ ] "Save Changes" saves and closes after ~800ms
- [ ] "Cancel" closes without saving
- [ ] Two instances of the same game can have **different** configs (verify by saving different port values)

---

## 8. Logs Tab

- [ ] "Logs" tab visible on every server panel
- [ ] Empty state message shown when server has not been started this session
- [ ] Starting the server causes log lines to stream into the panel in real time
- [ ] Log panel auto-scrolls to the bottom as new lines arrive
- [ ] Scrolling up pauses auto-scroll; "↓ Scroll to bottom" button appears
- [ ] Clicking "↓ Scroll to bottom" resumes auto-scroll and hides the button
- [ ] **Color coding** — error/exception lines appear red, warn lines yellow, others grey
- [ ] "Clear" button empties the log panel
- [ ] "Clear" button is disabled when the log is already empty
- [ ] Switching to another tab and back preserves the log buffer within the session
- [ ] Switching to a **different instance** clears the buffer (each instance has its own log)
- [ ] Buffer capped at ~1000 lines; oldest lines are dropped when exceeded

---

## 9. Backups Tab

- [ ] "Backups" tab visible on every server panel
- [ ] Empty state shown with description when no backups exist
- [ ] **Create Backup** button copies the entire server directory to a timestamped snapshot
- [ ] After creation, the backup appears in the list with a human-readable date and file size
- [ ] Multiple backups appear newest-first
- [ ] Clicking **Restore** shows an inline confirmation ("Overwrite current files? Yes / Cancel")
- [ ] Confirming restore overwrites the server directory with the backup contents
- [ ] Cancelling restore does nothing
- [ ] **Delete** (trash icon) removes the backup from list and disk immediately
- [ ] Yellow warning banner shown when the server is running
- [ ] Create Backup and Restore buttons disabled while server is running
- [ ] File sizes display correctly (B / KB / MB / GB)

---

## 10. Discord Webhook Integration

- [ ] Open Configure for any server, paste a valid Discord webhook URL into the field, save
- [ ] **Start the server** → Discord channel receives "🟢 **Server Name** is now **Online**!"
- [ ] **Stop the server** → Discord channel receives "🔴 **Server Name** is now **Offline**."
- [ ] If the server **crashes** (exits with non-zero code) → channel receives "⚠️ **Server Name** crashed (exit code N)."
- [ ] Leaving the webhook URL blank → no messages sent, no errors
- [ ] Invalid/unreachable URL → app continues normally (webhook errors are silent)
- [ ] Two instances of the same game each post to their own webhook if configured separately

---

## 11. Mods Tab — Minecraft

- [ ] "Mods" tab visible on a Minecraft server panel
- [ ] Tab shows a count badge when mods are enabled
- [ ] Library is empty on first use — empty state message shown
- [ ] **Browse button** opens a native file picker filtered to `.jar`
- [ ] Selecting a `.jar` adds it to the library list
- [ ] Mod row shows filename, display name, and file size
- [ ] **Drag and drop** a `.jar` file from Finder/Explorer onto the drop zone — mod appears in library
- [ ] Drop zone highlights on hover with correct accent colour
- [ ] **Toggle switch** enables a mod on the current instance
- [ ] Enabled mod shows "Enabled" badge with accent colour
- [ ] Toggling off removes the "Enabled" badge
- [ ] Enabled count in tab badge updates when toggling
- [ ] **Two instances** — enabling a mod on Instance A does NOT enable it on Instance B
- [ ] **Delete button** (trash icon, visible on row hover) removes mod from library
- [ ] Deleted mod also disappears from enabled list if it was on
- [ ] After toggling, the mod file is present/absent in the instance's `mods/` directory on disk

---

## 12. Mods Tab — Valheim & Rust

- [ ] "Mods" tab visible (same as Minecraft)
- [ ] `.zip` and `.dll` files accepted via Browse / drag-drop

---

## 13. Mods Tab — 7 Days to Die, Project Zomboid, V Rising

- [ ] "Mods" tab visible for all three games
- [ ] `.jar`, `.zip`, and `.dll` files accepted via Browse / drag-drop
- [ ] Toggle, per-instance isolation, and library delete all work the same as Minecraft

---

## 14. Games Without a Mods Tab

- [ ] Palworld, Don't Starve Together, ARK: Survival Evolved, and Enshrouded do **not** show a Mods tab

---

## 15. New Games — Per-Game Spot Checks

### ARK: Survival Evolved
- [ ] Genre "Survival / Action"; accent colour amber
- [ ] Ports: 7777 UDP (Game), 7778 UDP (Raw UDP), 27015 UDP (Steam Query)
- [ ] Settings: Session Name, Join Password, Admin Password, Max Players, Game Port, Query Port, Discord Webhook

### 7 Days to Die
- [ ] Genre "Survival / Horror"; accent colour red
- [ ] Ports: 26900 UDP (Game), 26901 UDP (Query), 26902 UDP (Steam), 8080 TCP (Web Panel)
- [ ] Settings: Server Name, Server Password, Max Players, Difficulty (choice field), Discord Webhook

### Project Zomboid
- [ ] Accent colour zinc/grey
- [ ] Ports: 16261 UDP (Game), 16262 UDP (Direct)
- [ ] Settings: Server Name, Admin Password, Max Players, Public Server toggle, Discord Webhook

### V Rising
- [ ] Genre "Survival / Action RPG"; accent colour purple
- [ ] Ports: 9876 UDP (Game), 9877 UDP (Query)
- [ ] Settings: Server Name, Max Players (max 40), Game Port, Query Port, Discord Webhook

### Enshrouded
- [ ] Accent colour violet
- [ ] Ports: 15636 UDP (Game), 15637 UDP (Query)
- [ ] Settings: Server Name, Password, Max Players (max 16), Game Port, Discord Webhook

---

## 16. Server Start / Stop

- [ ] "Start Server" launches the server process
- [ ] Status badge changes to "Online" (may take up to 10s for next poll)
- [ ] Local IP and port shown in connection info cards
- [ ] "Stop Server" terminates the process
- [ ] Status badge returns to "Offline"
- [ ] Status badge updates **immediately** if the server crashes (no waiting for the 10s poll)
- [ ] **Minecraft** — start command runs `java -jar server.jar nogui` (check Task Manager / `ps`)
- [ ] **Enabled mods** are copied to `mods/` before server starts
- [ ] Starting a second instance of the same game while the first is running works independently

---

## 17. Persistence Across Restarts

- [ ] Close and reopen the app
- [ ] All previously created instances appear in the sidebar
- [ ] Saved configs reload correctly (including Discord webhook URL)
- [ ] Mod library entries persist
- [ ] Enabled mod selections per instance persist
- [ ] Backup list persists (backups are on disk; reappear on next open)

---

## 18. Edge Cases

- [ ] Create 3+ instances for the same game — sidebar scrolls if needed
- [ ] Long instance name truncates gracefully in the sidebar
- [ ] Installing the same game twice (two instances) — each gets its own directory, no conflict
- [ ] Adding the same mod file twice — no duplicate in the library (file overwritten, single entry)
- [ ] Dropping a non-mod file (e.g. `.txt`) onto the mod drop zone — ignored
- [ ] No internet connection during install — wizard shows a clear error message
- [ ] Creating a backup of a not-yet-installed instance — fails gracefully, no crash
- [ ] Restoring a backup when the instance directory no longer exists — handled without crash
- [ ] Discord webhook with a malformed URL (missing `https://`) — silently ignored, no crash
- [ ] Log panel with 1000+ lines — oldest lines are dropped, UI remains responsive
