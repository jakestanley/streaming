#!/usr/bin/env pwsh
Param(
    [switch] [Parameter(HelpMessage="OBS control will be disabled")] $NoObs,
    [string] [Parameter(HelpMessage="Which scene should OBS switch to when game starts")] $PlayScene = "Playing",
    [switch] [Parameter(HelpMessage="Re-record a completed demo")] $ReRecord,
    [switch] [Parameter(HelpMessage="Automatically record and stop when gameplay ends")] $AutoRecord,
    [switch] [Parameter(HelpMessage="Play a random map")] $Random,
    [switch] [Parameter(HelpMessage="Demo recording will be disabled")] $NoDemo,
    [switch] [Parameter(HelpMessage="Use Crispy Doom instead of Chocolate Doom")] $Crispy,
    [switch] [Parameter(HelpMessage="If saved, play last map")] $Last,
    [string] [Parameter(HelpMessage="Override source port")] $SourcePort,
    [string] [Parameter(HelpMessage="Path to configuration file")] $ConfigPath = ".\config.json",
    [string] [Parameter(HelpMessage="Path to maps CSV file")] $CsvFilePath = (".\Season1.csv")
)

Import-Module OBSWebSocket
Import-Module ./common.psm1
Import-Module ./functions.psm1

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
    if ($Last) {
        if (Test-Path -Path ".\last.json") {
            $lastmap = Get-Content ".\last.json" -Raw | ConvertFrom-Json
            Write-Debug ("-Last flag set and found previous map")
            return $lastmap
        } else {
            Write-Debug ("-Last flag set but no previous map was found")
        }
    }
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
    $map | ConvertTo-Json | Out-File ".\last.json"
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

function RenameOutputFile {
    Param (
        $OutputPath,
        $DemoName
        )

    if ($OutputPath -eq "") {
        Write-Debug "OutputPath was empty"
    } elseif($DemoName -eq "") {
        Write-Debug "DemoName was empty"
    } else {
        $extension = [System.IO.Path]::GetExtension($OutputPath)
        $newOutputPath = [System.IO.Path]::Combine([System.IO.Path]::GetDirectoryName($OutputPath), $DemoName + $extension)
        Write-Debug ("Moving `n`t'{0}' to `n`t'{1}'" -f $OutputPath, $newOutputPath)

        # pause for 5 seconds to let OBS release any handles
        Start-Sleep(5)
        Rename-Item -Path $OutputPath -NewName $newOutputPath
    }
}

function RemoveLevelStatFile {
    if (Test-Path -Path ".\levelstat.txt") {
        Write-Debug "Found old levelstat.txt file. Deleting"
        Remove-Item ".\levelstat.txt"
    }
}

function WriteStats {
    Param (
        $Stats = $(throw "Stats argument missing"),
        $DemoDir = $(throw "DemoDir argument missing"),
        $DemoName = $(throw "DemoName argument missing")
    )

    $statsJsonPath = (Join-Path -Path $DemoDir -ChildPath ("{0}-STATS.json" -f $DemoName))
    Write-Debug ("Stats will be written to: {0}" -f $statsJsonPath)

    if (Test-Path -Path ".\levelstat.txt") {

        Write-Debug "Found levelstat.txt. Writing level stats"
        
        $raw_level_stats = Get-Content ".\levelstat.txt" | Select-Object -First 1
        # Archive (in case we need to debug stats later)
        if (Test-Path -Path ".\tmp"){
            # do nothing
        } else {
            New-Item -ItemType Directory -Path ".\tmp"
        }
        $archivedLevelStatTxt = (".\tmp\levelstat_{0}.txt" -f $DemoName)
        $Stats.levelStats = ParseLevelStats($raw_level_stats)

        Write-Debug ("Moving `n`t'levelstat.txt' to `n`t'{0}'" -f $archivedLevelStatTxt)
        Move-Item -Path ".\levelstat.txt" $archivedLevelStatTxt
    } else {

        Write-Debug "No levelstat.txt found. I assume you didn't finish the level or aren't using dsda-doom"
    }

    $Stats | ConvertTo-Json | Out-File $statsJsonPath
}

# script begins in earnest
$json = Get-Content $ConfigPath -Raw
$config = ConvertFrom-Json $json

$default_complevel=$config.default_complevel
$dsda_path=$config.dsda_path
$chocolatedoom_path=$config.chocolatedoom_path
$chocolatedoom_cfg_default=$config.chocolatedoom_cfg_default
$chocolatedoom_cfg_extra=$config.chocolatedoom_cfg_extra
$iwad_dir=$config.iwad_dir
$pwad_dir=$config.pwad_dir
$demo_dir=$config.demo_dir

