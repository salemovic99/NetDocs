# NetDocs Frontend

Modern SaaS dashboard for **NetDocs** (PRD §11), built on **Next.js 16** (App Router) +
React 19 + Tailwind v4, styled from `../DESIGN.md` ("Operational Clarity" deep-slate theme).

## Stack
- Next.js 16 (App Router, `proxy.ts` route guard, async params/cookies, Turbopack)
- Tailwind v4 (`@theme` tokens) + shadcn/ui (`components/ui`) + lucide-react
- TanStack Query (server cache) · react-hook-form + Zod (typed forms)
- Framer Motion (page/list/modal motion, reduced-motion aware)

## Architecture (separation of concern)
- **BFF auth**: JWTs live in **httpOnly cookies** set by `app/api/auth/*`; `app/api/proxy/[...path]`
  attaches the Bearer token and auto-refreshes on 401. The browser only calls same-origin Next.
- **Page-scoped components** colocate in each route's `_components/` folder. Shared primitives live
  in `components/ui` (shadcn) and `components/shared`. Data layer in `lib/` (`api`, `schemas`,
  `hooks`, `auth`, `motion`, `permissions`).

```
app/(auth)/login            app/(app)/{problems,inventory,sites,search,admin,...}
app/api/{auth,proxy}        components/{ui,shared}        lib/{api,schemas,hooks,auth,motion}
proxy.ts                    components.json
```

## Develop
> Requires **Node ≥ 20.9** (Next 16). 
```bash
npm install
API_INTERNAL_URL=http://localhost:8000 npm run dev   # http://localhost:3000
```
Backend must be running (`docker compose up` at repo root). Log in as the bootstrap admin.

## Production / Docker
The repo-root `docker-compose.yml` builds this via the `frontend` profile:
```bash
docker compose --profile frontend up --build
```
`output: "standalone"` is enabled; `API_INTERNAL_URL` (server-only) points at the API.

## Routes (PRD §11)
/login · / (dashboard) · /problems (+ /new, /[id], /[id]/edit) · /inventory (+ /[id] with VLAN CRUD)
· /inventory/isp-links · /inventory/wireless · /sites (+ /[id]) · /search · /admin/{users,roles,inventory}
· /change-password
