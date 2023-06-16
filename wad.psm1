Import-Module ./common.psm1

function GetMapsFromModList {
    param (
        $ModList
    )

    $maps = @()
    foreach ($mod in $ModList) {
        $files = GetPwads $pwad_dir $mod.Files
        
        foreach ($file in $files) {
            # TODO: cache this info. use shasum or something
            $wadentries = wad-ls.exe $file
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
                Write-Host "Found MAPINFO entry"
            } else {
                Write-Host "No MAPINFO found. Will use MAP entries"
                foreach($map in $filemaps) {
                    # $mod
                    fail this does not work
                    $mod.Farts = "fart"
                    Write-Host $mod
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