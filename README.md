# TestConvetorExcel

Modern document to Excel conversion MVP built with Next.js and FastAPI.

## Vercel Deployment

Deploy the frontend from the `frontend` folder.

- Framework preset: `Next.js`
- Root directory: `frontend`
- Build command: `npm run build`
- Install command: `npm install`
- Environment variable: `NEXT_PUBLIC_API_URL=<your deployed FastAPI backend URL>`

The FastAPI backend must be deployed separately on a Python host such as Render, Railway, or a VPS. Localhost backend URLs will not work from Vercel.
