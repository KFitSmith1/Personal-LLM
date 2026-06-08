# Integration: Open Notebook as a tab in Open-Generative-AI

Embed your private NotebookLM (Open Notebook from the main stack) as a
**Notebook Studio** tab inside [anil-matcha/open-generative-ai](https://github.com/anil-matcha/open-generative-ai),
so one dashboard gives you image/video/audio studios **and** source-based
research chat.

This is the **iframe sidecar** approach: lowest friction, no rewrite of either
project. (A deeper API-native integration is sketched at the bottom.)

```
Browser ── Open-Generative-AI (:3001)
              ├── Image / Video / Audio / Workflow / Agent studios
              └── Notebook Studio tab ──iframe──▶ Open Notebook (:8502)
                                                      └── Ollama (:11434)
```

> The studio's actual structure was verified against `main`: tabs live in a
> `TABS` array of `{ id, label }`, the active tab is `useState`, and each body
> renders via `{activeTab === 'x' && <Component />}`. The three edits below match
> that exactly.

---

## Prerequisites

- The Personal-LLM stack from this repo is running (`docker compose up -d`), so
  Open Notebook is live on `:8502`.
- A fork/clone of `open-generative-ai`. Clone **with submodules** — the workflow
  and agent packages are git submodules:
  ```bash
  git clone --recurse-submodules https://github.com/anil-matcha/open-generative-ai.git ../open-generative-ai
  cd ../open-generative-ai && npm run setup   # plain `npm install` is not enough
  ```

---

## Step 1 — Add the component

Copy [`NotebookStudio.js`](./NotebookStudio.js) into the studio fork:

```bash
cp integrations/open-generative-ai/NotebookStudio.js \
   ../open-generative-ai/components/NotebookStudio.js
```

## Step 2 — Make three edits in `components/StandaloneShell.js`

**a) Import it** (near the other component imports at the top):
```js
import NotebookStudio from './NotebookStudio';
```

**b) Register the tab** — add one entry to the `TABS` array:
```js
const TABS = [
  { id: 'image', label: 'Image Studio' },
  // ...existing entries...
  { id: 'notebook', label: 'Notebook Studio' },   // <-- add
];
```

**c) Render it** — add one line next to the other `activeTab === ...` blocks:
```jsx
{activeTab === 'notebook' && <NotebookStudio />}
```

## Step 3 — Point the iframe at your Open Notebook

The iframe loads in the **browser**, so the URL must be reachable from your
machine — your server's host/IP, not a Docker service name.

```bash
# in ../open-generative-ai/.env.local
NEXT_PUBLIC_NOTEBOOK_URL=http://<your-server-ip>:8502
```

## Step 4 — Run

Dev:
```bash
cd ../open-generative-ai && npm run dev
# open http://localhost:3000  -> Notebook Studio tab
```

Or run it as a container alongside this stack using the provided overlay:
```bash
# from THIS repo's root
docker compose \
  -f docker-compose.yml \
  -f integrations/open-generative-ai/compose.add-open-generative-ai.yml \
  up -d --build
# studio -> http://<server-ip>:3001
```

---

## Notes & gotchas

- **Iframe blocked / blank?** Open Notebook may send `X-Frame-Options` /
  CSP `frame-ancestors` that refuse embedding. If so, put both behind one
  reverse proxy (same origin) or strip those headers at the proxy for the
  Notebook route. Same-origin is the reliable fix.
- **Don't expose `:8502` publicly** just to make the iframe work — front it with
  HTTPS + the basic-auth already configured in the main stack.
- **Two `restart`/port maps**: the studio uses `3001` here to avoid clashing
  with Open WebUI on `3000`.

---

## Deeper option (later): API-native, no iframe

Instead of embedding the whole UI, build a native React tab that calls Open
Notebook's REST API (`:5055`) through Next.js proxy routes — avoids CORS and
feels like one app:

```
app/api/notebook/[...]/route.js  ──▶  http://open_notebook:5055/...
components/NotebookStudio.js      ──▶  fetch('/api/notebook/...')
```

Do this only after the iframe version proves the workflow is what you want.
