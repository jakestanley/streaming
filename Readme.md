# Setup

## Configuration

### Script variables

- Update `config.json` accordingly. Currently the script is not resilient to missing values.

### Playlist format (CSV)

At the time of writing, the script is hard coded to read a playlist from `.\Season1.csv`

The following values _MUST_ currently be present in the map CSV for the script to work:

- `CompLevel` determines the compatibility level
	- If empty, `default_complevel` from `config.json` is used
- `Map` determines the map identifier. 
	- Expected formats are 'E1M1' (Doom) or 'MAP01' (Doom 2)
- `Files` determines the files that need to be loaded. 
	- Currently DEH and WAD are supported. 
	- Multiple files MUST be separated by a pipe character. 
	- This can be empty.
- `Merge` is for use with chocolate doom to specify which files require the `-merge` parameter
	- See [WAD merging capability](https://www.chocolate-doom.org/wiki/index.php/WAD_merging_capability)
- `Title` determines the map title that MAY be displayed on the stream
- `Author` determines the map author that MAY be displayed on the stream
- `Port` determines the port to use, i.e `chocolate` for chocolate doom.
	- Defaults to dsda-doom

The following values are not yet required but _MAY_ be utilised later:

- `Season` (or `Year`) (undecided)
	- Corresponds to an [Cacowards](https://doomwiki.org/wiki/Cacowards) or [Top 100 WADs of All Time](https://doomwiki.org/wiki/Top_100_WADs_of_All_Time) year
	- MAY be displayed on the stream
- `Ranking`
	- Where the WAD placed in that years list. If not present MAY be empty. 
	- Considering removing this as it appears to have only been used from 1994 to 2003
- `Play Order`
	- Not required but serves to inform the user on the map select view
- `Notes`
	- Not required but serves to inform the user on the map select view
- `Doom wiki`
	- Not required. Link to the mod
- `IWAD`
 	- Not required. Currently inferred from the map identifier format whether to use DOOM.WAD or DOOM2.WAD
 	- The IWADs must be present for the relevant game in `iwad_dir` for this to work.

## Configure OBS

### Enable WebSocket server

- Menu -> Tools -> WebSocket Server Settings
- Check "Enable WebSocket server"
- Uncheck "Enable Authentication"
- Keep the default port, should be 4455

### Scenes and inputs

The `start.ps1` script is expecting the following scenes and inputs:
- Input "Text" for the map title, displayed at the top of the screen
- Scenes "Waiting" and "Playing" for switching between the map selection and game in progress states

These are subject to change.

## PowerShell

I'm not that sharp with PowerShell and Windows package management but here's my best attempt.

### Upgrade PowerShell

```
winget install --id Microsoft.Powershell --source winget
```

Close PowerShell and launch PowerShell 7. You may wish to set this as the default Windows Terminal profile.

### Install OBSWebSocket

- Documentation: https://github.com/onyx-and-iris/OBSWebSocket-Powershell
- Requests: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#requests
- PowerShell Gallery: https://www.powershellgallery.com/packages/OBSWebSocket/0.0.4

```
Install-Module -Name OBSWebSocket -Scope CurrentUser
```

## Python

### Install dependencies

```
pip install -r requirements.txt
```

## Testing

Run any scripts in `lib/py` or `lib/ps` with the `test_` prefix
I intend to add more tests later excepting UI tests.

```
lib/py/test_*.py
```

## Scripting OBS

I'm referencing my bass stream from the past year when writing OBS commands: https://github.com/jakestanley/midi-obs-ws-thing/blob/main/app.js

# Post-processing

## Extract audio tracks

Assuming that you have the OBS audio channels set up like I do in the format:

- All
- Desktop
- Microphone

Then you can use the following PowerShell snippet to separate the audio tracks for easier editing later:
```
foreach ($file in (Get-ChildItem "." -Filter *.mkv)) {

    $streams = ffprobe -v error -select_streams a $file.FullName -show_entries stream=index:stream_tags=title -of csv=p=0 | ConvertFrom-Csv -Header Index,Title
    $desktopStream = $streams | Where-Object {$_.Title -eq "Desktop"}
    $microphoneStream = $streams | Where-Object {$_.Title -eq "Microphone"}

    $desktopStreamIndex = $desktopStream.Index
    $microphoneStreamIndex = $microphoneStream.Index
    $desktopStreamIndex = [int]$desktopStreamIndex - 1
    $microphoneStreamIndex = [int]$microphoneStreamIndex - 1

    Write-Host $desktopStreamIndex
    Write-Host $microphoneStreamIndex

    # Use ffmpeg to extract the "Desktop" and "Microphone" audio streams
    ffmpeg -i $file.FullName -map 0:a:$desktopStreamIndex -c:a copy ("{0}_Desktop.m4a" -f $file.BaseName)
    ffmpeg -i $file.FullName -map 0:a:$microphoneStreamIndex -c:a copy ("{0}_Microphone.m4a" -f $file.BaseName)
}
```

## Convert to format supported by iMovie (sorry, it's what I like)

I'm assuming you are doing this on an Nvidia card with CUDA support.

```
Get-ChildItem -Path "." -Filter *.mkv | ForEach-Object { ffmpeg.exe -hwaccel cuvid -i $_.FullName -c:v h264_nvenc -cq:v 20 -b:v 4M -maxrate:v 8M -bufsize:v 16M -c:a copy $($_.FullName -replace '.mkv','.mp4') }
```

## Use SSH to copy to your editing machine

## Or you could do all of the above in one loop

I also added a bit on archiving

```
if (-not (Test-Path -Path ".\Originals" -PathType Container)) {
    New-Item -ItemType Directory -Path ".\Originals"
}

foreach ($file in (Get-ChildItem "." -Filter *.mkv)) {

    $streams = ffprobe -v error -select_streams a $file.FullName -show_entries stream=index:stream_tags=title -of csv=p=0 | ConvertFrom-Csv -Header Index,Title
    $desktopStream = $streams | Where-Object {$_.Title -eq "Desktop"}
    $microphoneStream = $streams | Where-Object {$_.Title -eq "Microphone"}

    $desktopStreamIndex = $desktopStream.Index
    $microphoneStreamIndex = $microphoneStream.Index
    $desktopStreamIndex = [int]$desktopStreamIndex - 1
    $microphoneStreamIndex = [int]$microphoneStreamIndex - 1

    Write-Host $desktopStreamIndex
    Write-Host $microphoneStreamIndex

    # Use ffmpeg to extract the "Desktop" and "Microphone" audio streams
    ffmpeg -i $file.FullName -map 0:a:$desktopStreamIndex -c:a copy ("{0}_Desktop.m4a" -f $file.BaseName)
    ffmpeg -i $file.FullName -map 0:a:$microphoneStreamIndex -c:a copy ("{0}_Microphone.m4a" -f $file.BaseName)
    ffmpeg -hwaccel cuvid -i $file.FullName -c:v h264_nvenc -cq:v 20 -b:v 4M -maxrate:v 8M -bufsize:v 16M -c:a copy $($file.FullName -replace '.mkv','.mp4')
    Move-Item -Path $file.FullName -Destination ".\Originals\"
}
```

# Optional functionality

- [maghoff/wad](https://github.com/maghoff/wad) for reading wad data (requires [rust](https://doc.rust-lang.org/cargo/getting-started/installation.html))

# Thanks

## ChatGPT
For when my patience was wearing thin with PowerShell, and because I'm lazy.

## Doom Text Generator
Thanks to https://c.eev.ee/doom-text-generator for the rendered stream overlay text

## Doom Wiki
Wanted to include their logo as I am using their resource. I'm not affiliated with the Doom Wiki but they are a great bunch. You can visit them here: https://doomwiki.org/
