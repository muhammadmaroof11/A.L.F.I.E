# A.L.F.I.E Video Compression & Poster Generation Script
# Uses ffmpeg to:
# 1. Re-encode all .webm videos with optimized VP9 settings
# 2. Generate poster .jpg frames for each video (for <video poster="...">)
# Backs up originals before replacing

$ErrorActionPreference = "Continue"
$ASSETS_ROOT = "e:\Me\A.L.F.I.E\alfie_website\public\assets"
$BACKUP_DIR  = "e:\Me\A.L.F.I.E\alfie_website\_asset_backups\videos"
$POSTER_DIR  = "e:\Me\A.L.F.I.E\alfie_website\public\assets\posters"

# Refresh PATH so we can find ffmpeg
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Compression profiles based on content type
# Robot avatars: small, looping, need to be crisp → moderate quality, small resolution
# Industry videos: ambient B-roll → can be lower quality, 720p is fine
# Brand mascot: main brand element → decent quality

function Get-Profile {
    param([string]$Path)
    
    if ($Path -match "robot_avatars") {
        return @{ CRF = 35; Width = 640; MaxRate = "500k"; Label = "Avatar" }
    }
    elseif ($Path -match "brand_mascot") {
        return @{ CRF = 32; Width = 720; MaxRate = "800k"; Label = "Brand" }
    }
    else {
        # Industry videos - ambient B-roll
        return @{ CRF = 36; Width = 854; MaxRate = "600k"; Label = "Industry" }
    }
}

function Format-Size {
    param([long]$Bytes)
    if ($Bytes -lt 1024) { return "$Bytes B" }
    if ($Bytes -lt 1MB)  { return "$([math]::Round($Bytes/1KB, 0)) KB" }
    return "$([math]::Round($Bytes/1MB, 2)) MB"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "  A.L.F.I.E Video Compression Pipeline"
Write-Host "=========================================="
Write-Host ""

# Create directories
New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
New-Item -ItemType Directory -Path $POSTER_DIR -Force | Out-Null

# Find all video files
$videos = Get-ChildItem -Path $ASSETS_ROOT -Recurse -Include *.webm,*.mp4 -File | Sort-Object Length -Descending

Write-Host "Found $($videos.Count) videos to process."
Write-Host "Backups: $BACKUP_DIR"
Write-Host "Posters: $POSTER_DIR"
Write-Host ""

$totalOriginal = 0
$totalCompressed = 0
$count = 0

foreach ($video in $videos) {
    $count++
    $profile = Get-Profile -Path $video.FullName
    $originalSize = $video.Length
    $totalOriginal += $originalSize
    
    $posterName = ($video.BaseName -replace '[^a-zA-Z0-9_]', '_') + ".jpg"
    $posterPath = Join-Path $POSTER_DIR $posterName
    $tempPath = Join-Path $video.DirectoryName ("_tmp_" + $video.Name)

    Write-Host "[$count/$($videos.Count)] $($profile.Label): $($video.Name) ($(Format-Size $originalSize))"

    # Backup original to flat backup dir
    Copy-Item $video.FullName (Join-Path $BACKUP_DIR $video.Name) -Force

    # 1. Generate poster frame (grab frame at 1 second or first frame)
    Write-Host "  Generating poster: $posterName"
    & ffmpeg -y -i $video.FullName -ss 0.5 -vframes 1 -q:v 5 -vf "scale=$($profile.Width):-2" $posterPath 2>$null
    
    if (Test-Path $posterPath) {
        $posterSize = (Get-Item $posterPath).Length
        Write-Host "  Poster: $(Format-Size $posterSize)"
    }

    # 2. Re-encode video
    Write-Host "  Compressing..."
    
    if ($video.Extension -eq ".mp4") {
        # MP4: Use H.264
        & ffmpeg -y -i $video.FullName `
            -c:v libx264 -crf $($profile.CRF) `
            -vf "scale=$($profile.Width):-2" `
            -maxrate $($profile.MaxRate) -bufsize "1M" `
            -preset slow -movflags +faststart `
            -an `
            $tempPath 2>$null
    }
    else {
        # WebM: Use VP9
        & ffmpeg -y -i $video.FullName `
            -c:v libvpx-vp9 -crf $($profile.CRF) -b:v 0 `
            -vf "scale=$($profile.Width):-2" `
            -maxrate $($profile.MaxRate) -bufsize "1M" `
            -row-mt 1 -tile-columns 2 -threads 4 `
            -an `
            $tempPath 2>$null
    }

    if (Test-Path $tempPath) {
        $newSize = (Get-Item $tempPath).Length
        $totalCompressed += $newSize
        $savings = [math]::Round((1 - $newSize / $originalSize) * 100, 1)
        
        # Replace original with compressed
        Remove-Item $video.FullName -Force
        Rename-Item $tempPath $video.Name
        
        $icon = if ($savings -gt 60) { [char]0x1F7E2 } elseif ($savings -gt 30) { [char]0x1F7E1 } else { [char]0x26AA }
        Write-Host "  $icon $(Format-Size $originalSize) -> $(Format-Size $newSize) ($savings% smaller)"
    }
    else {
        Write-Host "  FAILED - keeping original"
        $totalCompressed += $originalSize
    }
    
    Write-Host ""
}

Write-Host "=========================================="
Write-Host "  COMPRESSION COMPLETE"
Write-Host "  Videos: $count processed"
Write-Host "  Before: $(Format-Size $totalOriginal)"
Write-Host "  After:  $(Format-Size $totalCompressed)"
Write-Host "  Saved:  $(Format-Size ($totalOriginal - $totalCompressed)) ($([math]::Round((1 - $totalCompressed/$totalOriginal) * 100, 1))%)"
Write-Host "  Posters generated in: $POSTER_DIR"
Write-Host "=========================================="
