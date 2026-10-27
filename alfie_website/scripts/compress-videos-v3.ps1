# A.L.F.I.E Video Compression - VP9 Fixed
# ffmpeg 9 requires explicit bitrate parameters for VP9 CRF mode

$ASSETS_ROOT = "e:\Me\A.L.F.I.E\alfie_website\public\assets"
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

function Get-Profile {
    param([string]$Path)
    if ($Path -match "robot_avatars") {
        return @{ CRF = 38; Scale = 640; Label = "Avatar" }
    } elseif ($Path -match "brand_mascot") {
        return @{ CRF = 35; Scale = 720; Label = "Brand" }
    } else {
        return @{ CRF = 40; Scale = 854; Label = "Industry" }
    }
}

$videos = Get-ChildItem -Path $ASSETS_ROOT -Recurse -Filter *.webm -File | Sort-Object Length -Descending
Write-Host "`n=== VP9 Video Compression ===`n"
Write-Host "Found $($videos.Count) WebM videos"

$count = 0
$totalOrig = 0
$totalNew = 0

foreach ($video in $videos) {
    $count++
    $profile = Get-Profile -Path $video.FullName
    $origSize = $video.Length
    $totalOrig += $origSize
    $outFile = Join-Path $video.DirectoryName ("_cmp_" + $video.Name)
    
    Write-Host "`n[$count/$($videos.Count)] $($profile.Label): $($video.Name) ($([math]::Round($origSize/1MB,2)) MB)"
    Write-Host "  Encoding VP9 CRF=$($profile.CRF) scale=$($profile.Scale)..."
    
    # VP9 two-pass is slow; use single-pass with constrained quality mode
    # -quality good -speed 4 gives reasonable quality/speed tradeoff
    $args = "-y -i `"$($video.FullName)`" -c:v libvpx-vp9 -crf $($profile.CRF) -b:v 1M -maxrate 1M -bufsize 2M -vf `"scale=$($profile.Scale):-2`" -quality good -speed 4 -row-mt 1 -an `"$outFile`""
    
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = "ffmpeg"
    $pinfo.Arguments = $args
    $pinfo.RedirectStandardError = $true
    $pinfo.RedirectStandardOutput = $true
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true
    
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $pinfo
    $proc.Start() | Out-Null
    $proc.WaitForExit()
    
    if ((Test-Path $outFile) -and (Get-Item $outFile).Length -gt 1000) {
        $newSize = (Get-Item $outFile).Length
        $totalNew += $newSize
        $savings = [math]::Round((1 - $newSize/$origSize) * 100, 1)
        
        Remove-Item $video.FullName -Force
        Rename-Item $outFile $video.Name
        
        Write-Host "  $([math]::Round($origSize/1MB,2)) MB -> $([math]::Round($newSize/1MB,2)) MB ($savings% saved)"
    } else {
        Write-Host "  FAILED - keeping original ($([math]::Round($origSize/1MB,2)) MB)"
        $totalNew += $origSize
        if (Test-Path $outFile) { Remove-Item $outFile -Force }
    }
}

Write-Host "`n=== COMPLETE ==="
Write-Host "Before: $([math]::Round($totalOrig/1MB,1)) MB"
Write-Host "After:  $([math]::Round($totalNew/1MB,1)) MB"  
Write-Host "Saved:  $([math]::Round(($totalOrig-$totalNew)/1MB,1)) MB ($([math]::Round((1-$totalNew/$totalOrig)*100,1))%)"
