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

**CompareBuff** is Sublime Text package which provides interface for selecting buffers across open sublime windows which then are sent across to external comparison tool like Beyond Compare. To benefit from this package you must have the external tool installed and the tool must allow the files to be passed as command-line arguments.

You can configure the parameters and arguments to be sent to external tool. Take a look at _How to Use_ for usage.

### Installation

* Install [Sublime Text Package Control](https://packagecontrol.io). Skip if installed already
* Go to _Tools > Command Palette_. Select `Package Control: Install Package`
* Type or select `CompareBuff` and hit Enter
* Wait for installation to finish

## How to use

First off you need to configure external tool path and other optional settings. Head over to _Customization_ and come back to this section once the tool path is configured (with desired parameter if applicable) in settings.

There are two modes this package can be invoked:

#### Comparison

This command allows you to send **two** buffers to the external tool for comparison. First one is the active buffer on current window. You can select the second buffer using CompareBuff package which can be invoked in one of the following ways:

* Input/select `CompareBuff: compare with...` on Command Palette (_Ctrl+Shift+P_ on Windows or _Cmd+Shift+P_ on Mac)
* Right click context menu (if enabled) select `CompareBuff: compare with...`
* User defined key shortcut (see _Defining Key Binding_)

#### Merge

This command allows you to send **three** buffers to the external tool for merge. First one is the active buffer on current window. You can select the second & third buffers consecutively using CompareBuff package which can be invoked in one of the following ways::

* Input/select `CompareBuff: merge with...` on Command Palette (_Ctrl+Shift+P_ on Windows or _Cmd+Shift+P_ on Mac)
* Right click context menu (if enabled) select `CompareBuff: merge with...`
* User defined key shortcut (see _Defining Key Binding_)

Once `CompareBuff` is invoked it presents a quick panel where you can select other buffer(s). Inside the quick panel you can also select/click window label or 'recent files' label, which then opens that window/section's buffers in a new panel for selection. It's useful when you have number of buffers open for a certain window.

## How does it work

Once you launch the command, the package works on the selected buffers as below before sending across to tool:

* if the buffer is a valid file with **no** unsaved modifications the original file is directly sent to tool
* if the buffer is a valid file with **any** unsaved modifications then a temp file is created with original file name & sent across
* if the buffer is a scratch/untitled then a temp file is created and sent across
* if `prefer_selection` is `true` (default) then only selected lines/blocks (if any) are sent across for that buffer

## Defining Key Binding

You can also define the binding in your User Key Binding file (_Preferences > Key Bindings_ ) e.g.

```
// CompareBuff: compare with...
{ "keys": ["ctrl+alt+/"], "command": "compare_buff" }

// CompareBuff: merge with...
{ "keys": ["ctrl+alt+shift+/"], "command": "compare_buff", "args": { "merge": true } }
```

## Customization

You can override the default settings in User Settings file (_Preferences > Package Settings > CompareBuff > Settings_):
```
{
    // Provide the External Comparison tool path here e.g. Beyond Compare.
    // Make sure you use the correct path of the binary as it exists
    // ** WINDOWS **
    "external_tool_path": "C:\\Program Files\\Beyond Compare 4\\BCompare.exe",

    // NOTE: Above command will send the selected buffers as argument implicitly but
    // You can also customize the parameters for the external tool.
    // You can use {0}, {1} & {2} as placeholders in the command line params which are replaced with the the buffers you selected while launching the tool.
    // For comparison:
    // "external_tool_path": [ "C:\\Program Files\\Beyond Compare 4\\BCompare.exe", "--file1", "{0}", "--file2", "{1}" ],
    // For Merge:
    // "external_tool_path": [ "C:\\Program Files\\Beyond Compare 4\\BCompare.exe", "--file1", "{0}", "--file2", "{1}", --file3, "{2}" ],

    // ** MAC-OS **
    // "external_tool_path": "/Applications/Beyond Compare.app/Contents/MacOS/bcomp",
    // ** LINUX **
    // "external_tool_path": "/usr/bin/bcompare",

    // Just selection to be sent for comparison
    "prefer_selection": true,

    // Show command in buffer (right-click) context menu
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

### License
[GNU General Public License v3.0](https://github.com/nexional/CompareBuff/blob/master/LICENSE)

### Issues
Please report any bugs/issues [here](https://github.com/nexional/CompareBuff/issues/new)

### My other work
* [ConvertEpochToDate](https://packagecontrol.io/packages/ConvertEpochToDate)

### Links
* [Beyond Compare](https://www.scootersoftware.com/download.php)