# Vercel Configuration Notes

## ⚠️ IMPORTANT: Vercel Limitations

Your app is currently configured to work on Vercel, but there are critical limitations:

### 1. **Ephemeral Filesystem**
- `/tmp` directory is the ONLY writable location
- Files in `/tmp` are deleted between function invocations
- **Your database and uploads WILL NOT persist**

### 2. **Current Configuration**
- Database: SQLite in `/tmp/astrology_app.db` (resets on each cold start)
- Uploads: Stored in `/tmp/uploads` (deleted after function ends)

### 3. **What This Means**
- ❌ Data submitted by users will be LOST
- ❌ Uploaded photos and fingerprints will DISAPPEAR
- ❌ PDF reports can't be generated with stored data
- ✅ App will run without crashing
- ✅ Good for UI/UX testing only

## 🔧 REQUIRED for Production

To make this work properly on Vercel, you MUST:

### Option 1: Use PostgreSQL (Recommended)
1. Sign up for free PostgreSQL:
   - **Neon**: https://neon.tech (Best for Vercel)
   - **Supabase**: https://supabase.com
   - **Railway**: https://railway.app

2. Get connection string (looks like):
   ```
   postgresql://user:password@host:5432/database
   ```

3. Add to Vercel Environment Variables:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

4. Add to `requirements.txt`:
   ```
   psycopg2-binary==2.9.9
   ```

5. Update `app.py`:
   ```python
   # Replace postgres:// with postgresql:// for SQLAlchemy
   db_url = os.environ.get("DATABASE_URL", f"sqlite:///{db_path}")
   if db_url.startswith("postgres://"):
       db_url = db_url.replace("postgres://", "postgresql://", 1)
   app.config["SQLALCHEMY_DATABASE_URI"] = db_url
   ```

### Option 2: Use Vercel Blob Storage (for files)
1. Enable Vercel Blob in your project
2. Install SDK: `pip install vercel-blob`
3. Update `utils.py` to use Blob storage instead of local files

### Option 3: Use External Services
- **Database**: PlanetScale, CockroachDB, MongoDB Atlas
- **File Storage**: AWS S3, Cloudflare R2, Backblaze B2

## 🚀 Quick PostgreSQL Setup (5 minutes)

### Using Neon (Recommended)
1. Go to https://console.neon.tech
2. Sign up (free)
3. Create new project
4. Copy connection string
5. In Vercel Dashboard:
   - Settings → Environment Variables
   - Add: `DATABASE_URL` = your connection string
6. Redeploy

### Update Code for PostgreSQL
Run these commands in your project:

```powershell
# Add PostgreSQL support
Add-Content requirements.txt "`npsycopg2-binary==2.9.9"

# Commit
git add requirements.txt
git commit -m "Add PostgreSQL support"
git push origin deploy
```

## 📊 Current Status

✅ App deploys successfully  
✅ UI works  
⚠️ **Data does NOT persist** (SQLite in /tmp)  
⚠️ **Files do NOT persist** (uploads in /tmp)  
❌ Not production-ready  

## 💡 Alternative: Deploy to Railway/Render

If you don't want to deal with PostgreSQL complexity:

### Railway (Easiest)
- Supports SQLite with persistent storage
- One-click PostgreSQL
- Automatic deployments
- Free tier available

### Render
- Supports persistent disk
- Built-in PostgreSQL
- Auto SSL
- Free tier available

Both are easier for SQLite-based Flask apps than Vercel.

## 🎯 Bottom Line

**For Demo/Preview**: Current setup works fine  
**For Production**: MUST add PostgreSQL before going live  

Choose your path and I can help you implement it!
