# Lodge Manager Frontend

Frontend application for the Lodge Manager project. It is a React, TypeScript, Vite, and Tailwind CSS application located in the `frontend` directory.

## Requirements

Install these before running the frontend:

- Git, for cloning the repository.
- Node.js `20.19.0` or newer in the Node 20 line, or Node.js `22.12.0` or newer. The current Vite tooling requires `^20.19.0 || >=22.12.0`.
- npm. npm is included with Node.js and is used by the existing `package-lock.json`.
- A terminal or command prompt.
- A modern browser such as Chrome, Edge, Firefox, or Safari.

## Getting the Requirements

### Git

Check whether Git is already installed:

```bash
git --version
```

If the command is not found, install Git from:

```text
https://git-scm.com/downloads
```

### Node.js and npm

Check whether Node.js and npm are already installed:

```bash
node --version
npm --version
```

The Node.js version must satisfy:

```text
^20.19.0 || >=22.12.0
```

Recommended installation options:

- Download the current LTS version from `https://nodejs.org/en/download`.
- Use `nvm` on macOS or Linux if you need to manage multiple Node versions.
- Use `nvm-windows` on Windows if you need to manage multiple Node versions.

After installing Node.js, reopen your terminal and verify:

```bash
node --version
npm --version
```

## Project Location

From the repository root, move into the frontend folder before running frontend commands:

```bash
cd frontend
```

All commands in the rest of this README assume you are inside the `frontend` directory.

## Install Dependencies

Install the exact dependency versions recorded in `package-lock.json`:

```bash
npm ci
```

Use `npm ci` for a clean and reproducible setup. If you are actively changing dependencies and need npm to update `package-lock.json`, use:

```bash
npm install
```

## Environment Variables

The frontend currently does not require any Vite environment variable to run.

If API integration is added later, create a local `.env` file in the `frontend` directory and use Vite's `VITE_` prefix for browser-exposed values:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Only variables prefixed with `VITE_` are exposed to frontend code by Vite.

Do not commit `.env` files or secrets. The root `.gitignore` already ignores `.env`, and `frontend/.gitignore` ignores `*.local` files.

## Run the Development Server

Start the Vite development server:

```bash
npm run dev
```

Vite will print the local URL in the terminal. By default it is usually:

```text
http://localhost:5173/
```

Open that URL in your browser.

To expose the dev server on your local network:

```bash
npm run dev -- --host
```

To run the dev server on a specific port:

```bash
npm run dev -- --port 3000
```

## Available Scripts

### Development

```bash
npm run dev
```

Runs the local Vite development server with hot module replacement.

### Production Build

```bash
npm run build
```

Runs TypeScript project checks and creates a production build in:

```text
frontend/dist
```

### Preview Production Build

```bash
npm run preview
```

Serves the built `dist` output locally. Run `npm run build` before previewing.

### Lint

```bash
npm run lint
```

Runs ESLint across the frontend source.

## Recommended First Run

From the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Then open the URL printed by Vite.

## Running With the Backend

The frontend can be run independently for current screens. If a screen begins calling the FastAPI backend, run the backend separately from the repository root.

Typical backend startup:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

On Windows, activate the virtual environment with:

```bash
venv\Scripts\activate
```

The backend normally runs at:

```text
http://127.0.0.1:8000
```

If frontend API support is added, point the frontend to that backend URL with a `VITE_API_BASE_URL` value in `frontend/.env`.

## Source Structure

```text
frontend/
|-- public/                 Static assets served by Vite
|-- src/
|   |-- components/         Reusable UI, auth, dashboard, and layout components
|   |-- hooks/              Shared React hooks
|   |-- lib/                Utilities and validation schemas
|   |-- pages/              Route-level pages
|   |-- App.tsx             Route configuration
|   |-- index.css           Global styles and Tailwind imports
|   `-- main.tsx            React application entry point
|-- index.html              Vite HTML entry
|-- package.json            npm scripts and dependency list
|-- package-lock.json       Locked dependency versions
|-- tsconfig*.json          TypeScript configuration
`-- vite.config.ts          Vite, React Compiler, Babel, and Tailwind setup
```

## Main Dependencies

- React, for the UI.
- React DOM, for rendering React in the browser.
- React Router DOM, for client-side routing.
- TypeScript, for static typing.
- Vite, for local development and production builds.
- Tailwind CSS, for styling.
- Lucide React, for icons.
- React Hook Form, for form state.
- Zod, for validation schemas.
- React Hot Toast, for toast notifications.

## Clean Reinstall

If dependencies become inconsistent, remove the installed dependency folder and reinstall from the lockfile.

macOS or Linux:

```bash
rm -rf node_modules
npm ci
```

Windows PowerShell:

```powershell
Remove-Item -Recurse -Force node_modules
npm ci
```

## Troubleshooting

### `npm ci` fails because package files are out of sync

Run:

```bash
npm install
```

Commit the updated `package-lock.json` only if the dependency changes are intentional.

### Vite says the Node.js version is unsupported

Install a supported Node.js version:

```text
^20.19.0 || >=22.12.0
```

Then reinstall dependencies:

```bash
npm ci
```

### Port `5173` is already in use

Run the dev server on another port:

```bash
npm run dev -- --port 3000
```

### Browser shows a blank page

Check the terminal running Vite for compile errors. Also open the browser developer tools console and check for runtime errors.

### API requests fail

Confirm the backend is running at the URL configured for the frontend. For local backend development, the expected backend URL is usually:

```text
http://127.0.0.1:8000
```

Also check backend CORS settings if the browser blocks requests from the frontend dev server.

## Production Output

Build the frontend:

```bash
npm run build
```

Deploy the generated `dist` directory to a static hosting provider or serve it behind a web server. The production host must be configured to return `index.html` for client-side routes such as `/login`, `/dashboard`, and `/rooms`.
