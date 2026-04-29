# 🚀 Single-Platform Deployment Guide (FastAPI + React)

This project is now configured to serve the **React Frontend** directly through the **FastAPI Backend**. This allows you to deploy everything to a single URL on one platform (like Railway or Render).

---

## 🛠️ Final Steps to Deploy

### 1. Build the Frontend
You must generate the production files for your React app:
1.  Open your terminal in the `frontend/` directory.
2.  Run the following commands:
    ```bash
    npm install
    npm run build
    ```
    *This creates a `dist/` folder.*

### 2. Move Files to the Backend
1.  Locate the `frontend/dist/` folder.
2.  Copy all its contents into the `backend/static/` folder.
    *   *Note: I have already created the `static/` folder for you in the backend.*

### 3. Final Push to GitHub
Commit the changes (including the `backend/static` files) and push:
```bash
git add .
git commit -m "feat: unified deployment with static frontend"
git push origin main
```

### 4. Deploy to Railway (Single Service)
1.  Log in to **[Railway.app](https://railway.app/)**.
2.  **New Project** → **Deploy from GitHub** → Select `DIP_learning_simulator`.
3.  **Service Settings**:
    *   **Root Directory**: `/backend`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4.  **Wait for Build**: Railway will automatically detect the Python environment and start serving your app.

---

## 🔗 Your Live Site
Once deployed, your website will be available at:
`https://your-project-name.up.railway.app/`

-   **Frontend**: Handled automatically at the root `/`.
-   **API**: Available at `/api/...`.
-   **Docs**: Interactive API documentation at `/docs`.

---

## ⚠️ Important Notes
-   **Static Files**: Every time you make changes to the React code, you must re-run `npm run build` and move the files to `backend/static` before pushing to GitHub.
-   **CORS**: Since both are on the same domain, you no longer have to worry about CORS errors in production.
-   **Environment Variables**: You don't need `VITE_API_URL` anymore, as the frontend will automatically call the same domain.
