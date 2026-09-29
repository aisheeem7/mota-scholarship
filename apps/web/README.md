# TRISETU Web Application

The Next.js frontend for TRISETU. It contains the student portal, the administration dashboard and the application review interface. See the [project README](../../README.md) for the full system overview.

## Features

- **Student portal:** scheme selection, document upload with checks in the browser, and a status timeline.
- **Administration:** live application dashboard, application queue and review page with a validation scorecard.
- **Officer decisions:** approve, reject or request resubmission, each with a mandatory reason.
- **Languages:** English, Hindi and Bengali, switchable from the header.
- **Government-style interface:** compact masthead, tricolour accent, skip link and accessible focus states.

## Getting Started

```bash
npm install
cp .env.example .env.local
npm run dev
```

The application is served at `http://localhost:3000`. The backend must be running at the URL set in `NEXT_PUBLIC_API_URL`.

## Environment Variables

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Base URL of the FastAPI backend, for example `http://localhost:8000` |
| `NEXT_PUBLIC_DEMO_STUDENT_ID` | UUID of a seeded student, used by the demo upload flow |

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Start the development server |
| `npm run build` | Create a production build (includes type checking) |
| `npm run start` | Serve the production build |
| `npm run lint` | Run ESLint |

## Structure

| Path | Contents |
|---|---|
| `app/` | Routes: home, `student/*`, `admin/*` |
| `components/layout/` | Government header, footer and language provider |
| `components/admin/` | Validation scorecard |
| `components/ui/` | Shared UI components |
| `lib/api.ts` | Typed client for the backend API |
| `lib/i18n.ts` | English, Hindi and Bengali translations |
| `lib/types.ts` | Shared API types and status labels |
