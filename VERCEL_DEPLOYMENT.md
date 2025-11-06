# Vercel Deployment Guide

## 📦 Pre-Deployment Checklist

✅ Files created:
- `vercel.json` - Vercel configuration
- `runtime.txt` - Python version specification
- `.env.example` - Environment variables template
- `.gitignore` - Updated for Vercel
- `requirements.txt` - Dependencies listed

## 🚀 Deployment Steps

### 1. Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Vercel deployment"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 2. Vercel Dashboard Configuration

When deploying on Vercel, use these settings:

#### Framework Preset
- Select: **Other**

#### Root Directory
- Value: `./`

#### Build Command
- Leave **EMPTY** (Vercel auto-detects)

#### Output Directory
- Leave as: **N/A**

#### Install Command
- Use: `pip install -r requirements.txt`

### 3. Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

| Key | Value | Description |
|-----|-------|-------------|
| `SESSION_SECRET` | `generate-random-32-char-string` | Flask session secret |
| `FLASK_ENV` | `production` | Flask environment |
| `DATABASE_URL` | `sqlite:///astrology_app.db` | Database path |

**Generate SESSION_SECRET:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Deploy

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure settings as above
5. Add environment variables
6. Click "Deploy"

## ⚠️ Important Notes

### SQLite Limitations on Vercel
Vercel is serverless, so SQLite won't persist data between deployments. For production:

**Option 1: Use PostgreSQL (Recommended)**
- Add to requirements.txt: `psycopg2-binary`
- Use a hosted PostgreSQL (e.g., Neon, Supabase, Railway)
- Update `DATABASE_URL` environment variable

**Option 2: Continue with SQLite (Testing Only)**
- Data will reset on each deployment
- Good for demos/previews only

### File Uploads
Vercel has ephemeral file system. Uploaded files won't persist. For production:
- Use cloud storage (AWS S3, Cloudflare R2, etc.)
- Or use Vercel Blob Storage

### Static Files
Your `static/` folder will work fine, but uploads in `static/uploads/` won't persist.

## 🔄 PostgreSQL Migration (Production)

To use PostgreSQL instead of SQLite:

1. **Update requirements.txt:**
```
psycopg2-binary
```

2. **Update app.py database config:**
```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///astrology_app.db"
).replace('postgres://', 'postgresql://')  # Fix for some providers
```

3. **Get PostgreSQL URL:**
   - Neon: https://neon.tech (Free tier available)
   - Supabase: https://supabase.com (Free tier available)
   - Railway: https://railway.app (Pay as you go)

4. **Add to Vercel Environment Variables:**
```
DATABASE_URL=postgresql://user:password@host:port/database
```

## 🧪 Testing Locally with Production Settings

```bash
# Set environment variables (Windows PowerShell)
$env:SESSION_SECRET="your-secret-key"
$env:FLASK_ENV="production"

# Run app
python app.py
```

## 📝 Post-Deployment

1. Visit your Vercel URL (e.g., `your-app.vercel.app`)
2. Test all features:
   - Face capture
   - Personal details form
   - Fingerprint uploads
   - PDF generation
3. Check Vercel logs for any errors

## 🐛 Troubleshooting

### Build Fails
- Check Python version in `runtime.txt` matches requirements
- Verify all dependencies in `requirements.txt`
- Check Vercel build logs

### App Doesn't Load
- Check environment variables are set
- Verify `vercel.json` configuration
- Check Vercel function logs

### Database Errors
- SQLite won't persist on Vercel
- Migrate to PostgreSQL for production
- Check database connection string

### File Upload Issues
- Vercel has read-only filesystem (except /tmp)
- Use cloud storage for production
- For testing, files will work but won't persist

## 🔒 Security Checklist

- ✅ Change `SESSION_SECRET` to random value
- ✅ Set `FLASK_ENV=production`
- ✅ Never commit `.env` file
- ✅ Use HTTPS (Vercel provides automatically)
- ✅ Review CORS settings if adding API
- ✅ Consider rate limiting for production

## 📚 Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
- [SQLAlchemy with PostgreSQL](https://docs.sqlalchemy.org/en/latest/dialects/postgresql.html)

## 🎉 Success!

Once deployed, your app will be available at:
- Production: `https://your-app.vercel.app`
- Preview: Automatic preview URLs for each commit
- Local: `http://localhost:5000`

Remember to remove the preview watermark before final client delivery!
