Import-Module ./common.psm1

class Map {
    [string]$Season
    [int]$Ranking
    [string]$Title
    [string]$Author
    [string]$Map
    [string]$Notes
    [string]$DoomWiki
    [string]$IWAD
    [string]$Attempts
    [string]$Files
    [string]$Port
    [string]$Merge
    [string]$CompLevel

    Map([PSCustomObject]$CsvRow, [string]$MapId) {
        $this.Season = $CsvRow.Season
        $this.Ranking = $CsvRow.Ranking
        $this.Title = $CsvRow.Title
        $this.Author = $CsvRow.Author
        $this.IWAD = $CsvRow.IWAD
        $this.Files = $CsvRow.Files
        $this.Port = $CsvRow.Port
        $this.Merge = $CsvRow.Merge
        $this.CompLevel = $CsvRow.CompLevel
        $this.Map = $MapId
    }

    Map([PSCustomObject]$CsvRow, [string]$MapId, [string]$MapTitle) {
        $this.Season = $CsvRow.Season
        $this.Ranking = $CsvRow.Ranking
        $this.Title = $MapTitle
        $this.Author = $CsvRow.Author
        $this.IWAD = $CsvRow.IWAD
        $this.Files = $CsvRow.Files
        $this.Port = $CsvRow.Port
        $this.Merge = $CsvRow.Merge
        $this.CompLevel = $CsvRow.CompLevel
        $this.Map = $MapId
    }
}

function getMapEntries {
    param (
        $WadEntries
    )

    $mapEntries = @()
    foreach($entry in $WadEntries) {
        if ($entry -match "(E\dM\d|MAP\d\d|MAPINFO)$") {
            $mapEntries += $Matches[1]
        }
    }
    $mapEntries
}

function getMapsFromMapInfo {
    param (
        $mod, $file
    )

    Write-Debug "Found MAPINFO entry"
    $mapinfo = wad-read $file "MAPINFO"
    foreach($entry in $mapinfo) {
        if($entry -match "(E\dM\d|MAP\d\d) ""(.*)""$"){
            $mapId = $Matches[1]
            $mapTitle = $Matches[2]
            Write-Output [Map]::new($mod, $mapId, $mapTitle)
        }
    }
}

function GetMapsFromModList {
    param (
        $ModList
    )

    foreach ($mod in $ModList) {
        $files = GetPwads $pwad_dir $mod.Files
        
        foreach ($file in $files) {
            # TODO: cache this info. use shasum or something
            $wadEntries = (wad-ls $file)
            $mapEntries = getMapEntries $wadEntries
            if (${mapEntries}?.Contains("MAPINFO")) {
                Write-Output getMapsFromMapInfo $mod $file
            } else {
                foreach($map in $mapEntries) {
                    Write-Output [Map]::new($mod, $map)
                }
            }
        }
    }
}

# TODO unit test lol
# Describe

Export-ModuleMember -Function GetMapsFromModList