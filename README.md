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

### Installation

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

You can override the default settings two ways:

* From _Command Palette_ you can run following commands:
    * `CompareBuff: configure external_tool_path`
    * `CompareBuff: toggle prefer_selection`
    * `CompareBuff: toggle show_in_context_menu`
    * `CompareBuff: configure number_of_recent_items`

* User Settings file (_Preferences > Package Settings > CompareBuff > Settings_):
```
{
    // Provide the External Comparison tool path here e.g. Beyond Compare.
    // Make sure you use the correct path of the binary as it exists
    // ** WINDOWS **
    "external_tool_path": "C:\\Program Files\\Beyond Compare 4\\BCompare.exe",
    // ** MAC-OS **
    // "external_tool_path": "/usr/local/bin/bcompare",
    // ** LINUX **
    // "external_tool_path": "/usr/bin/bcompare",

    // Prefer selection(s) over whole file/buffer content for comparison
    // Turn it on when you want just selection to be sent for comparison
    "prefer_selection": true,

    // Show command in view context menu
    "show_in_context_menu": false,

    // Number of recent items
    "number_of_recent_items": 3
}
```

## License

[GNU General Public License v3.0](https://github.com/nexional/CompareBuff/blob/master/LICENSE)

## Issues

Please report any bugs/issues [here](https://github.com/nexional/CompareBuff/issues/new)

## Links

* [Beyond Compare](https://www.scootersoftware.com/download.php)
* [ConvertEpochToDate](https://packagecontrol.io/packages/ConvertEpochToDate) on packagecontrol.io (my other work)