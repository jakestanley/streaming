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

function GetMapSelection {
    param (
        $Maps = $(throw "Maps argument missing")
    )
    if(!(Get-Command Out-GridView -ErrorAction SilentlyContinue)) {
        Write-Debug "Out-GridView not supported. Attempting to use simple-term-menu"
        $options = @()
        foreach($map in $Maps) {
            $options += GetMapNameString($map)
        }
        
        # uses last exit code to obtain selected item
        & simple-term-menu -t "Select a map" $options
        $selected = $LASTEXITCODE-1
        if ($selected -lt 0) {
            return $null
        } else {
            $map = $Maps[$selected]
        }
    } else {
        $map = $Maps | Out-GridView -Title "Select a map" -OutputMode Single
    }
    return $map
}

function GetDemoSelection {
    param (
        $DemoDir = $(throw "DemoDir argument missing"),
        $DemoPrefix = $(throw "DemoPrefix argument missing")
    )

    $demos = @()
    Get-ChildItem -Path $DemoDir -Filter ("{0}*.lmp" -f $DemoPrefix) | ForEach-Object {
        $demos += $_.NameString
    }

    if(!(Get-Command Out-GridView -ErrorAction SilentlyContinue)) {
        Write-Debug "Out-GridView not supported. Attempting to use simple-term-menu"

        # uses last exit code to obtain selected item
        & simple-term-menu -t "Select a demo file" $demos
        $selected = $LASTEXITCODE-1
        if ($selected -lt 0) {
            return $null
        } else {
            $demo = $demos[$selected]
        }
    } else {
        # TODO multiple demo support
        $demo = $demos | Out-GridView -Title "Select a demo" -OutputMode Single
    }
    return $demo
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
    Write-Host ("Overriding with source port '{0}'" -f $SourcePort)
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

    $map = GetMapSelection($maps)

    if (!$map) {
        Write-Error "A map was not selected"
        Exit 1
    }

    # default arguments
    $dargs = [System.Collections.ArrayList]::new()
    $dargs.AddRange(@("-nomusic", "-skill", 4))
    $demo_prefix = ""

    # detect which IWAD we need and the map id format
    if ($map.Map -match "^E(\d)M(\d)$") {
        Write-Host "Detected a Doom map string"
        $demo_prefix="DOOM" # default just in case no pwad is provided
        $episodeno = [int]$Matches[1]
        $mapno = [int]$Matches[2]
        $dargs.AddRange(@("-warp", $episodeno, $mapno))
        $dargs.AddRange(@("-iwad", (Join-Path -Path $iwad_dir -ChildPath "DOOM.WAD")))
    } elseif($map.Map -match "^MAP(\d+)$") {
        Write-Host "Detected a Doom II map string"
        $demo_prefix="DOOM2" # default just in case no pwad is provided
        $mapno = [int]$Matches[1]
        $dargs.AddRange(@("-warp", $mapno))
        $dargs.AddRange(@("-iwad", (Join-Path -Path $iwad_dir -ChildPath "DOOM2.WAD")))
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
        $dargs.Add("-deh");
        $dargs.AddRange($dehs)
    }

    if ($pwads.Count -gt 0) {
        $demo_prefix = [System.IO.Path]::GetFileNameWithoutExtension($pwads[0])
        $dargs.Add("-file")
        $dargs.AddRange($pwads)
    }

    # Set map title in OBS
    ${r_client}?.Call("SetInputSettings", @{
        inputName = "Text"
        inputSettings = @{
            text = $map.Title + " - " + $map.Author
        }
    })

    if ($ReRecord) {
        $demo = GetDemoSelection $demo_dir $demo_prefix
        if(!$demo) {
            Write-Error "A demo was not selected"
            Exit 1
        }
        $dargs.AddRange(@("-playdemo", (Join-Path -Path $demo_dir -ChildPath $demo)))
    }

    # record the demo
    # TODO: check demo directory is writeable
    if ($ReRecord || $NoDemo) {} else {
        $time= (Get-Date).ToString("yyyy-MM-ddTHmmss")
        $dargs.AddRange(@("-record", (Join-Path -Path $demo_dir -ChildPath ("{0}-{1}-{2}.lmp" -f $demo_prefix, $map.Map, $time))))
    }

    # if the port must be chocolate doom or we have overridden to use chocolate doom (support for more later)
    $SourcePort = ($SourcePort -ne "") ? $SourcePort : $map.Port
    Write-Debug $SourcePort
    if ($SourcePort -ne "") {

        if ($mwads.Count -gt 0) {
            $dargs.Add("-merge")
            $dargs.AddRange($mwads)
        }
        
        Write-Debug "Starting chocolate-doom with the following arguments:"
        $dargs.AddRange(@("-config", $chocolatedoom_cfg_default, "-extraconfig", $chocolatedoom_cfg_extra))
        $executable = $chocolatedoom_path
    } else {

        $complevel = $map.CompLevel -replace '^$', $default_complevel
        if ($complevel -ne "") {
            $dargs.AddRange(@("-complevel", $complevel))
        }
        
        $dargs.Add("-window")
        Write-Debug "Starting dsda-doom with the following arguments:"
        $executable = $dsda_path
    }

    foreach($arg in $dargs) {
        Write-Debug `t`t$arg
    }
    Start-Sleep 3

    ${r_client}?.SetCurrentProgramScene("Playing")
    $ReRecord ? (${r_client}?.StartRecord()) : $null
    Start-Process -FilePath $executable -ArgumentList $dargs -Wait
    $ReRecord ? (${r_client}?.StopRecord()) : $null
    ${r_client}?.SetCurrentProgramScene("Waiting")

} finally { 
    ${r_client}?.TearDown()
}

Write-Host "Script exiting"
