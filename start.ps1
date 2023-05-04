Import-Module OBSWebSocket

$json = Get-Content .\config.json -Raw
$config = ConvertFrom-Json $json

$default_complevel=$config.default_complevel
$dsda_path=$config.dsda_path
$iwad_dir=$config.iwad_dir
$pwad_dir=$config.pwad_dir
$demo_dir=$config.demo_dir

Write-Host "Configuration:"
Write-Host "`tdefault_complevel: $default_complevel"
Write-Host "`tdsda_path: $dsda_path"
Write-Host "`tiwad_dir: $iwad_dir"
Write-Host "`tpwad_dir: $pwad_dir"
Write-Host "`tdemo_dir: $demo_dir"

$csvFilePath = ".\Season1.csv"

try {

    # Connect to OBS and switch to the "waiting" scene
    $r_client = Get-OBSRequest -hostname "localhost" -port 4455
    $r_client.SetCurrentProgramScene("Waiting")

    # load maps from CSV
    $csvData = Import-Csv $csvFilePath

    $maps = @()
    foreach ($row in $csvData) {
        $maps += $row
    }

    $map = $maps | Out-GridView -Title "Select a map" -OutputMode Single
    if (!$map) {
        Write-Error "A map was not selected"
        Exit 1
    }

    # default arguments
    $complevel = $map.CompLevel -replace '^$', $default_complevel
    $args = "-complevel " + $complevel + " -window -nomusic -skill 4 "

    # default
    $demo_prefix = ""
    $demo_name = ""

    # detect which IWAD we need and the map id format
    if ($map.Map -match "^E(\d)M(\d)$") {
        Write-Host "Detected a Doom map string"
        $episodeno = [int]$Matches[1]
        $mapno = [int]$Matches[2]
        $args += "-warp $episodeno $mapno "
        $args += "-iwad $iwad_dir\DOOM.WAD "
    } elseif($map.Map -match "^MAP(\d+)$") {
        Write-Host "Detected a Doom II map string"
        $mapno = [int]$Matches[1]
        Write-Host $mapno
        $args += "-warp $mapno "
        $args += "-iwad $iwad_dir\DOOM2.WAD "
    } else {
        Write-Error "Could not parse Map value: '$map.Map'"
    }

    $dehs = @()
    $pwads = @()

    # build lists of map specific files we need to pass in
    foreach($patch in $map.Files.Split("|")) {
        $fileExtension = [System.IO.Path]::GetExtension($patch).ToLower()
        if ($fileExtension -like "*.deh") {
            $dehs += "$pwad_dir\$patch"
        } elseif($fileExtension -like "*.wad") {
            $pwads += "$pwad_dir\$patch"
        } else {
            # ignore file
        }
    }

    if ($dehs.Count -gt 0) {
        $args += "-deh $dehs "
    }

    if ($pwads.Count -gt 0) {
        $demo_prefix = [System.IO.Path]::GetFileNameWithoutExtension($pwads[0])
        $args += "-file $pwads "
    }

    # Set map title in OBS
    $r_client.Call("SetInputSettings", @{
        inputName = "Text"
        inputSettings = @{
            text = $map.Title + " - " + $map.Author
        }
    })

    # record the demo
    $time= (Get-Date).ToString("yyyy-MM-ddTHmmss")
    $arg_record = "-record " + "$demo_dir" + "\" + $demo_prefix + "-" + $map.Map + "-" + "$time" + ".lmp "
    $args += $arg_record

    Write-Host "Starting dsda-doom with the following arguments:"
    Write-Host $args

    $r_client.SetCurrentProgramScene("Playing")
    Start-Process -FilePath $dsda_path -ArgumentList $args -Wait
    $r_client.SetCurrentProgramScene("Waiting")

    # $resp = $r_client.GetVersion()
    # Write-Host "obs version:", $resp.obsVersion
    # Write-Host "websocket version:", $resp.obsWebSocketVersion

} finally { 
    $r_client.TearDown() 
}
