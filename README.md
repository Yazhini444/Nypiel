# nypiel — skin, but better

A full-stack skin analysis platform: users upload a photo or use a live
camera scan, get their **skin type** (Model 1) and **skin concerns**
(Model 2, up to 10 classes) detected, see ingredient recommendations, save
results to their account, and can ask a chatbot follow-up questions.

```
nypiel/
├── backend/     FastAPI + SQLite — auth, inference, recommendations, chat
└── frontend/    React + Vite + Tailwind — nypiel-branded UI
```

## 1. Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

This runs the API at `http://localhost:8000`, auto-creates `nypiel.db`
(SQLite), and serves uploaded photos back at `/uploads/...`. Interactive
API docs: `http://localhost:8000/docs`.

### Plugging in your two trained models

Everything model-related lives in **`backend/app/inference.py`** — it's the
only file you should need to touch:

- `predict_skin_type(image_bytes)` → Model 1 (skin type: dry / oily /
  combination / normal)
- `predict_skin_concerns(image_bytes)` → Model 2 (multi-label, up to 10
  concern classes, each with an optional `[x, y, w, h]` box as a fraction
  of image size so the frontend can draw markers)
- `load_models()` is called once on server startup — load your weights
  there (`torch.load`, `tf.keras.models.load_model`, `onnxruntime`, etc.)

Until you wire in real weights, both functions return realistic mock
predictions so the rest of the app (auth, saving, recommendations, chat,
UI) is fully testable today.

The `CONCERN_CLASSES` list at the top of that file should match your
model's label order exactly — edit it to your real 10 classes.

### Ingredient logic

`backend/app/recommendations.py` is a plain, editable rule table mapping
skin type + detected concerns → ingredients (niacinamide, salicylic acid,
retinol, vitamin C, etc.), each with usage timing and frequency. No ML
needed here — tweak the dictionaries directly as your product line grows.

### Chatbot

`backend/app/chatbot.py` is a small keyword-retrieval bot over a skincare
knowledge base, with no external API key required, so it works offline.
When a `scan_id` is passed, it grounds its answer in that user's saved
skin type/concerns/recommendations. Swap `answer()`'s body for a call to
an LLM API later if you want richer conversation — the function signature
won't need to change.

### Data model

- `User` — email, hashed password (bcrypt), name
- `ScanResult` — owned by a user; stores the image path, both models'
  outputs, and the computed recommendations, timestamped

Auth is JWT-based (`Authorization: Bearer <token>`), 1-week expiry.
Set a real `NYPIEL_SECRET_KEY` env var in production.

### Streamlit authentication and storage

The deployed Streamlit app uses the same SQLAlchemy `users` table and bcrypt
password hashes as the standalone FastAPI app. By default both use
`nypiel.db` at the repository root. Existing FastAPI users remain compatible
when that database file is available to Streamlit; no accounts are migrated
or deleted automatically.

Set `DATABASE_URL` when Streamlit should use a different SQLite file or an
external database, for example `sqlite:////mounted/path/nypiel.db`. The
database file is not committed because it may contain account data.

Streamlit Community Cloud does not guarantee persistence for files written to
the app container. The default SQLite file can therefore be lost when the
app/container is recreated. Use a persistent external database or mounted
storage supported by the deployment environment if accounts must survive
recreation; otherwise this deployment should be treated as development or
best-effort storage.

## 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173` and proxies `/api` + `/uploads` to the
backend on port 8000 (see `vite.config.js`) — so start the backend first.

Pages: Landing, Login/Signup, Scan (upload or live camera), Results
(image with concern markers + skin type + ingredients), History (saved
scans), Ask nypiel (chatbot).

### Brand system

Pulled from your logo: warm cream background, walnut-brown ink, olive/gold
accents, an arch-and-botanical motif echoed throughout (see `ArchMark.jsx`
and the rounded-arch corners on cards). Headings use **Fraunces** (serif,
matches the wordmark's character), body text uses **Inter**. All tokens
live in `tailwind.config.js` if you want to adjust the palette.

## 3. Going live

- Swap SQLite for Postgres by setting `DATABASE_URL` (backend/app/database.py)
- Move uploaded images to S3/Cloud Storage instead of local disk
- Lock CORS in `backend/app/main.py` down to your real frontend domain
- Put the frontend behind your own domain and link it from your Instagram bio
- Consider adding rate limiting to `/scan/analyze` and `/chat/ask` before
  opening this up publicly
