@echo off
cd /d "%~dp0"
echo ========================================================
echo Membuka browser untuk otorisasi YouTube...
echo Silakan login dengan akun Google Anda dan klik Allow/Izinkan.
echo ========================================================
python -c "from src.upload import get_service; get_service()"

if not exist "token_default.json" (
    echo [Error] Gagal mendapatkan token.
    pause
    exit /b
)

echo ========================================================
echo Token berhasil didapatkan! Menyebarkan ke 8 Repository...
echo ========================================================
powershell -Command "$tokenB64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes('token_default.json')); $repos = @('konten-1', 'konten-2', 'konten3', 'konten4', 'konten5', 'konten6', 'konten-web-ai', 'sainstek'); foreach ($repo in $repos) { Write-Host 'Mengupdate' $repo'...'; echo $tokenB64 | gh secret set TOKEN_B64 -R 'Deady456/$repo' }"

echo ========================================================
echo SELESAI! Semua token YouTube di 8 repo sudah diupdate!
echo Anda bisa menutup jendela ini.
echo ========================================================
pause
