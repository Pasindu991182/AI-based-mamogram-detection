# ExBI-RADS Engine — Frontend

React + Vite (JSX) SPA for the Explainable BI-RADS Morphological Scoring
Engine. Email/password login → a **Worklist** home → a guided **6-step diagnostic
wizard** (Upload → Segment → Features → BI-RADS → ER Status → Report), matching
the diagnostic-pipeline wireframe.

## Stack
- React 18 + Vite 6 (plain JavaScript / JSX)
- Tailwind CSS v4
- React Router v6
- Axios client with a JWT Bearer interceptor; the access token is kept in memory
  only and silently renewed from an `httpOnly` session cookie

## Quick start

```bash
cd birads-frontend
npm install
cp .env.example .env     # set VITE_API_URL
npm run dev              # http://localhost:5173
```

Sign in with an account created on the backend
(`python -m scripts.create_user …`, or the admin **Users** screen). The app's
origin must be listed in the backend's `BACKEND_CORS_ORIGINS`.

## Structure

```
src/
├── main.jsx             # AuthProvider + App
├── App.jsx              # router (public /login, protected app shell)
├── routes/              Login · Worklist (home) · Study (wizard)
├── components/          ProtectedRoute · Layout · Brand · Stepper
│   └── study/           UploadStep · SegmentStep · FeaturesStep ·
│                        BiRadsStep · ErStep · ReportStep
├── context/AuthContext  # user + session, restores it from the cookie on load
├── hooks/useAuth        # context accessor
└── lib/api.js           # axios instance + endpoint calls
```

A teal brand palette (`brand-*`, from `#0f9b8e`) is defined via Tailwind v4
`@theme` in `index.css`.

## Flow
1. **Login** — email + password → backend `/auth/login` → access JWT in memory
   + session cookie. A temporary password must be changed before continuing.
2. **Worklist** — `/cases` list with search + BI-RADS 4/5 filter; each row
   shows views, BI-RADS, ER status and sign-off state. **+ New study** opens
   the wizard; clicking a row reopens it for that case.
3. **Study wizard** (`/study`) — one guided flow that persists to a Case:
   1. **Upload** — patient details + CC/MLO → creates the case, runs `/analyze`.
   2. **Segment** — original → attention overlay → binary mask, per view.
   3. **Features** — 6 worst-case radiomic features with CC/MLO sub-values.
   4. **BI-RADS** — category + **why** panel (rules that fired + importance).
   5. **ER Status** — 7 inputs (tumour size auto-filled) → `/er/predict`,
      probability bar, contributions, treatment signal.
   6. **Report** — auto-drafted, editable; **Save draft** / **Sign & finalize**
      (`/report`), plus Print / PDF.

## Build

```bash
npm run build      # vite production build → dist/
npm run preview
```

Deploy `dist/` to Vercel / Netlify; set the two `VITE_*` env vars there.
