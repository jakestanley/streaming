function GetPatches {
    param (
        $PwadDir,
        $Files,
        $Merge
    )

    $dehs = @()
    $pwads = @()
    $mwads = @()

    # TODO null checks on $Merge

    # build lists of map specific files we need to pass in
    foreach($patch in $Files.Split("|")) {
        $fileExtension = [System.IO.Path]::GetExtension($patch).ToLower()
        if ($fileExtension -like "*.deh") {
            $dehs += Join-Path -Path $PwadDir -ChildPath $patch
        } elseif($fileExtension -like "*.wad") {
            $pwads += Join-Path -Path $PwadDir -ChildPath $patch
        } else {
            # ignore file
        }
    }

    # for chocolate doom/vanilla wad merge emulation
    foreach($merge in $Merge.Split("|")) {
        $mwads += Join-Path -Path $PwadDir -ChildPath $merge
    }

    return [PSCustomObject]@{
        Dehs = $dehs
        Pwads = $pwads
        Mwads = $mwads
    }
}

Export-ModuleMember -Function GetPatches