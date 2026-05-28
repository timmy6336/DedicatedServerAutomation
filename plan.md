# Monetization Plan — Dedicated Server Automation

## Model: Freemium + Pro Tier

### Free Tier
- 1 server instance per game
- Manual install, start, and stop
- Basic config editor
- Local mod library

### Pro Tier (~$5–8/month or ~$40 one-time)
- Unlimited server instances per game
- Scheduled auto-restart (cron-style rules)
- Remote management via cloud relay (start/stop from phone/browser)
- Automatic backups to local path or cloud (S3 / Backblaze B2)
- One-click mod updates (check for newer versions automatically)
- Priority support

---

## Implementation Roadmap

### Phase 1 — Feature Gating
- Gate instance count > 1 behind Pro
- Add license key input in Settings
- Validate key client-side (HMAC) with optional server-side check

### Phase 2 — Payments & Distribution
- Set up storefront on **Gumroad** or **Lemon Squeezy** (handles payments, VAT, license key generation)
- Offer both monthly subscription and one-time lifetime option
- Distribute app on GitHub (free tier) with Pro upgrade link

### Phase 3 — Pro Features (build in order of demand)
1. Unlimited instances (gate lift — quick win once licensing is wired)
2. Scheduled auto-restart
3. Automatic backups
4. Remote management relay
5. One-click mod updates

### Phase 4 — Growth
- Post to relevant communities: r/gameservers, r/admincraft, game-specific Discord servers
- Add GitHub Sponsors button alongside the paid tier
- Collect feedback, prioritize next game additions based on requests

---

## Pricing Rationale
- **$5–8/month** is impulse-buy territory for anyone running a game server
- **$40 one-time** appeals to self-hosters who distrust subscriptions
- Free tier creates organic word-of-mouth; Pro converts power users

---

## Notes
- License validation should work offline (HMAC) so the app doesn't break without internet
- Keep the free tier genuinely useful — it builds trust and the install base
- Start with manual license distribution (copy/paste key from Gumroad) before building a full auth backend
