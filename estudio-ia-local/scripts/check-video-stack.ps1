# ¿Cuál de las cinco herramientas de vídeo-IA local es viable en ESTA máquina? (Windows)
# Uso: powershell -ExecutionPolicy Bypass -File scripts\check-video-stack.ps1 [-MinDiskGB 150]
# Umbrales tomados de los README/instaladores de cada app (ver ..\README.md §1).

[CmdletBinding()]
param([int]$MinDiskGB = 150)

$ErrorActionPreference = 'SilentlyContinue'
$gpuKind = 'none'; $vramMB = 0; $gpuName = ''; $driver = ''

function Ok    { param($m) Write-Host "  OK    $m" -ForegroundColor Green }
function Warn2 { param($m) Write-Host "  WARN  $m" -ForegroundColor Yellow }
function Fail  { param($m) Write-Host "  FAIL  $m" -ForegroundColor Red }
function Info  { param($m) Write-Host "  .     $m" -ForegroundColor DarkGray }
function Head  { param($m) Write-Host ""; Write-Host $m -ForegroundColor Cyan }

Write-Host "Vídeo-IA local . chequeo de hardware"
Info "sistema: $([System.Environment]::OSVersion.VersionString) ($env:PROCESSOR_ARCHITECTURE)"

Head "GPU"
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
  $q = & nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>$null
  if ($q) {
    $gpuKind = 'nvidia'
    $p = ($q | Select-Object -First 1) -split ','
    $gpuName = $p[0].Trim()
    $vramMB  = [int](($p[1] -replace '[^0-9]', ''))
    $driver  = if ($p.Count -ge 3) { $p[2].Trim() } else { '?' }
    Ok "NVIDIA: $gpuName - $vramMB MB VRAM - driver $driver"
    $major = [int]($driver -split '\.')[0]
    if ($major -ge 580) { Ok "Driver 580+: compatible con el runtime CUDA 13 por defecto de Maestro" }
    else { Warn2 "Driver <580: Maestro bloquea la instalación si necesita CUDA 13 (pide 580 o superior)" }
  }
}
if ($gpuKind -eq 'none') {
  $cards = Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name
  if ($cards) {
    $joined = $cards -join ' | '
    if ($joined -match 'AMD|Radeon') { Warn2 "AMD detectada ($joined): Maestro, H3 y FramePack son NVIDIA-only" }
    else { Warn2 "Sin NVIDIA utilizable ($joined): las tres apps de vídeo no arrancan" }
  } else { Warn2 "No se detectó GPU: las tres apps de vídeo no arrancan" }
}
if ($gpuKind -eq 'nvidia') {
  if     ($vramMB -ge 24000) { Info "tramo 24 GB+: Maestro estima 1-3 min por clip" }
  elseif ($vramMB -ge 12000) { Info "tramo 12-16 GB: perfil de offload, 4-10 min por clip" }
  elseif ($vramMB -ge 6000)  { Info "tramo 6-8 GB: offload fuerte, clips de ~10 s a 720p" }
  else                        { Info "menos de 6 GB: por debajo del mínimo de Maestro" }
}

Head "Memoria"
$ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
if     ($ramGB -ge 32) { Ok "RAM: $ramGB GB (recomendado)" }
elseif ($ramGB -ge 16) { Warn2 "RAM: $ramGB GB (mínimo de Maestro; clips cortos y paciencia)" }
else                   { Fail "RAM: $ramGB GB (por debajo del mínimo de 16 GB)" }

$cs = Get-CimInstance Win32_ComputerSystem
$os = Get-CimInstance Win32_OperatingSystem
$pageGB = [math]::Round(($os.TotalVirtualMemorySize - $os.TotalVisibleMemorySize) * 1KB / 1GB, 1)
if ($cs.AutomaticManagedPagefile) { Ok "Pagefile automático de Windows (~$pageGB GB): deja 40 GB libres por disco" }
elseif ($pageGB -ge 20) { Ok "Pagefile: ~$pageGB GB" }
else { Warn2 "Pagefile manual pequeño (~$pageGB GB): con 6-8 GB de VRAM se sufre" }

