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

- obsws-python
- [simple-term-menu](https://pypi.org/project/simple-term-menu/)

```
pip install -U obsws-python simple-term-menu
```

## Scripting OBS

I'm referencing my bass stream from the past year when writing OBS commands: https://github.com/jakestanley/midi-obs-ws-thing/blob/main/app.js

# Thanks

## ChatGPT
For when my patience was wearing thin with PowerShell, and because I'm lazy.

## Doom Text Generator
Thanks to https://c.eev.ee/doom-text-generator for the rendered stream overlay text

## Doom Wiki
Wanted to include their logo as I am using their resource. I'm not affiliated with the Doom Wiki but they are a great bunch. You can visit them here: https://doomwiki.org/
