# Setting up the integration worktree on another computer

This assumes the repo, venv, Postgres/pgvector and `demo_db` are already set up on that computer.
The only thing missing is the second folder with the frontend:

| Folder | Branch | Contents |
|---|---|---|
| `Documents\GitHub\SimsSSG` | `vincent-work` | backend only (already set up) |
| `Documents\GitHub\SimsSSG-integration` | `vincent-frontend-integration` | backend + Pennie's React frontend |

Both folders share one git repository, so there's nothing new to clone.

Requires **Node.js** (check with `node --version`).

## 1. Create the worktree

From the existing `SimsSSG` folder:
```powershell
git fetch
git worktree add ..\SimsSSG-integration vincent-frontend-integration
```
This creates `SimsSSG-integration` next to `SimsSSG`, already on the branch with the frontend and
the Admin page.

## 2. Python: reuse the existing venv

`.venv` isn't in git, so the new folder doesn't have one. Reuse the one in `SimsSSG`:
```powershell
cd ..\SimsSSG-integration
..\SimsSSG\.venv\Scripts\Activate.ps1
```
In VS Code (with `SimsSSG-integration` open): `Ctrl+Shift+P` → **Python: Select Interpreter** →
pick `SimsSSG\.venv\Scripts\python.exe`.

This works as long as the two branches have the same `requirements.txt`. If they ever differ, create
a separate `.venv` in the integration folder.

## 3. Install the frontend

`node_modules` isn't in git either:
```powershell
cd frontend
npm install
git restore package-lock.json     # npm install rewrites it; don't commit that change
```

## 4. Run both

**Terminal 1: backend from the integration folder.** Start it the same way as in `SimsSSG`, but
from `SimsSSG-integration`. Only this version has CORS enabled and the `GET /employees/{emp_id}/`
route that the Admin page uses. Stop the `SimsSSG` backend first if it's running, since both use
port 8000.

**Terminal 2: frontend.**
```powershell
cd $HOME\Documents\GitHub\SimsSSG-integration\frontend
npm run dev
```
Open `http://localhost:5173/admin`.

The database on this computer has different employees than the first one. If the list is empty,
add one with a POST in `http://localhost:8000/docs`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `fatal: invalid reference: vincent-frontend-integration` | Run `git fetch` first |
| `'...SimsSSG-integration' already exists` | A folder with that name is already there. Remove or rename it. |
| Admin page says *"Could not reach backend"* | The backend isn't running, or it was started from `SimsSSG` instead of `SimsSSG-integration`. Press F12 → Console for details. |

## Pushing from this computer

In `SimsSSG-integration`: `git add ...`, `git commit -m "..."`, `git push`. That goes to
`vincent-frontend-integration` and doesn't affect `master` or `vincent-work`.

To delete the worktree later: `git worktree remove ..\SimsSSG-integration` (from `SimsSSG`).