$stats = [PSCustomObject]@{
    map         = ""
    compLevel   = 0
    sourcePort  = ""
    args        = ""
    levelStats  = $null
}

if ($NoObs) {
    Write-Host "OBS will NOT be controlled"
}

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

    $AutoRecord ? (${r_client}?.StartRecord()) : $null
    if ($Random) {
        $map = $maps[(Get-Random -Minimum 0 -Maximum $maps.length)]
    } else {
        $map = GetMapSelection($maps)
    }

    if (!$map) {
        Write-Error "A map was not selected"
        $r_output = ${r_client}?.StopRecord()
        if ($r_output) {
            Start-Sleep(3)
            Remove-Item $r_output.outputPath
        }
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

    $stats.map = $map.Map

    $p = GetPatches $pwad_dir $map.Files $map.Merge
    $dehs = $p.Dehs
    $pwads = $p.Pwads
    $mwads = $p.Mwads

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
    $textMapName = ($map.Title -eq "" ? $map.Map : $map.Title) + " - " + $map.Author
    Write-Debug ("Title: '{0}'" -f $textMapName)
    ${r_client}?.Call("SetInputSettings", @{
        inputName = "Text Map Name"
        inputSettings = @{
            text = $textMapName
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

    # set the name of the demo. this format is subject to change
    $time= (Get-Date).ToString("yyyy-MM-ddTHHmmss")
    $demo_name = "{0}-{1}-{2}" -f $demo_prefix, $map.Map, $time

    # record the demo
    # TODO: check demo directory is writeable
    Write-Debug ("Demo name: '{0}'" -f $demo_name)
    if ($ReRecord -or $NoDemo) {} else {
        $dargs.AddRange(@("-record", (Join-Path -Path $demo_dir -ChildPath ("{0}.lmp" -f $demo_name))))
    }

    # if the port must be chocolate doom or we have overridden to use chocolate doom (support for more later)
    if ($SourcePort -ne "") {
        Write-Host ("Overriding with source port '{0}'" -f $SourcePort)
    } else {
        Write-Debug ("Using source port '{0}'" -f $map.Port)
        $SourcePort = $map.Port
    }

    # TODO: use regexes for fuzzy matching - https://stackoverflow.com/a/3495262
    $stats.sourcePort = $SourcePort
    switch ($SourcePort) {
        chocolate {
            # TODO put this in a function (may require reworking into an object)
            if ($mwads.Count -gt 0) {
                $dargs.Add("-merge")
                $dargs.AddRange($mwads)
            }

            if ($Crispy) {
                Write-Debug "Starting crispy-doom with the following arguments:"
                $stats.sourcePort = "crispy-doom"
                $executable = $config.crispydoom_path
            } else {
                Write-Debug "Starting chocolate-doom with the following arguments:"
                $stats.sourcePort = "chocolate-doom"
                $executable = $chocolatedoom_path
            }

            $dargs.AddRange(@("-config", $chocolatedoom_cfg_default, "-extraconfig", $chocolatedoom_cfg_extra))
        }
        gzdoom {
            # TODO put this in a function (may require reworking into an object)

            $executable = $config.gzdoom_path
            $dargs.AddRange(@("-config", $config.gzdoom_cfg.path))
        }
        default {
            # TODO put this in a function (may require reworking into an object)
            $complevel = $map.CompLevel -replace '^$', $default_complevel
            if ($complevel -ne "") {
                $dargs.AddRange(@("-complevel", $complevel))
            }
            $stats.compLevel = $complevel
            
            $dargs.AddRange(@("-window", "-levelstat"))
            Write-Debug "Starting dsda-doom with the following arguments:"
            $executable = $dsda_path
        }
    }

    $stats.args = $dargs
    foreach($arg in $dargs) {
        Write-Debug `t`t$arg
    }

    RemoveLevelStatFile
    Start-Sleep 3

    ${r_client}?.SetCurrentProgramScene($PlayScene)
    $ReRecord ? (${r_client}?.StartRecord()) : $null
    Start-Process -FilePath $executable -ArgumentList $dargs -Wait
    ($ReRecord -or $AutoRecord) ? ($r_output = ${r_client}?.StopRecord()) : $null
    ${r_client}?.SetCurrentProgramScene("Waiting")

    WriteStats $stats $demo_dir $demo_name

    if ($r_output) {
        RenameOutputFile $r_output.outputPath $demo_name
    }

} finally { 
    ${r_client}?.TearDown()
}

Write-Host "Script exiting"
