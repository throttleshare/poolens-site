# SplashLens Launch-Now Handoff

Updated: May 26, 2026

## What Windows/Codex Wired

- Production app: `https://app.splashlens.com`
- Production site: `https://splashlens.com`
- PartSnap Pro checkout is live:
  - Monthly: `https://buy.stripe.com/7sY7sE2aIaq31cE5EF8AE0O`
  - Annual: `https://buy.stripe.com/aFa28k9Da69NdZq3wx8AE0P`
- Site checkout redirects:
  - `https://splashlens.com/api/checkout?plan=monthly`
  - `https://splashlens.com/api/checkout?plan=yearly`
- App checkout redirects:
  - `https://app.splashlens.com/api/checkout?plan=monthly`
  - `https://app.splashlens.com/api/checkout?plan=yearly`
- Anonymous launch event capture:
  - Endpoint: `POST https://splashlens.com/api/event`
  - D1 database: `splashlens-subscribers`
  - Table: `events`
  - Captures page views, open-app clicks, checkout clicks, AI scan starts, PartSnap results, and buy-link clicks.
- Privacy copy now reflects the live scanner, waitlist email capture, Stripe checkout, and first-party anonymous launch events.

## Query Commands

```powershell
npx wrangler d1 execute splashlens-subscribers --remote --command "SELECT event, source, path, plan, mode, created_at FROM events ORDER BY id DESC LIMIT 50"
npx wrangler d1 execute splashlens-subscribers --remote --command "SELECT email, source, created_at FROM subscribers ORDER BY created_at DESC LIMIT 100"
```

## Launch Actions That Still Require Console/Mac/Human Access

- Google Play Console: submit a TWA wrapper around `https://app.splashlens.com`.
- Apple App Store: submit the Capacitor/Median wrapper and screenshots from Mac/Xcode or the chosen wrapper service.
- Cloudflare Web Analytics: optional; first-party event capture is already live, but Cloudflare beacon still requires a dashboard token if you want CF's built-in charts.
- Amazon Associates: apply for/approve affiliate tag, then replace `YOUR_TAG` in the app with the approved tag.
- Email platform: export D1 subscribers to Brevo, Resend, or SendGrid before sending announcements.

## Fast Field Launch Copy

Use this angle in Facebook groups and tech conversations:

> Free pool tech field rescue app. No account. Open it at app.splashlens.com. Error-code lookup and dosing tools work offline after first load. Online scanner reads equipment displays, identifies parts with PartSnap, and helps with test-strip triage. Core tools stay free during season.

## Verification Targets

- `https://splashlens.com/` should show PartSnap Pro and free field tools.
- `https://splashlens.com/privacy.html` should mention online AI scanner, Stripe, email capture, and anonymous first-party launch events.
- `https://splashlens.com/api/event` should accept a JSON POST and write to D1.
- `https://app.splashlens.com/` should show 10 free AI scans monthly and post scan/upgrade/buy events to the site event endpoint.
