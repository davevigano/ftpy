# ftpy

A simple, lightweight FTP client with a small GUI, built with Python and [FreeSimpleGUI](https://github.com/spyoungtech/FreeSimpleGUI).

## Features

* Connect to an FTP server with an address, username and password
* Upload one or more files at once
* Browse, download and delete files already on the server
* Save connection details locally for quick reuse

## Requirements

* Windows — the client relies on Windows-only APIs for error dialogs and downloads
* Python 3.9.6 or higher
* pip 21.3.1 or higher

## Installation

1. Download `client.py` and `requirements.txt` into a folder
2. Open a terminal in that folder
3. Install dependencies: `pip install -r requirements.txt`
4. Run the client: `python client.py`

The first run creates a `saved_servers.csv` file used to store saved connections.

## Usage

1. Enter the server address, username and password, then click **CONNECT**
2. **UPLOAD** to send one or more local files to the server
3. **FILE MANAGER** to view, download or delete files already on the server
4. **SAVE CONNECTION DATA** to store the current credentials for next time, and **SEE SAVED DATA** to reuse or delete them later

## Notes / Limitations

* The client does not manage folders — only files in the current directory are shown
* Saved connection data (including the password) is stored in plain text in `saved_servers.csv` — don't use "save connection data" on a shared or untrusted machine
