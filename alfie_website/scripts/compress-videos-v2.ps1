# A.L.F.I.E Video Compression (Fixed) 
# Uses ffmpeg with proper process waiting

$ASSETS_ROOT = "e:\Me\A.L.F.I.E\alfie_website\public\assets"
$BACKUP_DIR  = "e:\Me\A.L.F.I.E\alfie_website\_asset_backups\videos"

# Refresh PATH for ffmpeg
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

function Get-Profile {
    param([string]$Path)
    if ($Path -match "robot_avatars") {
        return @{ CRF = 35; Width = 640; MaxRate = "500k"; Label = "Avatar" }
    } elseif ($Path -match "brand_mascot") {
        return @{ CRF = 32; Width = 720; MaxRate = "800k"; Label = "Brand" }
    } else {
        return @{ CRF = 36; Width = 854; MaxRate = "600k"; Label = "Industry" }
    }
}

$videos = Get-ChildItem -Path $ASSETS_ROOT -Recurse -Include *.webm,*.mp4 -File | Sort-Object Length -Descending

Write-Host "`n=== A.L.F.I.E Video Compression ===`n"
Write-Host "Found $($videos.Count) videos"
$count = 0
$totalOrig = 0
$totalNew = 0

foreach ($video in $videos) {
    $count++
    $profile = Get-Profile -Path $video.FullName
    $origSize = $video.Length
    $totalOrig += $origSize
    $outputPath = Join-Path $video.DirectoryName ("_compressed_" + $video.Name)
    
    Write-Host "[$count/$($videos.Count)] $($profile.Label): $($video.Name) ($([math]::Round($origSize/1MB,2)) MB)"
    
    # Run ffmpeg and WAIT for it to complete
    if ($video.Extension -eq ".mp4") {
        $proc = Start-Process -FilePath "ffmpeg" -ArgumentList @(
            "-y", "-i", "`"$($video.FullName)`"",
            "-c:v", "libx264", "-crf", "$($profile.CRF)",
            "-vf", "scale=$($profile.Width):-2",
            "-maxrate", "$($profile.MaxRate)", "-bufsize", "1M",
            "-preset", "slow", "-movflags", "+faststart",
            "-an",
            "`"$outputPath`""
        ) -Wait -NoNewWindow -PassThru
    } else {
        $proc = Start-Process -FilePath "ffmpeg" -ArgumentList @(
            "-y", "-i", "`"$($video.FullName)`"",
            "-c:v", "libvpx-vp9", "-crf", "$($profile.CRF)", "-b:v", "0",
            "-vf", "scale=$($profile.Width):-2",
            "-maxrate", "$($profile.MaxRate)", "-bufsize", "1M",
            "-row-mt", "1", "-tile-columns", "2", "-threads", "4",
            "-an",
            "`"$outputPath`""
        ) -Wait -NoNewWindow -PassThru
    }
    
    if ((Test-Path $outputPath) -and (Get-Item $outputPath).Length -gt 0) {
        $newSize = (Get-Item $outputPath).Length
        $totalNew += $newSize
        $savings = [math]::Round((1 - $newSize/$origSize) * 100, 1)
        
        # Swap files
        Remove-Item $video.FullName -Force
        Rename-Item $outputPath $video.Name
        
        Write-Host "  $([math]::Round($origSize/1MB,2)) MB -> $([math]::Round($newSize/1MB,2)) MB ($savings% smaller)"
    } else {
        Write-Host "  FAILED - keeping original"
        $totalNew += $origSize
        if (Test-Path $outputPath) { Remove-Item $outputPath -Force }
    }
}

Write-Host "`n=== DONE ==="
Write-Host "Before: $([math]::Round($totalOrig/1MB,1)) MB"
Write-Host "After:  $([math]::Round($totalNew/1MB,1)) MB"
Write-Host "Saved:  $([math]::Round(($totalOrig-$totalNew)/1MB,1)) MB ($([math]::Round((1-$totalNew/$totalOrig)*100,1))%)"
