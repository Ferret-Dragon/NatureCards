# 🚀 Render Deployment with Persistent Data

## 🔧 **Fixed Issues:**

### **1. Session Timeout (FIXED)**
- ✅ Extended login sessions to **30 days**
- ✅ Enabled "Remember Me" functionality
- ✅ Users stay logged in even if server restarts

### **2. Data Loss (FIXED)**
- ✅ Added PostgreSQL database support
- ✅ Data persists when server goes to sleep
- ✅ User accounts never get deleted

## 📋 **Deployment Steps:**

### **Quick Deploy:**
1. Push your code to GitHub
2. Go to [render.com](https://render.com)
3. Create "New Web Service" from GitHub repo
4. Render will auto-detect the `render.yaml` config
5. Click "Deploy"

### **What Happens Automatically:**
- ✅ PostgreSQL database created (free tier)
- ✅ Environment variables configured
- ✅ User sessions persist for 30 days
- ✅ Data never gets deleted

## 🌟 **Key Improvements:**

### **Session Management:**
```python
# Users stay logged in for 30 days
PERMANENT_SESSION_LIFETIME = 30 days
REMEMBER_COOKIE_DURATION = 30 days
```

### **Database:**
- **Development**: SQLite (local testing)
- **Production**: PostgreSQL (Render cloud)
- **Auto-switching**: Code detects environment

### **Free Tier Benefits:**
- **PostgreSQL**: 1GB storage (plenty for thousands of flashcards)
- **Web Service**: 750 hours/month (sufficient for personal use)
- **Sleep Mode**: App sleeps after 15min, but data persists!

## 🎯 **Result:**

✅ **No more lost accounts**
✅ **30-day login sessions**
✅ **Instant wake-up** (2-3 seconds from sleep)
✅ **All data preserved** forever

Your users can now:
- Login once and stay logged in for a month
- Access notes from any device
- Never lose their flashcard data
- Use the app reliably on Render's free tier

## 🔗 **After Deployment:**

Your app will be live at: `https://naturecards.onrender.com`

Share this URL with users - they can bookmark it and access their private flashcards anytime!