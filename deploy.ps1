$envFile = ".env"
$dbFile = "site.db"
$deployHook = "<YOUR_RENDER_DEPLOY_HOOK_URL>"

# Check .env
if (!(Test-Path $envFile)) {
    Write-Error ".env file is missing. Please create one with your secret keys and API settings."
    exit 1
}

Write-Output "✅ .env file found:"
Get-Content $envFile | ForEach-Object { Write-Output "`t$_" }

# Check if database exists
if (!(Test-Path $dbFile)) {
    Write-Output "🔧 site.db not found. Creating initial database..."

    $env:FLASK_APP = "app.py"
    python -c "from db import db; db.create_all()"

    if (Test-Path $dbFile) {
        Write-Output "✅ Database created successfully."
    } else {
        Write-Error "❌ Failed to create database."
        exit 1
    }
} else {
    Write-Output "✅ Database already exists."
}

# Trigger Render deploy
if ($deployHook -ne "<YOUR_RENDER_DEPLOY_HOOK_URL>") {
    Write-Output "🚀 Triggering Render deploy..."
    Invoke-RestMethod -Method POST -Uri $deployHook
    Write-Output "✅ Deploy hook triggered."
} else {
    Write-Warning "⚠️ Please replace '<YOUR_RENDER_DEPLOY_HOOK_URL>' with your actual Render deploy hook URL."
}

Read-Host "`nScript completed. Press Enter to close the window"
