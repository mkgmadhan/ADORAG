# ADO RAG Setup Script
# This script helps set up the development environment

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  ADO RAG Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher from https://www.python.org/" -ForegroundColor Red
    exit 1
}

Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Check if Python version is 3.10+
$versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
if ($versionMatch) {
    $majorVersion = [int]$Matches[1]
    $minorVersion = [int]$Matches[2]
    
    if (($majorVersion -lt 3) -or (($majorVersion -eq 3) -and ($minorVersion -lt 10))) {
        Write-Host "ERROR: Python 3.10 or higher is required" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    $response = Read-Host "Virtual environment already exists. Recreate? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "Virtual environment recreated" -ForegroundColor Green
    } else {
        Write-Host "Using existing virtual environment" -ForegroundColor Green
    }
} else {
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}

Write-Host "Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes)" -ForegroundColor Cyan
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "Dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ".env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Please edit .env file with your Azure credentials" -ForegroundColor Yellow
    Write-Host "Required values:" -ForegroundColor Yellow
    Write-Host "  - ADO_ORGANIZATION" -ForegroundColor Cyan
    Write-Host "  - ADO_PROJECT_NAME" -ForegroundColor Cyan
    Write-Host "  - ADO_PAT" -ForegroundColor Cyan
    Write-Host "  - AZURE_OPENAI_ENDPOINT" -ForegroundColor Cyan
    Write-Host "  - AZURE_OPENAI_KEY" -ForegroundColor Cyan
    Write-Host "  - AZURE_SEARCH_ENDPOINT" -ForegroundColor Cyan
    Write-Host "  - AZURE_SEARCH_KEY" -ForegroundColor Cyan
    Write-Host ""
    $openEditor = Read-Host "Open .env file for editing now? (Y/n)"
    if ($openEditor -ne 'n' -and $openEditor -ne 'N') {
        notepad .env
    }
} else {
    Write-Host ".env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Ensure .env file is configured with your credentials" -ForegroundColor White
Write-Host "2. Run the application with:" -ForegroundColor White
Write-Host "   streamlit run app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed instructions, see QUICKSTART.md" -ForegroundColor Yellow
Write-Host ""

# Offer to run the application
$runNow = Read-Host "Would you like to run the application now? (y/N)"
if ($runNow -eq 'y' -or $runNow -eq 'Y') {
    Write-Host ""
    Write-Host "Starting ADO RAG application..." -ForegroundColor Green
    Write-Host ""
    streamlit run app.py
}
