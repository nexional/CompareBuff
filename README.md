```
 _______ _______ __   __ _______ _______ ______   _______ _______ __   __ _______ _______ 
|       |       |  |_|  |       |   _   |    _ | |       |  _    |  | |  |       |       |
|       |   _   |       |    _  |  |_|  |   | || |    ___| |_|   |  | |  |    ___|    ___|
|       |  | |  |       |   |_| |       |   |_||_|   |___|       |  |_|  |   |___|   |___ 
|      _|  |_|  |       |    ___|       |    __  |    ___|  _   ||       |    ___|    ___|
|     |_|       | ||_|| |   |   |   _   |   |  | |   |___| |_|   |       |   |   |   |    
|_______|_______|_|   |_|___|   |__| |__|___|  |_|_______|_______|_______|___|   |___|    

```
# CompareBuff

**CompareBuff** is Sublime Text package which allows you to compare any two open files/buffers
using an external comparison tool like Beyond Compare. To benefit from this package you must
have the external tool installed and the tool must allow the files to be passed as command-line
arguments.

Using this package you can compare current file/buffer with any other open file/buffer from
any existing sublime windows. Once you invoke the command you'll be asked to select another
file/buffer which you wish to compare against the current one.

Take a look at **How to Use** for usage.

## Installation

* Install [Sublime Text Package Control](https://packagecontrol.io). Skip if installed already
* Go to _Tools > Command Palette_. Select `Package Control: Install Package`
* Type or select `CompareBuff` and hit Enter
* Wait for installation to finish

## How to use

First off you need to configure External tool path and other optional settings. Head over to **Customization** & come back to this section.

Once you have basic setup, you can invoke the command in few ways:

* Command Palette (_Ctrl+Shift+P_ on Windows or _Cmd+Shift+P_ on Mac) > Input/select `CompareBuff: compare with...`
* Right click context menu (if enabled) select `CompareBuff: compare with...`
* User defined key shortcut (see **Defining Key Binding**)

This will present a quick panel where you can select other file/buffer to compare against the
current one. Once you select second file/buffer the external comparison tool will launch using those.

You can also click window label inside panel. It will open that window's views in a new panel for selection. It's useful when you have number of views open.

## How does it work

Once you launch the command, the package works on the file/buffers as below before sending to tool:

* if the buffer is a valid file with **no** unsaved modifications the original file is directly sent to tool
* if the buffer is a valid file with **any** unsaved modifications then a temp file is created with original file name & sent across
* if the buffer is a scratch/untitled then a temp file is created and sent across
* if `prefer_selection` is `true` (default) then only selected lines/blocks (if any) are sent across for that file/buffer

## Defining Key Binding

You can also define the binding in your User Key Binding file (_Preferences > Key Bindings_ ) e.g.

`{ "keys": ["ctrl+alt+/"], "command": "compare_buff" }`

## Customization

You can override the default settings in User Settings file (_Preferences > Package Settings > CompareBuff > Settings_):
```
{
    // Provide the External Comparison tool path here e.g. Beyond Compare.
    // Make sure you use the correct path of the binary as it exists
    // ** WINDOWS **
    "external_tool_path": "C:\\Program Files\\Beyond Compare 4\\BCompare.exe",

    // NOTE: Above command will send the selected buffers as argument implicitly but
    // if you need to send more than two arguments to the external tool then you can
    // define as below where {0} and {1} are replaced with the buffers you select
    // "external_tool_path": [ "C:\\Program Files\\Beyond Compare 4\\BCompare.exe", "--file1", "{0}", "--file2", "{1}" ],

    // ** MAC-OS **
    // "external_tool_path": "/Applications/Beyond Compare.app/Contents/MacOS/bcomp",
    // ** LINUX **
    // "external_tool_path": "/usr/bin/bcompare",

    // Just selection to be sent for comparison
    "prefer_selection": true,

    // Show command in view (right-click) context menu
    "show_in_context_menu": false,

    // Number of recent items to show in panel
    "number_of_recent_items": 3,

    // Show file preview in the panel
    "file_preview_in_panel": true,

    // Icons, you can disable if you see [?] in panel
    "icons":
    {
        "enable": true,
        "icon_ellipsis": "…",
        "icon_package": "🗗",
        "icon_recent_files": "🗍",
        "icon_scratch_file": "🗋",
        "icon_valid_file": "🗎",
        "icon_window": "🗔"
    }
}
```

## License

[GNU General Public License v3.0](https://github.com/nexional/CompareBuff/blob/master/LICENSE)

## Issues

Please report any bugs/issues [here](https://github.com/nexional/CompareBuff/issues/new)

## My other work
* [ConvertEpochToDate](https://packagecontrol.io/packages/ConvertEpochToDate)

## Links
* [Beyond Compare](https://www.scootersoftware.com/download.php)