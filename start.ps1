#!/usr/bin/env pwsh
Param(
    [switch] [Parameter(HelpMessage="OBS control will be disabled")] $NoObs,
    [switch] [Parameter(HelpMessage="Re-record a completed demo")] $ReRecord,
    [switch] [Parameter(HelpMessage="play a random map")] $Random,
    [switch] [Parameter(HelpMessage="Demo recording will be disabled")] $NoDemo,
    [string] [Parameter(HelpMessage="Override source port")] $SourcePort,
    [string] [Parameter(HelpMessage="Path to configuration file")] $ConfigPath = ".\config.json",
    [string] [Parameter(HelpMessage="Path to maps CSV file")] $CsvFilePath = ".\Season1.csv"
)

Import-Module OBSWebSocket

# declare functions here
function GetMapNameString {
    param (
        $Map
    )
    return '"#{0}: {1} | {2} | {3}"' -f $map.Ranking, $map.Title, $map.Author, $map.Map
}

# script begins in earnest
$json = Get-Content $ConfigPath -Raw
$config = ConvertFrom-Json $json

# TODO: should use source port configured comp level if this is not set
$default_complevel=$config.default_complevel
$dsda_path=$config.dsda_path
$chocolatedoom_path=$config.chocolatedoom_path
$chocolatedoom_cfg_default=$config.chocolatedoom_cfg_default
$chocolatedoom_cfg_extra=$config.chocolatedoom_cfg_extra
$iwad_dir=$config.iwad_dir
$pwad_dir=$config.pwad_dir
$demo_dir=$config.demo_dir

if ($NoObs) {
    Write-Host "OBS will NOT be controlled"
}

if ($SourcePort) {
    Write-Host "Overriding with source port '{}'" -f $SourcePort
}

Write-Debug "Configuration:"
Write-Debug "`tdefault_complevel: $default_complevel"
Write-Debug "`tdsda_path: $dsda_path"
Write-Debug "`tchocolatedoom_path: $chocolatedoom_path"
Write-Debug "`tchocolatedoom_cfg_default: $chocolatedoom_cfg_default"
Write-Debug "`tchocolatedoom_cfg_extra: $chocolatedoom_cfg_extra"
Write-Debug "`tiwad_dir: $iwad_dir"
Write-Debug "`tpwad_dir: $pwad_dir"
Write-Debug "`tdemo_dir: $demo_dir"

try {

    # Connect to OBS and switch to the "waiting" scene
    $r_client = $NoObs ? $null : (Get-OBSRequest -hostname "localhost" -port 4455)
    ${r_client}?.SetCurrentProgramScene("Waiting")

    # load maps from CSV
    $csvData = Import-Csv $CsvFilePath

    $maps = @()
    foreach ($row in $csvData) {
        $maps += $row
    }

    if(!(Get-Command Out-GridView -ErrorAction SilentlyContinue)) {
        Write-Debug "Out-GridView not supported. Attempting to use simple-term-menu"
        $options = @()
        foreach($map in $maps) {
            $options += GetMapNameString($map)
        }
        
        # use last exit code to obtain selected item
        & simple-term-menu $options
        $selected = $LASTEXITCODE-1
        if ($selected -lt 0) {
            Write-Error "A map was not selected"
            Exit 1
        }

        $map = $maps[$selected]
    } else {
        $map = $maps | Out-GridView -Title "Select a map" -OutputMode Single
    }

    if (!$map) {
        Write-Error "A map was not selected"
        Exit 1
    }

    # default arguments
    $complevel = $map.CompLevel -replace '^$', $default_complevel
    $args = [System.Collections.ArrayList]::new()
    $args.AddRange(@("-nomusic", "-skill", 4))
    $demo_prefix = ""

    # detect which IWAD we need and the map id format
    if ($map.Map -match "^E(\d)M(\d)$") {
        Write-Host "Detected a Doom map string"
        $demo_prefix="DOOM" # default just in case no pwad is provided
        $episodeno = [int]$Matches[1]
        $mapno = [int]$Matches[2]
        $args.AddRange(@("-warp", $episodeno, $mapno))
        $args.AddRange(@("-iwad", (Join-Path -Path $iwad_dir -ChildPath "DOOM.WAD")))
    } elseif($map.Map -match "^MAP(\d+)$") {
        Write-Host "Detected a Doom II map string"
        $demo_prefix="DOOM2" # default just in case no pwad is provided
        $mapno = [int]$Matches[1]
        $args.AddRange(@("-warp", $mapno))
        $args.AddRange(@("-iwad", (Join-Path -Path $iwad_dir -ChildPath "DOOM2.WAD")))
    } else {
        Write-Error "Could not parse Map value: '$map.Map'"
    }

    $dehs = @()
    $pwads = @()
    $mwads = @()

    # build lists of map specific files we need to pass in
    foreach($patch in $map.Files.Split("|")) {
        $fileExtension = [System.IO.Path]::GetExtension($patch).ToLower()
        if ($fileExtension -like "*.deh") {
            $dehs += Join-Path -Path $pwad_dir -ChildPath $patch
        } elseif($fileExtension -like "*.wad") {
            $pwads += Join-Path -Path $pwad_dir -ChildPath $patch
        } else {
            # ignore file
        }
    }

    # for chocolate doom/vanilla wad merge emulation
    foreach($merge in $map.Merge.Split("|")) {
        $mwads += Join-Path -Path $pwad_dir -ChildPath $merge
    }

    if ($dehs.Count -gt 0) {
        $args.Add("-deh");
        $args.AddRange($dehs)
    }

    if ($pwads.Count -gt 0) {
        $demo_prefix = [System.IO.Path]::GetFileNameWithoutExtension($pwads[0])
        $args.Add("-file")
        $args.AddRange($pwads)
    }

    # Set map title in OBS
    ${r_client}?.Call("SetInputSettings", @{
        inputName = "Text"
        inputSettings = @{
            text = $map.Title + " - " + $map.Author
        }
    })


    # record the demo
    # TODO: check demo directory is writeable
    if (!$NoDemo) {
        $time= (Get-Date).ToString("yyyy-MM-ddTHmmss")
        $args.AddRange(@("-record", (Join-Path -Path $demo_dir -ChildPath ("{0}-{1}-{2}.lmp" -f $demo_prefix, $map.Map, $time))))
    }

    # if the port must be chocolate doom or we have overridden to use chocolate doom (support for more later)
    if ($map.Port -eq "chocolate" || $SourcePort -eq "chocolate") {

        if ($mwads.Count -gt 0) {
            $args.Add("-merge")
            $args.AddRange($mwads)
        }
        
        Write-Debug "Starting chocolate-doom with the following arguments:"
        $args.AddRange(@("-config", $chocolatedoom_cfg_default, "-extraconfig", $chocolatedoom_cfg_extra)) 
        $executable = $chocolatedoom_path
    } else {
        # default to dsda-doom and set complevel args
        $args.AddRange(@("-complevel", $complevel, "-window")) 
        Write-Debug "Starting dsda-doom with the following arguments:"
        $executable = $dsda_path
    }

    foreach($arg in $args) {
        Write-Debug `t`t$arg
    }
    Start-Sleep 3

    ${r_client}?.SetCurrentProgramScene("Playing")
    Start-Process -FilePath $executable -ArgumentList $args -Wait
    ${r_client}?.SetCurrentProgramScene("Waiting")

} finally { 
    ${r_client}?.TearDown()
}

Write-Host "Script exiting"
