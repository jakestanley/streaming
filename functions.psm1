function ParseLevelStats {
    param (
        [string] $RawLevelStats = ""
    )

    $LevelStats = [PSCustomObject]@{
        Time = "???"
        Kills = "???"
        Items = "???"
        Secrets = "???"
    }

    #"E1M1 - 0:13.11 (0:13)  K: 3/4  I: 15/37  S: 2/3 "
    if($RawLevelStats -match "\d+:\d+.\d+") {
        $time = [string]$Matches[0]
        $LevelStats.Time = $time
    } else {
        return $null
    }

    if($RawLevelStats -match "K: (\d+\/\d+)") {
        $kills = $Matches[1]
        $LevelStats.Kills = $kills
    }

    if($RawLevelStats -match "S: (\d+\/\d+)") {
        $secrets = $Matches[1]
        $LevelStats.Secrets = $secrets
    }

    if($RawLevelStats -match "I: (\d+\/\d+)") {
        $items = $Matches[1]
        $LevelStats.Items = $items
    }

    return $LevelStats
}