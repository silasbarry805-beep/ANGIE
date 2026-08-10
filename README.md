# ANGIE — Web + PWA

A rebuild of ANGIE as a responsive web app instead of a desktop Flet
app — same idea as Clavi (Flask + AI + SQLite), with a PWA layer so
it installs on any phone or laptop straight from the browser and
works even when the connection drops.

## Run it locally

```
pip install -r requirements.txt
cp .env.example .env
# then edit .env and add your real GROQ_API_KEY
python app.py
```

Visit `http://localhost:5000` — sign up, and you're in.

## Installing it as an app (PWA)

Once it's running somewhere reachable (locally or deployed):

- **Android (Chrome)**: open the site, tap the menu (⋮) → "Install app"
  — or wait for the in-app install banner to appear automatically.
- **iPhone/iPad (Safari)**: open the site, tap Share → "Add to Home
  Screen". (iOS doesn't support the automatic install prompt — this
  manual step is Apple's only path for any PWA, not specific to ANGIE.)
- **Windows/Mac/Linux (Chrome, Edge)**: look for the install icon (⊕)
  in the address bar, or use the in-app install banner.

Once installed, it opens in its own window, gets its own icon, and
the chat/dashboard/journal/mood pages you've already visited keep
working offline (new AI replies still need a connection).

## Deploying so others can reach it

This is a normal Flask app — it needs a real host to be reachable
from other devices (a PWA can only be installed over `https://`,
except on `localhost` for testing). Common free/cheap options:
Render, Railway, Fly.io, PythonAnywhere. Ask if you want a walkthrough
for any of these — the steps differ enough between them that it's
worth doing as its own guide.

## What's the same as the Flet version, what's different

**Same**: color palette, topic list, AI system prompt/model (Groq),
journal/mood/settings feature set, database structure (users,
messages, moods, journal_entries).

**Different**: runs in any browser instead of needing a desktop
install; installable as a PWA on phone AND laptop from one codebase
instead of needing separate builds; chat streams over Server-Sent
Events instead of Flet's own update loop; responsive layout (bottom
tab bar on phone, top nav on desktop) instead of a fixed window size.

## Project structure

```
app.py              Flask routes
ai.py                Groq streaming AI engine
database.py           SQLite data layer
templates/            Jinja2 HTML pages
static/css/style.css   Responsive styling, light/dark themes, wallpapers
static/js/             Per-page JS (auth, chat, journal, mood, settings)
static/manifest.json   PWA manifest
static/service-worker.js   Offline caching
static/icons/           App icons (192, 512, maskable)
data/angie.db           SQLite database (created on first run)
```
