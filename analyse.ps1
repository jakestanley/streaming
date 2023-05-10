#!/usr/bin/env pwsh
Param(
    [string] [Parameter(HelpMessage="Path to configuration file")] $ConfigPath = ".\config.json",
    [string] [Parameter(HelpMessage="Path to maps CSV file")] $CsvFilePath = ".\Season1.csv"
)

Import-Module ./common.psm1

$json = Get-Content $ConfigPath -Raw
$cfg = ConvertFrom-Json $json

# load maps from CSV
$csvData = Import-Csv $CsvFilePath

foreach ($map in $csvData) {
    $p = GetPatches $cfg.pwad_dir $map.Files $map.Merge
    $demo_prefix = [System.IO.Path]::GetFileNameWithoutExtension($p.Pwads[0])
    $demo_prefix += ("-{0}" -f $map.Map)
    $demos_for_map = Get-ChildItem -Path $cfg.demo_dir -Filter ("{0}*" -f $demo_prefix)
    if ($demos_for_map.Count -gt 0) {
        Write-Host ("{0} attemps: {1}" -f $demo_prefix, $demos_for_map.Count)
    }
    
}
