# Marcos OS Dashboard

The primary interface for Marcos OS — a mobile-first, responsive Progressive
Web App. The same application is the interface across phones, tablets, and
desktops.

**Status:** v0.1 — Home screen only. Mock data throughout; no backend
integration yet.

---

## Stack

| Concern | Choice | Why |
|---|---|---|
| Framework | React 19 + TypeScript + Vite | Client-only SPA — no meta-framework, so no seam for business logic to leak out of `marcos-core` |
| Styling | Tailwind CSS v4 | Fast iteration, first-class dark mode |
| Components | shadcn/ui (on Radix/base-ui) | Generated into the codebase, not an opaque dependency — fully ownable and editable |
| Routing | React Router | Real URLs per tab, proper back-button and deep-link behavior |
| Animation | Motion (Framer Motion) | Entrance stagger, animated bottom-nav indicator |
| Icons | lucide-react | |
| PWA | vite-plugin-pwa (Workbox) | Manifest + service worker, installable |

See `specs/` at the repository root for the technology decision rationale.

---

## Project Structure

```
src/
├── components/
│   ├── ui/          shadcn/ui primitives
│   ├── layout/       AppShell, TopBar, BottomNav
│   └── shared/        reusable composed pieces
├── features/
│   ├── home/          Home screen and its section components
│   └── placeholder/    ComingSoon — used by not-yet-built tabs
├── data/mock/         typed mock data fixtures
├── api/                thin data-access functions (mock today, real fetch later)
├── hooks/, lib/, types/
```

The `api/` layer is the seam for connecting to a real backend later: every
screen reads data through a function like `getDashboardSnapshot()`. Only
that function's internals change when `marcos-core` exposes a real API — no
component is touched.

---

## Development

```bash
npm install
npm run dev       # http://localhost:5173
npm run build     # type-check + production build to dist/
npm run preview   # serve the production build locally
npm run lint
```

Regenerate PWA icons from the brand mark source if it ever changes:

```bash
node scripts/generate-icons.mjs
```

---

## Docker

```bash
docker build -t marcos-dashboard .
docker run -p 8080:80 marcos-dashboard
```

Multi-stage build: Node builds static assets, nginx serves them. The final
image ships no Node runtime. `nginx.conf` handles SPA fallback routing and
long-lived caching for hashed assets.

---

## What's Built (v0.1)

- Home screen: Greeting, Current Sprint, Current Task, Today's Focus,
  Builder Status, Quick Actions, Recent Activity — mock data
- AppShell: top bar with dark mode toggle, bottom navigation with animated
  active-tab indicator
- Capture / AI / System tabs exist as routes with a placeholder screen —
  not yet built out

## What's Not Built Yet

- Real data — everything currently reads from `src/data/mock/`
- Capture, AI, and System tab content
- Any connection to `marcos-core`
