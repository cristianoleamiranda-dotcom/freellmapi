# Preflight para instalar FooocusPlus con Pinokio (Windows / PowerShell).
# Uso:  powershell -ExecutionPolicy Bypass -File scripts\preflight.ps1 [-MinDiskGB 50]
# Salida: informe legible + exit 0 (listo o listo con avisos), 1 (bloqueante).

[CmdletBinding()]
param([int]$MinDiskGB = 50)

$ErrorActionPreference = 'SilentlyContinue'
$blockers = 0
$warnings = 0

function Write-Ok   { param($m) Write-Host "  OK    $m" -ForegroundColor Green }
function Write-Warn2{ param($m) Write-Host "  WARN  $m" -ForegroundColor Yellow; $script:warnings++ }
function Write-Bad  { param($m) Write-Host "  FAIL  $m" -ForegroundColor Red; $script:blockers++ }
function Write-Info { param($m) Write-Host "  .     $m" -ForegroundColor DarkGray }
function Write-Head { param($m) Write-Host ""; Write-Host $m -ForegroundColor Cyan }

Write-Host "FooocusPlus . preflight"
Write-Info "sistema: $([System.Environment]::OSVersion.VersionString) ($env:PROCESSOR_ARCHITECTURE)"

# ---------------------------------------------------------------- GPU
Write-Head "GPU"
$vramMB = 0
$gpuKind = 'none'
$gpuName = ''
$smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($smi) {
  $q = & nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>$null
  if ($q) {
    $gpuKind = 'nvidia'
    $first = ($q | Select-Object -First 1)
    $parts = $first -split ','
    $gpuName = $parts[0].Trim()
    $vramMB = [int](($parts[1] -replace '[^0-9]', ''))
    $driver = if ($parts.Count -ge 3) { $parts[2].Trim() } else { '?' }
    Write-Ok "NVIDIA detectada: $gpuName ($vramMB MB VRAM, driver $driver)"
  }
}
if ($gpuKind -eq 'none') {
  $cards = Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name
  if ($cards) {
    $gpuName = ($cards -join ' | ')
    if ($gpuName -match 'NVIDIA') {
      Write-Warn2 "GPU NVIDIA presente pero nvidia-smi no responde: instala/actualiza el driver"
    } elseif ($gpuName -match 'AMD|Radeon') {
      Write-Warn2 "AMD en Windows: soporte parcial en FooocusPlus ($gpuName)"
    } else {
      Write-Warn2 "Sin GPU acelerada reconocida ($gpuName): arrancará con --always-cpu"
    }
  } else {
    Write-Warn2 "No se detectó GPU: arrancará con --always-cpu (muy lento)"
  }
}

if ($gpuKind -eq 'nvidia') {
  if ($vramMB -ge 12000)     { Write-Ok "VRAM suficiente para Flux (12 GB recomendados)" }
  elseif ($vramMB -ge 8000)  { Write-Ok "VRAM suficiente para SDXL; Flux irá justo" }
  elseif ($vramMB -ge 6000)  { Write-Warn2 "6-7 GB: solo presets SDXL ligeros; Flux no es viable" }
  else                       { Write-Warn2 "Menos de 6 GB: usa presets de VRAM baja o SD1.5" }
}

# ---------------------------------------------------------------- RAM y swap
Write-Head "Memoria"
$ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
$cores = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfCores -Sum).Sum
if ($ramGB -ge 32)     { Write-Ok "RAM: $ramGB GB (32 para SDXL, 48 para Flux)" }
elseif ($ramGB -ge 16) { Write-Ok "RAM: $ramGB GB (suficiente para SDXL)" }
else                   { Write-Bad "RAM: $ramGB GB - por debajo del mínimo de 16 GB" }
Write-Info "núcleos de CPU: $cores"

$os = Get-CimInstance Win32_OperatingSystem
$autoManaged = (Get-CimInstance Win32_ComputerSystem).AutomaticManagedPagefile
$pageBytes = $os.TotalVirtualMemorySize - $os.TotalVisibleMemorySize
$pageGB = [math]::Round($pageBytes * 1KB / 1GB, 1)
if ($autoManaged) {
  Write-Ok "Pagefile gestionado por Windows (~$pageGB GB): deja al menos 40 GB libres por disco"
} elseif ($pageGB -ge 20) {
  Write-Ok "Pagefile: ~$pageGB GB"
} else {
  Write-Warn2 "Pagefile manual pequeño (~$pageGB GB): el troubleshoot pide ~40 GB o gestión automática"
}

# ---------------------------------------------------------------- disco
Write-Head "Disco"
$freeGB = [math]::Round((Get-PSDrive -Name ($env:SystemDrive.TrimEnd(':'))).Free / 1GB)
if ($freeGB -ge $MinDiskGB)     { Write-Ok "Libre en $env:SystemDrive : $freeGB GB (mínimo $MinDiskGB GB)" }
elseif ($freeGB -ge 20)         { Write-Warn2 "Libre en $env:SystemDrive : $freeGB GB - alcanza para instalar, no para Flux + SDXL" }
else                            { Write-Bad "Libre en $env:SystemDrive : $freeGB GB - insuficiente (mínimo 50 GB)" }
Write-Info "desglose típico: entorno Python 10-15 GB + modelos 6-25 GB por familia"

# ---------------------------------------------------------------- herramientas
Write-Head "Herramientas"
foreach ($t in @('git','curl')) {
  if (Get-Command $t -ErrorAction SilentlyContinue) { Write-Ok "$t encontrado" }
  else { Write-Bad "$t no encontrado (lo necesita el launcher; git viene con Git for Windows)" }
}
if (Get-Command uv -ErrorAction SilentlyContinue) { Write-Ok "uv: $((& uv --version) 2>$null)" }
else { Write-Info "uv ausente: Pinokio instala su bundle 'ai' y lo aporta" }

# ---------------------------------------------------------------- puerto
Write-Head "Puerto 7860"
$inUse = Get-NetTCPConnection -LocalPort 7860 -State Listen -ErrorAction SilentlyContinue
if ($inUse) {
  Write-Warn2 "7860 ocupado (PID $($inUse.OwningProcess -join ', ')): cierra la otra app o cambia el puerto en start.js"
} else {
  Write-Ok "7860 libre"
}

# ---------------------------------------------------------------- red
Write-Head "Red"
function Test-Endpoint {
  param([string]$Url, [string]$Label)
  try {
    $r = Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 12 -UseBasicParsing
    Write-Ok "$Label alcanzable (HTTP $($r.StatusCode))"
  } catch {
    $code = $null
    if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
    if ($code -and $code -in 401,403) { Write-Ok "$Label alcanzable (HTTP $code)" }
    else { Write-Bad "$Label NO alcanzable - instalación o descargas fallarán ($($_.Exception.Message))" }
  }
}
Test-Endpoint 'https://github.com' 'github.com (clone y auto-update)'
Test-Endpoint 'https://huggingface.co' 'huggingface.co (modelos)'

# ---------------------------------------------------------------- resumen
Write-Head "Resumen"
if ($blockers -gt 0) {
  Write-Host "  BLOQUEANTE: $blockers fallo(s), $warnings aviso(s). Resuelve los FAIL antes de instalar." -ForegroundColor Red
  exit 1
} elseif ($warnings -gt 0) {
  Write-Host "  LISTO CON AVISOS: $warnings aviso(s). Puedes instalar; revisa swap/VRAM." -ForegroundColor Yellow
} else {
  Write-Host "  LISTO: sin avisos. Instala desde Pinokio y arranca." -ForegroundColor Green
}
exit 0
