param(
  [int]$InitialA = 0,
  [int]$InitialB = 0,
  [int]$InitialCin = 0,
  [string]$Output = 'C01-cong-2bit/video/C01-demo.mp4',
  [int]$MoveMilliseconds = 600,
  [string]$Plan,
  [Nullable[int]]$Seed,
  [ValidateSet('ddagrab','gdigrab')][string]$CaptureBackend = 'ddagrab',
  [Int64]$WindowHandle = 0,
  [int]$CaptureX = -1,
  [int]$CaptureY = -1,
  [int]$CaptureWidth = -1,
  [int]$CaptureHeight = -1
)
function Join-ProcessArgs([object[]]$Items) {
 # Windows PowerShell 5.1 không có ProcessStartInfo.ArgumentList: ghép thành chuỗi có trích dẫn.
 ($Items | ForEach-Object { $a=[string]$_; if ($a -match '[\s"]') { '"' + ($a -replace '"','\"') + '"' } else { $a } }) -join ' '
}
function New-MotionPath([int]$X0,[int]$Y0,[int]$X1,[int]$Y1,[System.Random]$Random) {
 $dx=$X1-$X0; $dy=$Y1-$Y0; $distance=[Math]::Sqrt($dx*$dx+$dy*$dy)
 $amplitude=3+4*$Random.NextDouble(); if($distance -lt 60){$amplitude *= $distance/60}
 $f1=1.5+1.5*$Random.NextDouble(); $f2=3+3*$Random.NextDouble()
 $phi1=2*[Math]::PI*$Random.NextDouble(); $phi2=2*[Math]::PI*$Random.NextDouble()
 $steps=$Random.Next(60,81); $duration=$Random.Next(500,801); $pause=$Random.Next(150,251)
 $nx=0.0; $ny=0.0; if($distance -gt 0){$nx=-$dy/$distance; $ny=$dx/$distance}
 $points=@(for($i=1;$i -le $steps;$i++){
  $t=$i/[double]$steps; $ease=3*$t*$t-2*$t*$t*$t
  $offset=$amplitude*[Math]::Sin([Math]::PI*$t)*(0.7*[Math]::Sin(2*[Math]::PI*$f1*$t+$phi1)+0.3*[Math]::Sin(2*[Math]::PI*$f2*$t+$phi2))
  [pscustomobject]@{ x=[int][Math]::Round($X0+$dx*$ease+$nx*$offset); y=[int][Math]::Round($Y0+$dy*$ease+$ny*$offset); t=$t }
 })
 [pscustomobject]@{ start=@($X0,$Y0); end=@($X1,$Y1); distance=$distance; amplitude=$amplitude; f1=$f1; f2=$f2; phi1=$phi1; phi2=$phi2; steps=$steps; durationMs=$duration; pauseMs=$pause; points=$points }
}
# Open C01 in Velxio, maximize Chrome, Circuit view, collapse AI panel,
# click Reset view (100%). Coordinates are for 1920x1080 desktop, 100% scale.
# Requires PowerShell 7 (pwsh). Capture uses Desktop Duplication for a moving hardware cursor.
# Switch order top to bottom: A0, B0, A1, B1, Cin. Set InitialA/B/Cin to actual UI values.
# Do not touch the mouse or change focus during capture. Output is never overwritten.
$ErrorActionPreference = 'Stop'
if ($MoveMilliseconds -lt 400 -or $MoveMilliseconds -gt 800) { throw 'Use 400..800 ms movement.' }
$repo = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repo
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class C01Mouse {
 [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
 [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT p);
 [DllImport("user32.dll")] public static extern int GetSystemMetrics(int index);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] public static extern void mouse_event(uint flags,uint dx,uint dy,uint data,UIntPtr extra);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hwnd);
 [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,IntPtr p);
 [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a,uint b,bool attach);
 [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
 public static bool ActivateTarget(IntPtr h){uint current=GetCurrentThreadId();uint foreground=GetWindowThreadProcessId(GetForegroundWindow(),IntPtr.Zero);bool attached=current!=foreground&&AttachThreadInput(current,foreground,true);try{ShowWindow(h,3);BringWindowToTop(h);return SetForegroundWindow(h);}finally{if(attached)AttachThreadInput(current,foreground,false);}}
 [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hwnd);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd,int command);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
}
"@
if ($Plan) {
 $ErrorActionPreference = 'Stop'
 if ($MoveMilliseconds -lt 400 -or $MoveMilliseconds -gt 800) { throw 'Use 400..800 ms movement.' }
 if (-not $PSBoundParameters.ContainsKey('Output')) { throw 'When using -Plan, pass -Output explicitly.' }
 $repo = Split-Path $PSScriptRoot -Parent
 if ([IO.Path]::IsPathRooted($Output)) { $finalOutput = [IO.Path]::GetFullPath($Output) }
 else { $finalOutput = [IO.Path]::GetFullPath((Join-Path $repo $Output)) }
 if (Test-Path -LiteralPath $finalOutput) { throw "Output already exists: $finalOutput" }
 if ([IO.Path]::GetExtension($finalOutput) -ne '.mp4') { throw 'Plan output must be an .mp4 file.' }

 $planPath = (Resolve-Path -LiteralPath $Plan).Path
 $planData = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json -AsHashtable
 if (-not $planData.title -or -not $planData.switches -or -not $planData.cases -or -not $planData.capture) { throw 'Plan requires title, switches, capture, and cases.' }
 if ($CaptureX -lt 0) { $CaptureX = [int]$planData.capture.x }
 if ($CaptureY -lt 0) { $CaptureY = [int]$planData.capture.y }
 if ($CaptureWidth -lt 1) { $CaptureWidth = [int]$planData.capture.width }
 if ($CaptureHeight -lt 1) { $CaptureHeight = [int]$planData.capture.height }
 if ($CaptureX -lt 0 -or $CaptureY -lt 0 -or $CaptureWidth -lt 1 -or $CaptureHeight -lt 1) { throw 'Capture rectangle must have non-negative origin and positive size.' }
 $virtualLeft = [C01Mouse]::GetSystemMetrics(76)
 $virtualTop = [C01Mouse]::GetSystemMetrics(77)
 $virtualWidth = [C01Mouse]::GetSystemMetrics(78)
 $virtualHeight = [C01Mouse]::GetSystemMetrics(79)
 if ($CaptureX -lt $virtualLeft -or $CaptureY -lt $virtualTop -or
     ($CaptureX + $CaptureWidth) -gt ($virtualLeft + $virtualWidth) -or
     ($CaptureY + $CaptureHeight) -gt ($virtualTop + $virtualHeight)) { throw 'Capture rectangle lies outside the virtual desktop.' }

 if ($WindowHandle -ne 0) { $targetHandle = [IntPtr]::new($WindowHandle) }
 elseif ($planData.windowHandle) { $targetHandle = [IntPtr]::new([Int64]$planData.windowHandle) }
 else { $targetHandle = [C01Mouse]::GetForegroundWindow() }
 if ($targetHandle -eq [IntPtr]::Zero -or -not [C01Mouse]::IsWindow($targetHandle)) { throw 'A valid Velxio window handle is required (use plan.windowHandle or -WindowHandle).' }
 if ([C01Mouse]::IsIconic($targetHandle)) { [void][C01Mouse]::ShowWindow($targetHandle, 9) } # SW_RESTORE only when minimized
 [void][C01Mouse]::ShowWindow($targetHandle,3)
 [void][C01Mouse]::ActivateTarget($targetHandle)
 $windowReady = $false
 for ($try=0; $try -lt 30; $try++) {
  $titleBuilder = [Text.StringBuilder]::new(512)
  [void][C01Mouse]::GetWindowText($targetHandle, $titleBuilder, 512)
  if ([C01Mouse]::GetForegroundWindow() -eq $targetHandle -and $titleBuilder.ToString().IndexOf('Velxio',[StringComparison]::OrdinalIgnoreCase) -ge 0) { $windowReady=$true; break }
  Start-Sleep -Milliseconds 100
 }
 if (-not $windowReady) { throw 'Could not restore and foreground the target window with a Velxio title.' }

 $switchNames = @($planData.switches.Keys)
 if ($switchNames.Count -eq 0) { throw 'Plan must define at least one switch.' }
 foreach ($name in $switchNames) {
  $point = $planData.switches[$name]
  if ($null -eq $point.x -or $null -eq $point.y) { throw "Switch '$name' requires x and y coordinates." }
  if ([int]$point.x -lt $virtualLeft -or [int]$point.x -ge ($virtualLeft+$virtualWidth) -or [int]$point.y -lt $virtualTop -or [int]$point.y -ge ($virtualTop+$virtualHeight)) { throw "Switch '$name' is outside the virtual desktop." }
  if (-not $planData.initial.Contains($name) -or $planData.initial[$name] -notin @(0,1)) { throw "Plan initial state must define $name as 0 or 1." }
 }
 foreach ($case in $planData.cases) {
  if ($null -eq $case.values -or $null -eq $case.caption) { throw 'Every case requires values and caption.' }
  foreach ($name in $case.values.Keys) {
   if ($name -notin $switchNames -or $case.values[$name] -notin @(0,1)) { throw "Invalid case value for switch '$name'." }
  }
  if ($null -ne $case.hold -and [double]$case.hold -lt 0) { throw 'Case hold must be non-negative.' }
 }

 $runDir = Join-Path ([IO.Path]::GetTempPath()) ('velxio-demo-' + [guid]::NewGuid().ToString('N'))
 New-Item -ItemType Directory -Path $runDir | Out-Null
 $progressFile = Join-Path $runDir 'progress.log'
 $captionFile = Join-Path $runDir 'caption.txt'
 $eventsFile = Join-Path $runDir 'events.log'
 $ffmpegLog = Join-Path $runDir 'ffmpeg.log'
 $probeLog = Join-Path $runDir 'ffprobe.log'
 $decodeLog = Join-Path $runDir 'decode.log'
 $partialOutput = Join-Path $runDir 'capture.partial.mp4'
 [IO.File]::WriteAllText($progressFile, '')
 [IO.File]::WriteAllText($eventsFile, '')
 $ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
 $ffprobe = (Get-Command ffprobe -ErrorAction Stop).Source
 $captionPath = $captionFile.Replace('\','/').Replace(':','\:').Replace("'","\'")
 $captionY = [Math]::Max(8, $CaptureHeight - 70)
 $captionFilter = "drawbox=x=0:y=$($CaptureHeight-100):w=${CaptureWidth}:h=100:color=black@1:t=fill,drawtext=font=Arial:textfile='$captionPath':reload=1:fontcolor=white:fontsize=25:x=32:y=$captionY"
 foreach($name in $switchNames) {
  $labelX=[int]$planData.switches[$name].x+30-$CaptureX
  $labelY=[int]$planData.switches[$name].y-30-$CaptureY
  $captionFilter+=",drawtext=font=Arial:text='${name}':fontcolor=white:fontsize=20:x=${labelX}:y=${labelY}"
 }
 $inputSpec = "ddagrab=framerate=30:draw_mouse=1:video_size=${CaptureWidth}x${CaptureHeight}:offset_x=${CaptureX}:offset_y=${CaptureY}"
 $info = [Diagnostics.ProcessStartInfo]::new()
 $info.FileName = $ffmpeg; $info.WorkingDirectory = $runDir; $info.UseShellExecute=$false; $info.CreateNoWindow=$true
 $info.RedirectStandardInput=$true; $info.RedirectStandardError=$true
 $captureArgs = if ($CaptureBackend -eq 'gdigrab') { @('-f','gdigrab','-framerate','30','-draw_mouse','1','-offset_x',"$CaptureX",'-offset_y',"$CaptureY",'-video_size',"${CaptureWidth}x${CaptureHeight}",'-i','desktop','-vf',$captionFilter) } else { @('-f','lavfi','-i',$inputSpec,'-vf',("hwdownload,format=bgra,"+$captionFilter)) }
 $info.Arguments = Join-ProcessArgs (@('-n','-progress',$progressFile)+$captureArgs+@('-an','-c:v','libx264','-preset','veryfast','-tune','zerolatency','-crf','20','-pix_fmt','yuv420p',$partialOutput))
 $proc = [Diagnostics.Process]::new(); $proc.StartInfo=$info
 $events = [Collections.Generic.List[string]]::new()
 $current = @{}; foreach ($name in $switchNames) { $current[$name] = [int]$planData.initial[$name] }
 if ($null -eq $Seed) { $Seed = [Security.Cryptography.RandomNumberGenerator]::GetInt32(0,[int]::MaxValue) }
 $motionRandom=[System.Random]::new([int]$Seed)
 $motionLog=Join-Path $runDir 'motion.jsonl'
 [IO.File]::WriteAllText($motionLog,((@{seed=[int]$Seed} | ConvertTo-Json -Compress)+[Environment]::NewLine))
 function Assert-PlanWindow {
  $title = [Text.StringBuilder]::new(512)
  [void][C01Mouse]::GetWindowText($targetHandle,$title,512)
  if ($started -and $proc.HasExited) { throw 'ffmpeg stopped during capture; no further input sent.' }
  if ([C01Mouse]::GetForegroundWindow() -ne $targetHandle -or $title.ToString().IndexOf('Velxio',[StringComparison]::OrdinalIgnoreCase) -lt 0) { throw 'Velxio target lost foreground focus during capture.' }
 }
 function Move-PlanRoute([int]$X,[int]$Y) {
  Assert-PlanWindow
  $point=[C01Mouse+POINT]::new(); if (-not [C01Mouse]::GetCursorPos([ref]$point)) { throw 'GetCursorPos failed.' }
  $path=New-MotionPath $point.X $point.Y $X $Y $motionRandom
  $progressText=Get-Content -LiteralPath $progressFile -Raw
  $progressMatches=[regex]::Matches($progressText,'out_time_us=(\d+)')
  $videoTimeStart=if($progressMatches.Count){[double]$progressMatches[$progressMatches.Count-1].Groups[1].Value/1000000}else{0.0}
  $watch=[Diagnostics.Stopwatch]::StartNew()
  foreach($sample in $path.points) {
   $deadline=$path.durationMs*$sample.t
   while(($remaining=$deadline-$watch.Elapsed.TotalMilliseconds) -gt 0) {
    if($remaining -gt 3) { Start-Sleep -Milliseconds ([int][Math]::Floor($remaining-1)) } else { [Threading.Thread]::Yield() | Out-Null }
   }
   if (-not [C01Mouse]::SetCursorPos($sample.x,$sample.y)) { throw 'SetCursorPos failed.' }
   $absoluteX=[uint32]($sample.x*65535/([C01Mouse]::GetSystemMetrics(0)-1)); $absoluteY=[uint32]($sample.y*65535/([C01Mouse]::GetSystemMetrics(1)-1))
   [C01Mouse]::mouse_event(0x8001,$absoluteX,$absoluteY,0,[UIntPtr]::Zero)
  }
  $watch.Stop()
  $record=@{ seed=[int]$Seed; path=$path; videoTimeStart=$videoTimeStart; actualDurationMs=$watch.Elapsed.TotalMilliseconds }
  [IO.File]::AppendAllText($motionLog,(($record | ConvertTo-Json -Depth 8 -Compress)+[Environment]::NewLine))
  Start-Sleep -Milliseconds $path.pauseMs
 }
 function Write-PlanCaption([string]$Text) {
  $bytes=[Text.Encoding]::UTF8.GetBytes($Text.PadRight(4096))
  for($retry=0;$retry-lt20;$retry++) {
   try {
    $stream=[IO.File]::Open($captionFile,[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite)
    try{$stream.Write($bytes,0,$bytes.Length);$stream.Flush()}finally{$stream.Dispose()}
    return
   } catch [IO.IOException] {if($retry-eq19){throw};Start-Sleep -Milliseconds 50}
  }
 }
 $started = $false; $stderrTask = $null
 try {
  Assert-PlanWindow
  Write-PlanCaption ([string]$planData.title)
  [void]$proc.Start(); $started=$true; $stderrTask=$proc.StandardError.ReadToEndAsync()
  $ready=$false
  for ($attempt=0; $attempt -lt 120; $attempt++) {
   if ($proc.HasExited) { throw 'ffmpeg ended before capture started.' }
   if ((Get-Content -LiteralPath $progressFile -Raw) -match 'frame=[1-9]') { $ready=$true; break }
   Start-Sleep -Milliseconds 250
  }
  if (-not $ready) { throw 'Timed out waiting for first captured frame.' }
  foreach ($case in $planData.cases) {
   foreach ($name in $case.values.Keys) {
    $value=[int]$case.values[$name]
    if ($current[$name] -ne $value) {
     $switchPoint=$planData.switches[$name]
     Move-PlanRoute ([int]$switchPoint.x) ([int]$switchPoint.y)
     Assert-PlanWindow
     [C01Mouse]::mouse_event(2,0,0,0,[UIntPtr]::Zero); Start-Sleep -Milliseconds 60
     [C01Mouse]::mouse_event(4,0,0,0,[UIntPtr]::Zero); Start-Sleep -Milliseconds 120
     $current[$name]=$value
    }
   }
   $message=[string]$case.caption
   Write-PlanCaption $message
   $progressText=Get-Content -LiteralPath $progressFile -Raw
   $videoTime=0.0
   $matchesTime=[regex]::Matches($progressText,'out_time_us=(\d+)')
   if($matchesTime.Count){$videoTime=[double]$matchesTime[$matchesTime.Count-1].Groups[1].Value/1000000}
   $line=('{0:F3}s | {1} | {2}' -f $videoTime,$message,(ConvertTo-Json -InputObject $current -Compress))
   $events.Add($line); Start-Sleep -Seconds ([double]$(if ($null -ne $case.hold) { $case.hold } else { 2 }))
  }
 } finally {
  if ($started -and -not $proc.HasExited) { $proc.StandardInput.WriteLine('q'); $proc.StandardInput.Flush(); $null=$proc.WaitForExit(15000) }
  if ($started -and $stderrTask) { $stderrTask.Result | Set-Content -LiteralPath $ffmpegLog }
  $events | Set-Content -LiteralPath $eventsFile
 }
 if (-not $started -or $proc.ExitCode -ne 0) { throw "ffmpeg capture failed; partial output and logs retained at $runDir" }
 $probeJson = & $ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height -show_entries format=duration -of json $partialOutput 2> $probeLog
 if ($LASTEXITCODE -ne 0) { throw "ffprobe failed; partial output and logs retained at $runDir" }
 $probe = ($probeJson -join "`n") | ConvertFrom-Json
 if (-not $probe.streams -or $probe.streams[0].width -ne $CaptureWidth -or $probe.streams[0].height -ne $CaptureHeight -or [double]$probe.format.duration -le 0) { throw "Captured MP4 failed stream/duration validation; artifacts retained at $runDir" }
 & $ffmpeg -v error -i $partialOutput -f null - 2> $decodeLog
 if ($LASTEXITCODE -ne 0) { throw "MP4 decode validation failed; artifacts retained at $runDir" }
 $outputDirectory = Split-Path -Parent $finalOutput
 if ($outputDirectory) { New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null }
 [IO.File]::Copy($partialOutput,$finalOutput,$false)
 Write-Output "Saved $finalOutput"
 Write-Output "Plan artifacts: $runDir"
 return
}
if (-not $Plan) {
 if (Test-Path -LiteralPath $Output) { throw "Output already exists: $Output" }
 New-Item -ItemType Directory -Path 'C01-cong-2bit/video' -Force | Out-Null
}
function Assert-Velxio {
 $title = [Text.StringBuilder]::new(512)
 [void][C01Mouse]::GetWindowText([C01Mouse]::GetForegroundWindow(),$title,512)
 if ($title.ToString() -notmatch 'Velxio.*Google Chrome') { throw 'Foreground window must be the separate Velxio Chrome window.' }
}
function Move-Smooth([int]$X,[int]$Y) {
 Assert-Velxio
 $point = [C01Mouse+POINT]::new()
 [void][C01Mouse]::GetCursorPos([ref]$point)
 $steps = 40
 for ($i=1; $i -le $steps; $i++) {
  $t=$i/[double]$steps; $ease=$t*$t*(3-2*$t)
    $px=$point.X+($X-$point.X)*$ease; $py=$point.Y+($Y-$point.Y)*$ease
  $nx=[uint32]($px*65535/([C01Mouse]::GetSystemMetrics(0)-1)); $ny=[uint32]($py*65535/([C01Mouse]::GetSystemMetrics(1)-1))
  [C01Mouse]::mouse_event(0x8001,$nx,$ny,0,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds ([int]($MoveMilliseconds/$steps))
 }
}
function Click-Switch([int]$Y) {
 Move-Smooth 180 $Y
 Assert-Velxio
 [C01Mouse]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 60
 [C01Mouse]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 180
}
$positions = @{ A0=252; B0=372; A1=492; B1=612; Cin=732 }
$current = @{ A0=($InitialA-band 1); B0=($InitialB-band 1); A1=($InitialA-shr 1); B1=($InitialB-shr 1); Cin=$InitialCin }
# Ten stable demonstration cases, including carry through both stages and max sum.
$cases = @(@(0,0,0),@(0,0,1),@(1,0,1),@(1,1,0),@(1,1,1),@(3,0,1),@(2,2,0),@(2,3,1),@(3,3,0),@(3,3,1))
Assert-Velxio
$caption='C01-cong-2bit/video/caption.txt'
function Write-Caption([string]$Text) {
 $bytes=[Text.Encoding]::ASCII.GetBytes($Text.PadRight(180))
 for($retry=0; $retry -lt 20; $retry++) {
  try {
   $stream=[IO.File]::Open((Join-Path $repo $caption),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite)
   try { $stream.Write($bytes,0,$bytes.Length); $stream.Flush() } finally { $stream.Dispose() }
   return
  } catch [IO.IOException] { if($retry -eq 19) { throw }; Start-Sleep -Milliseconds 50 }
 }
}
Write-Caption 'C01: 2-bit ripple carry adder - actual LEDs on canvas'
$filter="drawbox=x=0:y=850:w=1900:h=135:color=black@0.85:t=fill,drawtext=font=Arial:textfile=${caption}:reload=1:fontcolor=white:fontsize=28:x=55:y=880"
foreach ($key in @('A0','B0','A1','B1','Cin')) { $labelY=$positions[$key]-35; $filter+=",drawtext=font=Arial:text=${key}:fontcolor=white:fontsize=23:x=205:y=$labelY" }
$info=[Diagnostics.ProcessStartInfo]::new()
$info.FileName=(Get-Command ffmpeg -ErrorAction Stop).Source
$info.WorkingDirectory=$repo; $info.UseShellExecute=$false; $info.CreateNoWindow=$true
$info.RedirectStandardInput=$true; $info.RedirectStandardError=$true
$info.Arguments = Join-ProcessArgs @('-n','-progress','C01-cong-2bit/video/capture-progress.log','-f','lavfi','-i','ddagrab=framerate=30:draw_mouse=1:video_size=1920x1032','-vf',("hwdownload,format=bgra,"+$filter),'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',$Output)
$proc=[Diagnostics.Process]::new(); $proc.StartInfo=$info
[IO.File]::WriteAllText((Join-Path $repo 'C01-cong-2bit/video/capture-progress.log'),'')
[void]$proc.Start(); $errors=$proc.StandardError.ReadToEndAsync()
$clock=[Diagnostics.Stopwatch]::StartNew(); $events=[Collections.Generic.List[string]]::new()
try {
 # Wait for ffmpeg's first captured frame before changing any switch.
 $ready=$false
 for($attempt=0; $attempt -lt 120; $attempt++) {
  if($proc.HasExited) { throw 'ffmpeg ended before capture started.' }
  if(Test-Path -LiteralPath 'C01-cong-2bit/video/capture-progress.log') {
   $progress=Get-Content -LiteralPath 'C01-cong-2bit/video/capture-progress.log' -Raw
   if($progress -match 'frame=[1-9]') { $ready=$true; break }
  }
  Start-Sleep -Milliseconds 250
 }
 if(-not $ready) { throw 'Timed out waiting for actual first captured frame.' }
 $clock.Restart()
 Start-Sleep -Seconds 2
 foreach($case in $cases) {
  $A,$B,$Cin=$case
  $target=@{ A0=($A-band 1); A1=($A-shr 1); B0=($B-band 1); B1=($B-shr 1); Cin=$Cin }
  foreach($key in @('A0','B0','A1','B1','Cin')) { if($current[$key] -ne $target[$key]) { Click-Switch $positions[$key]; $current[$key]=$target[$key] } }
  $sum=$A+$B+$Cin
  $message="A=$A  B=$B  Cin=$Cin  | EXPECTED Cout S1 S0 = $([Convert]::ToString($sum,2).PadLeft(3,'0'))"
  Write-Caption $message
  $line=('{0:F3}s | {1}' -f $clock.Elapsed.TotalSeconds,$message)
  $events.Add($line); Write-Output $line
  Start-Sleep -Seconds 3
 }
} finally {
 if(-not $proc.HasExited) { $proc.StandardInput.WriteLine('q'); $proc.StandardInput.Flush(); $proc.WaitForExit(15000) | Out-Null }
 $errors.Result | Set-Content -LiteralPath 'C01-cong-2bit/video/ffmpeg.log'
 $events | Set-Content -LiteralPath 'C01-cong-2bit/video/cases.log'
}
if($proc.ExitCode -ne 0) { throw "ffmpeg exit $($proc.ExitCode), see video/ffmpeg.log" }
Write-Output "Saved $Output"














