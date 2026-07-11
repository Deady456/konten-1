# ============================================================
# FreeFaceless - Music Asset Setup
# ============================================================
# Run this script to set up the music directory structure
# and download free royalty-free music.

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FreeFaceless - Music Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create music directory
$musicDir = "assets\music"
if (-not (Test-Path $musicDir)) {
    New-Item -ItemType Directory -Path $musicDir -Force | Out-Null
    Write-Host "[OK] Created $musicDir" -ForegroundColor Green
} else {
    Write-Host "[OK] $musicDir already exists" -ForegroundColor Green
}

# Create mood subdirectories
$moods = @("upbeat", "cinematic", "neutral", "mysterious", "dramatic")
foreach ($mood in $moods) {
    $moodDir = "$musicDir\$mood"
    if (-not (Test-Path $moodDir)) {
        New-Item -ItemType Directory -Path $moodDir -Force | Out-Null
        Write-Host "[OK] Created $moodDir" -ForegroundColor Green
    }
}

# Create README with music sources
$readme = @"
# Free Royalty-Free Music Sources
# ================================
#
# Download music from these sources and place them in the correct mood folder:
#
# 1. Pixabay Music (FREE)
#    https://pixabay.com/music/
#    - No attribution required
#    - Download as MP3
#    - Place in assets/music/<mood>/
#
# 2. YouTube Audio Library (FREE)
#    https://studio.youtube.com/channel/UC/music
#    - Free for YouTube videos
#    - Download as MP3
#    - Place in assets/music/<mood>/
#
# 3. Uppbeat (FREE tier)
#    https://uppbeat.io/
#    - Free for non-commercial
#    - Place in assets/music/<mood>/
#
# 4. Free Music Archive
#    https://freemusicarchive.org/
#    - Check license per track
#    - Place in assets/music/<mood>/
#
# Mood Guide:
# - upbeat: Ceria, energi, fakta menarik
# - cinematic: Dramatis, petualangan, sejarah
# - neutral: Netral, informatif, edukasi
# - mysterious: Misterius, teka-teki, mitos
# - dramatic: Tegang, surprise, myth busting
#
# Tips:
# - Gunakan 3-5 lagu per mood untuk variasi
# - Panjang ideal: 60-120 detik
# - Hindari lagu dengan vokal (ganggu narasi)
# - Volume akan diatur otomatis oleh pipeline

"@

$readme | Out-File -FilePath "$musicDir\README.txt" -Encoding UTF8
Write-Host "[OK] Created $musicDir\README.txt" -ForegroundColor Green

# Create branding directory
$brandingDir = "assets\branding"
if (-not (Test-Path $brandingDir)) {
    New-Item -ItemType Directory -Path $brandingDir -Force | Out-Null
    Write-Host "[OK] Created $brandingDir" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Download free music from links above" -ForegroundColor White
Write-Host "  2. Place MP3 files in assets/music/<mood>/" -ForegroundColor White
Write-Host "  3. (Optional) Add intro/outro/watermark to assets/branding/" -ForegroundColor White
Write-Host ""
