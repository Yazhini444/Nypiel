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

Drop your files here:

```
backend/weights/nypiel_skin_type_model.pth  <- your skin-type ResNet-18 classifier
backend/weights/best.pt                     <- your YOLO concern detector
```

That's it for the concern model — `best.pt` is already wired up via
`ultralytics.YOLO`, which reads its 10 class names directly from the file
itself, runs detection, and converts each box to `[x, y, w, h]` as a
fraction of image size so the frontend can draw markers regardless of
display size. `pip install -r requirements.txt` already includes
`ultralytics`.

For the skin-type model, `app/inference.py` handles the common case
automatically: if you saved it with `torch.save(model)` (the whole model,
not just weights), it loads and runs as-is. If you saved only a
`state_dict` (`torch.save(model.state_dict())`), you'll see a clear error
telling you to rebuild your model architecture (e.g. `resnet18(...)`) in
`load_models()` and load the state_dict into it — there's a code example
already written in that function's comments, just uncomment and adjust it
to whatever architecture you trained.

Also double check `_preprocess_for_classifier()` in that same file — it
assumes standard 224×224 ImageNet preprocessing. Change the resize and
normalization values there if your training pipeline used something
different.

If either file is missing, that model quietly falls back to mock
predictions (logged to the console on startup) so the rest of the app —
auth, saving, recommendations, chat, UI — stays fully testable without
blocking on the models.

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
