# 🚀 MouldFlow App - Easy Deployment Guide

## ⚠️ Important: GitHub Pages Won't Work!

GitHub Pages only hosts **static HTML/CSS/JS files**. Your MouldFlow app needs:
- ✅ Backend server (Python/FastAPI) running 24/7
- ✅ Database
- ✅ API endpoints

So we need **proper hosting**. Here are 3 FREE options:

---

## 🎯 OPTION 1: Deploy to Render (EASIEST - Recommended)

Render offers FREE hosting for full-stack apps!

### Step-by-Step:

1. **Go to** [https://render.com](https://render.com)
2. **Sign up** with your GitHub account
3. **Click "New +"** → Select **"Blueprint"**
4. **Connect your repository:** `IM-MouldFlow_App_Basic1`
5. Render will **auto-detect** and deploy both frontend & backend
6. **Wait 5-10 minutes** for deployment
7. **Get your live URL!** (like `https://mouldflow-app.onrender.com`)

**That's it!** ✅

---

## 🎯 OPTION 2: Deploy to Railway.app

Railway is another great FREE option:

1. **Go to** [https://railway.app](https://railway.app)
2. **Sign in with GitHub**
3. **Click "New Project"** → **"Deploy from GitHub repo"**
4. **Select** your `IM-MouldFlow_App_Basic1` repository
5. Railway will:
   - Deploy backend automatically
   - Deploy frontend automatically
   - Give you a live URL
6. **Access your app!**

---

## 🎯 OPTION 3: Deploy Frontend to Vercel + Backend to Render

### Frontend (Vercel):
1. Go to [https://vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Select your repository
5. Set root directory to: `frontend`
6. Click Deploy
7. Get frontend URL (like `https://mouldflow.vercel.app`)

### Backend (Render):
1. Go to [https://render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repo
4. Set root directory to: `backend`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Deploy!

### Connect them:
- Update frontend `.env` file with backend URL from Render

---

## 📊 What You Get:

✅ **Live URL** you can access from ANY browser
✅ **24/7 uptime** (not just when your computer is on)
✅ **Shareable link** (send to others to test)
✅ **FREE** (all platforms have free tiers)

---

## ⚡ FASTEST METHOD RIGHT NOW:

**Use Render Blueprint (Option 1)** - it's literally 2 clicks and 10 minutes wait!

1. Create Render account
2. Connect GitHub
3. Click Deploy
4. Done! ✅

---

## 🆘 Need Help?

If you get stuck, just tell me which platform you chose and where you're stuck. I'll guide you through!

The app is 100% ready to deploy - all configuration files are already included!
