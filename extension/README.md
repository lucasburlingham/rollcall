# Extension Installation

During development, the extension can be installed by navigating to [about:debugging#/runtime/this-firefox](about:debugging#/runtime/this-firefox) and clicking on "Load Temporary Add-on...". Select the `manifest.json` file in the extension directory.

## How it works

The extension does two basic things:

1. It automatically gets the current tab's URL and associated messages from the server API and displays them in the extension window (sidebar or popup) at extension startup.
2. It allows the user to send a message to the server API to be inserted into the database.
