Import-Module ./common.psm1

class Map {
    [int]$Season
    [int]$Ranking
    [int]$PlayOrder
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
}

function GetMapsFromModList {
    param (
        $ModList
    )

    $maps = [System.Collections.ArrayList]::new()
    foreach ($mod in $ModList) {
        $files = GetPwads $pwad_dir $mod.Files
        
        foreach ($file in $files) {
            # TODO: cache this info. use shasum or something
            $wadentries = wad-ls $file
            $filemaps = [System.Collections.ArrayList]::new()
            foreach($entry in $wadentries) {
                if ($entry -match "(E\dM\d|MAP\d\d|MAPINFO)$") {
                    foreach($key in $Matches.Keys){
                        if (!$filemaps.Contains($Matches[$key])) {
                            $filemaps.Add($Matches[$key])
                        }
                    }
                }
            }

            if ($filemaps.Contains("MAPINFO")) {
                $mapinfo = wad-read $file "MAPINFO"
                Write-Debug "Found MAPINFO entry"
            } else {
                Write-Debug "No MAPINFO found. Will use MAP entries"
                foreach($mapId in $filemaps) {
                    # $mod
                    $maps.Add([Map]::new($mod, $mapId))
                }
            }
        }

        # TODO duplicate map data for resulting table
    }

    return $maps
}

# TODO unit test lol
# Describe

Export-ModuleMember -Function GetMapsFromModList