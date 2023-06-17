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
}

function GetMapsFromModList {
    param (
        $ModList
    )

    foreach ($mod in $ModList) {
        $files = GetPwads $pwad_dir $mod.Files
        
        foreach ($file in $files) {
            # TODO: cache this info. use shasum or something
            $wadentries = wad-ls $file
            $filemaps = [System.Collections.ArrayList]::new()
            foreach($entry in $wadentries) {
                if ($entry -match "(MAPINFO)$") {
                    Write-Debug "Found MAPINFO entry"
                    $filemaps = @()
                    $mapinfo = wad-read $file "MAPINFO"
                    # TODO parse MAPINFO wad-read output
                    break
                } elseif ($entry -match "(E\dM\d|MAP\d\d)$") {
                    foreach($key in $Matches.Keys){
                        if (!$filemaps.Contains($Matches[$key])) {
                            # not doing this will cause the function to output the indexes.
                            #  ffs this took ages to figure out
                            [Void]$filemaps.Add($Matches[$key])
                        }
                    }
                }
            }
            
            foreach($mapId in ($filemaps | Sort-Object)) {
                $map = [Map]::new($mod, $mapId)
                Write-Output $map
            }
        }
    }
}

# TODO unit test lol
# Describe

Export-ModuleMember -Function GetMapsFromModList