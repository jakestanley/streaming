#!/usr/bin/env pwsh
Param(
    [string] [Parameter(HelpMessage="Path to configuration file")] $ConfigPath = ".\config.json",
    [string] [Parameter(HelpMessage="Path to maps CSV file")] $CsvFilePath = ".\Season1.csv"
)

$json = Get-Content $ConfigPath -Raw
$config = ConvertFrom-Json $json

# load maps from CSV
$csvData = Import-Csv $CsvFilePath

$maps = @()
foreach ($row in $csvData) {
    $maps += $row
}