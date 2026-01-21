# compile.ps1 - Compila e mantiene solo il .exe
param(
    [string]$ScriptPath,
    [switch]$KeepConsole = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMPILATORE PULITO PYTHON -> .EXE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verifica parametri
if (-not $ScriptPath) {
    Write-Host "❌ Errore: Specifica un file .py" -ForegroundColor Red
    Write-Host "Esempio: .\compile.ps1 -ScriptPath 'mio_script.py'" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Host "❌ Errore: File '$ScriptPath' non trovato" -ForegroundColor Red
    exit 1
}

$scriptFile = Get-Item $ScriptPath
$scriptName = $scriptFile.BaseName
$scriptDir = $scriptFile.DirectoryName

Write-Host "`nScript: $($scriptFile.FullName)" -ForegroundColor White
Write-Host "Nome: $scriptName" -ForegroundColor White
Write-Host "Cartella: $scriptDir" -ForegroundColor White

# 1. Installa PyInstaller se necessario
Write-Host "`n[1/5] Verifica PyInstaller..." -ForegroundColor Gray
try {
    pip install pyinstaller --quiet 2>&1 | Out-Null
    Write-Host "  ✓ PyInstaller pronto" -ForegroundColor Green
} catch {
    Write-Host "  ℹ PyInstaller già installato" -ForegroundColor Yellow
}

# 2. Crea cartella temporanea
Write-Host "[2/5] Creazione ambiente temporaneo..." -ForegroundColor Gray
$tempDir = Join-Path $env:TEMP "pyinstaller_$(Get-Random)"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# 3. Costruisci comando PyInstaller
Write-Host "[3/5] Compilazione in corso..." -ForegroundColor Gray
$pyinstallerArgs = @(
    "--onefile",
    "--distpath", $tempDir,
    "--workpath", (Join-Path $tempDir "build"),
    "--specpath", $tempDir
)

if (-not $KeepConsole) {
    $pyinstallerArgs += "--noconsole"
}

$pyinstallerArgs += $scriptFile.FullName

# 4. Esegui PyInstaller
try {
    pyinstaller @pyinstallerArgs 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller fallito con codice $LASTEXITCODE"
    }
    
    Write-Host "  ✓ Compilazione completata" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Errore nella compilazione: $_" -ForegroundColor Red
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

# 5. Trova e sposta il .exe
Write-Host "[4/5] Spostamento .exe..." -ForegroundColor Gray
$exeTempPath = Join-Path $tempDir "$scriptName.exe"

if (-not (Test-Path $exeTempPath)) {
    $exeTempPath = Get-ChildItem -Path $tempDir -Filter "*.exe" | Select-Object -First 1 -ExpandProperty FullName
}

if (-not $exeTempPath) {
    Write-Host "  ❌ Nessun .exe trovato" -ForegroundColor Red
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

# Destinazione finale (nella stessa cartella dello script)
$exeDestPath = Join-Path $scriptDir "$scriptName.exe"

# Se esiste già, aggiungi numero
$counter = 1
while (Test-Path $exeDestPath) {
    $exeDestPath = Join-Path $scriptDir "${scriptName}_${counter}.exe"
    $counter++
}

Move-Item $exeTempPath $exeDestPath -Force
Write-Host "  ✓ .exe spostato in: $exeDestPath" -ForegroundColor Green

# 6. Mostra informazioni
$exeSize = (Get-Item $exeDestPath).Length / 1MB
Write-Host "  📏 Dimensione: $($exeSize.ToString('0.00')) MB" -ForegroundColor Cyan

# 7. Pulisci
Write-Host "[5/5] Pulizia file temporanei..." -ForegroundColor Gray
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  ✓ File temporanei eliminati" -ForegroundColor Green

# 8. Risultato finale
Write-Host "`n" + "="*40 -ForegroundColor Green
Write-Host "✅ COMPILAZIONE PULITA COMPLETATA!" -ForegroundColor Green
Write-Host "="*40 -ForegroundColor Green
Write-Host "📁 Il tuo .exe è qui:" -ForegroundColor White
Write-Host "   $exeDestPath" -ForegroundColor Yellow
Write-Host "`n🧹 Nessun altro file è stato creato!" -ForegroundColor Green
Write-Host "="*40 -ForegroundColor Green

# 9. Chiedi se aprire la cartella
$response = Read-Host "`nVuoi aprire la cartella contenente il .exe? (s/n)"
if ($response -eq 's') {
    explorer /select,"$exeDestPath"
}