Head "Disco"
$freeGB = [math]::Round((Get-PSDrive -Name ($env:SystemDrive.TrimEnd(':'))).Free / 1GB)
if     ($freeGB -ge 500)          { Ok "Libre: $freeGB GB (alcanza para la colección completa de Maestro)" }
elseif ($freeGB -ge $MinDiskGB)   { Ok "Libre: $freeGB GB (mínimo de Maestro: $MinDiskGB GB)" }
elseif ($freeGB -ge 75)           { Warn2 "Libre: $freeGB GB - alcanza para H3 ComfyUI (75 GB) pero no para Maestro" }
else                              { Fail "Libre: $freeGB GB - insuficiente incluso para H3 ComfyUI" }
Info "desglose: Maestro 150 GB - H3 ComfyUI ~75 GB - FramePack ~30 GB - VideoCrafter 2 ~5 GB"

Head "Red"
function Check-Endpoint {
  param($Url, $Label)
  try {
    $r = Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 12 -UseBasicParsing
    Ok "$Label alcanzable (HTTP $($r.StatusCode))"
  } catch {
    $code = $null
    if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
    if ($code -and $code -in 401,403) { Ok "$Label alcanzable (HTTP $code)" }
    else { Fail "$Label NO alcanzable: las descargas de pesos fallarán" }
  }
}
Check-Endpoint 'https://github.com' 'github.com (clones)'
Check-Endpoint 'https://huggingface.co' 'huggingface.co (todos los pesos)'

Head "Puertos"
$busy = $false
foreach ($port in 7860, 8188) {
  if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
    Warn2 "puerto $port ocupado (ComfyUI/Maestro)"; $busy = $true
  }
}
if (-not $busy) { Ok "7860 y 8188 libres" }

Head "Veredicto por app"
$viable = 0
function Judge {
  param($Name, [bool]$Good, [bool]$Fair, $MsgGood, $MsgFair, $MsgNo)
  if ($gpuKind -ne 'nvidia') {
    Write-Host ("  {0,-5} {1,-22} {2}" -f "NO", $Name, "requiere NVIDIA (tienes: $gpuKind)") -ForegroundColor Red
    return
  }
  if ($Good)      { Write-Host ("  {0,-5} {1,-22} {2}" -f "SÍ",   $Name, $MsgGood) -ForegroundColor Green;  $script:viable++ }
  elseif ($Fair)  { Write-Host ("  {0,-5} {1,-22} {2}" -f "JUSTA", $Name, $MsgFair) -ForegroundColor Yellow; $script:viable++ }
  else            { Write-Host ("  {0,-5} {1,-22} {2}" -f "NO",   $Name, $MsgNo)   -ForegroundColor Red }
}

Judge 'Maestro' `
  ($vramMB -ge 12000 -and $ramGB -ge 32 -and $freeGB -ge 150) `
  ($vramMB -ge 6000  -and $ramGB -ge 16 -and $freeGB -ge 150) `
  '24 GB+: 1-3 min por clip' 'tu tramo: clips más lentos, pero viables' `
  "necesita >=6 GB VRAM y >=150 GB libres (tienes $vramMB MB y $freeGB GB)"

Judge 'MiniMax H3 ComfyUI' `
  ($vramMB -ge 24000 -and $freeGB -ge 75) `
  ($vramMB -ge 8000  -and $freeGB -ge 75) `
  '32 GB: un modelo por vez sin sudar' 'con menos VRAM, offload de ComfyUI' `
  "necesita ~75 GB libres y NVIDIA (tienes $freeGB GB)"

Judge 'FramePack' `
  ($vramMB -ge 8000 -and $freeGB -ge 30) `
  ($vramMB -ge 6000 -and $freeGB -ge 30) `
  '8 GB+: sin apuros' 'probado en 6 GB; lento' `
  'necesita >=6 GB VRAM y ~30 GB libres'

Write-Host ("  {0,-5} {1,-22} {2}" -f "—", "VideoCrafter 2", "instalable en casi cualquier GPU, pero 512 px y de 2024: no lo recomiendo") -ForegroundColor DarkGray
Write-Host ("  {0,-5} {1,-22} {2}" -f "—", "arena-hard-auto", "no genera imagen ni vídeo: es un benchmark de LLM (necesita API keys de pago)") -ForegroundColor DarkGray

Head "Resumen"
if ($viable -gt 0) {
  Write-Host "  $viable app(s) viable(s). Para la historia: Maestro. Para la landing y el 3D: código, no generación." -ForegroundColor Green
  exit 0
} else {
  Write-Host "  Ninguna viable en esta máquina. Alternativas: API en la nube para los clips, o el pipeline offline de abyss-historia-15s (sin GPU)." -ForegroundColor Red
  exit 1
}
