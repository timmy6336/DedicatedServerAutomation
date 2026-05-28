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

- [ ] All 5 games appear: Palworld, Valheim, Rust, Don't Starve Together, Minecraft
- [ ] Each game shows its instance count badge
- [ ] Clicking a game header expands / collapses its section
- [ ] "New server" button appears when a game is expanded
- [ ] Empty state shown in main panel when no instance is selected

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

---

## 5. Install Wizard — Steam Games (Palworld, Valheim, Rust, DST)

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
- [ ] "Save Changes" saves and closes after ~800ms
- [ ] "Cancel" closes without saving
- [ ] Two instances of the same game can have **different** configs (verify by saving different port values)

---

## 8. Mods Tab — Minecraft

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

## 9. Mods Tab — Valheim & Rust

- [ ] "Mods" tab visible (same as Minecraft)
- [ ] `.zip` and `.dll` files accepted via Browse / drag-drop
- [ ] Palworld and DST do **not** show a Mods tab

---

## 10. Server Start / Stop

- [ ] "Start Server" launches the server process
- [ ] Status badge changes to "Online" (may take up to 10s for next poll)
- [ ] Local IP and port shown in connection info cards
- [ ] "Stop Server" terminates the process
- [ ] Status badge returns to "Offline"
- [ ] **Minecraft** — start command runs `java -jar server.jar nogui` (check Task Manager / `ps`)
- [ ] **Enabled mods** are copied to `mods/` before server starts
- [ ] Starting a second instance of the same game while the first is running works independently

---

## 11. Persistence Across Restarts

- [ ] Close and reopen the app
- [ ] All previously created instances appear in the sidebar
- [ ] Saved configs reload correctly
- [ ] Mod library entries persist
- [ ] Enabled mod selections per instance persist

---

## 12. Edge Cases

- [ ] Create 3+ instances for the same game — sidebar scrolls if needed
- [ ] Long instance name truncates gracefully in the sidebar
- [ ] Renaming an instance (future feature) — not yet implemented, verify no crash
- [ ] Installing the same game twice (two instances) — each gets its own directory, no conflict
- [ ] Adding the same mod file twice — no duplicate in the library (file overwritten, single entry)
- [ ] Dropping a non-mod file (e.g. `.txt`) onto the drop zone — ignored
- [ ] No internet connection during install — wizard shows a clear error message
