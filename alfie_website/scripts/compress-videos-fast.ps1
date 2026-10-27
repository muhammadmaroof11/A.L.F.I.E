# Fast WebM Compression using VP9 Realtime Mode
$ASSETS_ROOT = "e:\Me\A.L.F.I.E\alfie_website\public\assets"
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

function Get-Profile {
    param([string]$Path)
    if ($Path -match "robot_avatars") {
        return @{ CRF = 36; Width = 640; Bitrate = "550k"; Label = "Avatar" }
    } elseif ($Path -match "brand_mascot") {
        return @{ CRF = 34; Width = 720; Bitrate = "750k"; Label = "Brand" }
    } else {
        return @{ CRF = 36; Width = 854; Bitrate = "600k"; Label = "Industry" }
    }
}

$videos = Get-ChildItem -Path $ASSETS_ROOT -Recurse -Filter *.webm -File | Sort-Object Length -Descending
Write-Host "`n=== Fast VP9 WebM Video Compression ==="
Write-Host "Found $($videos.Count) WebM videos`n"

$count = 0
$totalOrig = 0
$totalNew = 0

foreach ($video in $videos) {
    $count++
    $profile = Get-Profile -Path $video.FullName
    $origSize = $video.Length
    $totalOrig += $origSize
    $tempOut = Join-Path $video.DirectoryName ("_fastcmp_" + $video.Name)
    
    Write-Host "[$count/$($videos.Count)] $($profile.Label): $($video.Name) ($([math]::Round($origSize/1MB,2)) MB)"
    
    & ffmpeg -y -i $video.FullName `
        -c:v libvpx-vp9 -crf $($profile.CRF) -b:v $($profile.Bitrate) `
        -vf "scale=$($profile.Width):-2" `
        -deadline realtime -cpu-used 8 -row-mt 1 -an `
        $tempOut 2>$null
    
    if ((Test-Path $tempOut) -and (Get-Item $tempOut).Length -gt 1000) {
        $newSize = (Get-Item $tempOut).Length
        $totalNew += $newSize
        $savings = [math]::Round((1 - $newSize/$origSize) * 100, 1)
        
        Remove-Item $video.FullName -Force
        Rename-Item $tempOut $video.Name
        
        Write-Host "  -> $([math]::Round($newSize/1MB,2)) MB ($savings% saved)`n"
    } else {
        Write-Host "  -> FAILED, keeping original`n"
        $totalNew += $origSize
        if (Test-Path $tempOut) { Remove-Item $tempOut -Force }
    }
}

Write-Host "=== ALL VIDEOS COMPRESSED ==="
Write-Host "Original Total : $([math]::Round($totalOrig/1MB, 2)) MB"
Write-Host "Optimized Total: $([math]::Round($totalNew/1MB, 2)) MB"
Write-Host "Saved          : $([math]::Round(($totalOrig - $totalNew)/1MB, 2)) MB ($([math]::Round((1 - $totalNew/$totalOrig)*100, 1))% reduction)"
