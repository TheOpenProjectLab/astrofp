# Quick Deployment Script
# Run this before pushing to GitHub

Write-Host "🚀 Preparing for Vercel Deployment..." -ForegroundColor Green

# Generate a secure session secret
Write-Host "`n📝 Generating SESSION_SECRET..." -ForegroundColor Yellow
$secret = python -c "import secrets; print(secrets.token_hex(32))"
Write-Host "Copy this to Vercel Environment Variables:" -ForegroundColor Cyan
Write-Host "SESSION_SECRET=$secret" -ForegroundColor White

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "`n📦 Initializing Git repository..." -ForegroundColor Yellow
    git init
}

# Add all files
Write-Host "`n📦 Adding files to Git..." -ForegroundColor Yellow
git add .

# Show status
Write-Host "`n📊 Git Status:" -ForegroundColor Yellow
git status

Write-Host "`n✅ Ready to commit and push!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Run: git commit -m 'Deploy to Vercel'" -ForegroundColor White
Write-Host "2. Create GitHub repo if needed" -ForegroundColor White
Write-Host "3. Run: git remote add origin YOUR_GITHUB_URL" -ForegroundColor White
Write-Host "4. Run: git push -u origin main" -ForegroundColor White
Write-Host "5. Go to vercel.com and import your GitHub repo" -ForegroundColor White
Write-Host "`n📋 Remember to add these Environment Variables in Vercel:" -ForegroundColor Yellow
Write-Host "   SESSION_SECRET=$secret" -ForegroundColor White
Write-Host "   FLASK_ENV=production" -ForegroundColor White
Write-Host "   DATABASE_URL=sqlite:///astrology_app.db" -ForegroundColor White
