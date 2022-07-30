import sublime
import sublime_plugin
import re
import os
import os.path
import tempfile
import subprocess

rec_objs = []
rec_list = []
view_objs = []
panel_objs = []
icons = {}
package_settings = 'CompareBuff.sublime-settings'

def plugin_loaded():
    global settings, icons
    settings = sublime.load_settings(package_settings)
    settings.clear_on_change('show_in_context_menu')
    settings.add_on_change('show_in_context_menu', CompareBuffContextMenuCommand.is_visible())
    settings.clear_on_change('icons')
    settings.add_on_change('icons', load_icons())
    load_icons()

def with_icon(icon, string):
    global icons
    return(' '.join(filter(None, [icons.get(icon), string])))

this_package = with_icon('icon_package', 'CompareBuff: ')

def load_icons():
    global icons
    icons = settings.get('icons')
    if not (icons and icons.get('enable') and icons.get('enable') in [True, False]): icons = {}

class Buffers(sublime_plugin.EventListener):
    def on_activated(self, view):
        global panel_objs, rec_objs, rec_list, settings, max_rec
        curr_win = view.window()
        for win in panel_objs:
            if win == curr_win: continue
            win.run_command('hide_overlay')
            panel_objs.remove(win)

        max_rec = settings.get('number_of_recent_items')
        if not max_rec or int(max_rec) < 0: return
        if not view.is_valid() \
            or view.settings().get('is_widget') \
            or view == view.window().find_output_panel('find_results') \
            or view == view.window().find_output_panel('package_dev'): return

        for v in rec_objs:
            index = rec_objs.index(v)
            if v.is_valid():
                rec_list[index] = get_view_name(v)
            else:
                rec_objs.pop(index)
                rec_list.pop(index)

        if view in rec_objs:
            index = rec_objs.index(view)
            rec_objs.pop(index)
            rec_list.pop(index)
        elif len(rec_list) == (max_rec + 1):
            rec_list.pop()
            rec_objs.pop()

        rec_list.insert(0, get_view_name(view))
        rec_objs.insert(0, view)

class CompareBuffContextMenuCommand(sublime_plugin.WindowCommand):
    def run(self):
        global curr_win
        curr_win = self.window
        curr_win.run_command('compare_buff')

    def is_visible(self=None):
        global settings
        return(settings.get('show_in_context_menu'))

class CompareBuffCommand(sublime_plugin.WindowCommand):
    def run(self, toggle_show_in_context_menu=False, toggle_prefer_selection=False, configure_external_tool_path=False, configure_number_of_recent_items=False, toggle_icons=False):
        global curr_win, curr_view, settings
        curr_win = self.window
        settings = sublime.load_settings(package_settings)
        if settings_update(locals()): return
        curr_view = curr_win.active_view()
        if curr_view is None or not (curr_view.is_valid() and validate_external_tool()): return
        validate_prefer_selection()
        sort_and_place_first()
        prepare_quick_panel()
        launch_quick_panel()

def settings_update(locals):
    if True not in locals.values(): return False
    if locals['toggle_show_in_context_menu']:
        settings.clear_on_change('show_in_context_menu')
        settings.set('show_in_context_menu', not settings.get('show_in_context_menu'))
        settings.add_on_change('show_in_context_menu', CompareBuffContextMenuCommand.is_visible())
        sublime.save_settings(package_settings)
        sublime.message_dialog(this_package + 'Context menu now ' + ('enabled' if settings.get('show_in_context_menu') else 'disabled'))
    elif locals['toggle_prefer_selection']:
        settings.set('prefer_selection', not settings.get('prefer_selection'))
        sublime.save_settings(package_settings)
        sublime.message_dialog(this_package + 'prefer_selection now ' + ('enabled' if settings.get('prefer_selection') else 'disabled'))
    elif locals['configure_external_tool_path']:
        path = settings.get('external_tool_path')
        if not (path and os.path.exists(path) and os.path.isfile(path)):
            platform = sublime.platform()
            if platform == 'windows': path = 'C:\\Program Files\\Beyond Compare 4\\BCompare.exe'
            elif platform == 'osx': path = '/Applications/Beyond Compare.app/Contents/MacOS/bcomp'
            elif platform == 'linux': path = '/usr/bin/bcompare'
        def on_done(path):
            path = re.sub('''^["']|["']$''', '', path.strip())
            if path and os.path.exists(path) and os.path.isfile(path):
                settings.set('external_tool_path', path)
                sublime.save_settings(package_settings)
                sublime.message_dialog(this_package + 'External tool path updated to \'' + path + '\'')
            else:
                sublime.error_message(this_package + 'External tool path \'' + path + '\' does not exist')
                curr_win.show_input_panel('External Comparison tool path:', path, on_done, None, None)
        curr_win.show_input_panel('External Comparison tool path:', path, on_done, None, None)
    elif locals['configure_number_of_recent_items']:
        num = str(settings.get('number_of_recent_items'))
        if num is None or not num.isdigit() or int(num) < 0: num = 3
        def on_done(num):
            if num and num.isdigit() and int(num) >= 0:
                settings.set('number_of_recent_items', int(num))
                sublime.save_settings(package_settings)
                sublime.message_dialog(this_package + 'number_of_recent_items updated to ' + str(num))
            else:
                sublime.error_message(this_package + 'please provide a valid whole number')
                curr_win.show_input_panel('number_of_recent_items:', num, on_done, None, None)
        curr_win.show_input_panel('number_of_recent_items:', num, on_done, None, None)
    elif locals['toggle_icons']:
        settings.clear_on_change('icons')
        icons = settings.get('icons')
        icons['enable'] = not icons['enable']
        settings.set('icons', icons)
        settings.add_on_change('icons', load_icons())
        sublime.save_settings(package_settings)
        sublime.message_dialog(this_package + 'icons now ' + ('enabled' if settings.get('icons')['enable'] else 'disabled'))
    return True

def validate_external_tool():
    global settings, external_tool_path
    external_tool_path = settings.get('external_tool_path')
    if not (os.path.exists(external_tool_path) and os.path.isfile(external_tool_path)):
        sublime.error_message(this_package + 'External tool path \'' + external_tool_path + '\' is invalid.\nPlease check \'external_tool_path\' value under Preferences > Package Settings > CompareBuff > Settings')
        return False
    return True

def validate_prefer_selection():
    global settings, prefer_selection
    prefer_selection = settings.get('prefer_selection')
    if prefer_selection not in [True, False]: prefer_selection = True

def prepare_quick_panel():
    global view_objs, win_list, view_list, rec_list, max_rec
    view_objs = []
    view_list = []
    curr_view = curr_win.active_view()
    for win in win_list:
        if win == curr_win:
            if len(win.views()) <= 1: continue
            win_str = 'this window'
        else:
            if not win.views(): continue
            win_str = 'window#' + str(win.id())

        folder_bases = []
        proj = win.project_data()
        if proj:
            for folder in proj['folders']:
                folder_base = os.path.basename(folder['path'])
                if folder_base: folder_bases.append(folder_base)
            if folder_bases: win_str += ' (' + ', '.join(folder_bases) + ')'

        view_objs.append(win)
        win_str = with_icon('icon_window', win_str)
        view_list.append(win_str)

        for view in win.views():
            if view == curr_view: continue
            view_objs.append(view)
            view_list.append(get_view_name(view))

    if max_rec and len(rec_list) > 1:
        view_list = rec_list[1:] + view_list
        view_list.insert(0, with_icon('icon_recent_files', 'recent files'))
        view_objs = rec_objs[1:] + view_objs
        view_objs.insert(0, 'recent files')

def get_view_name(view):
    path = view.file_name()
    w = view.window()
    is_active_view = (w and view == w.active_view())

    if path:
        view_name = os.path.basename(path) + ('*' if view.is_dirty() else '')
        view_name = with_icon('icon_valid_file', '[' + view_name + ']' if is_active_view else view_name)
    else:
        first_line = view.substr(sublime.Region(0,75)).encode('unicode_escape').decode()
        view_name = (first_line + with_icon('icon_ellipsis', '') if first_line else 'untitled')
        view_name = with_icon('icon_scratch_file', '[' + view_name + ']' if is_active_view else view_name)
    return('    ' + view_name)

def sort_and_place_first():
    global curr_win, win_list
    win_list = sublime.windows()
    n = len(win_list)
    while True:
        newn = 0
        for i in range(1, n):
            if win_list[i-1].id() > win_list[i].id():
                win_list[i-1], win_list[i] = win_list[i], win_list[i-1]
                newn = i
        n = newn
        if (n <= 1): break
    win_list.insert(0, win_list.pop(win_list.index(curr_win)))

def launch_quick_panel():
    def on_select(i):
        global panel_objs, view_objs, curr_view, curr_win, external_tool_path, view_list, external_tool_name
        if curr_win in panel_objs: panel_objs.remove(curr_win)
        if i == -1: return

        target = view_objs[i]
        if (isinstance(target, sublime.Window) or isinstance(target, sublime.View)) and not target.is_valid():
            sublime.error_message(this_package + 'window or view does not exist')
            return

        if target in sublime.windows() + ['recent files']:
            if (target != 'recent files' and isinstance(target, sublime.Window) and not target.views()):
                sublime.error_message(this_package + 'window has no open views')
                return
            v_start = i + 1
            views = rec_objs[1:] if target == 'recent files' else target.views()
            offset = len(views) - (1 if target == curr_win else 0)
            v_end = v_start + offset
            view_objs = view_objs[v_start:v_end]
            view_list = list(map(lambda x: re.sub(r'^\s*', '', x), view_list[v_start:v_end]))
            if curr_win not in panel_objs: panel_objs.append(curr_win)
            curr_win.show_quick_panel(items=view_list, selected_index=-1, on_select=on_select)
            return

        sublime.status_message(this_package + 'Opening external tool for comparison...')
        try: subprocess.Popen([external_tool_path, get_path(curr_view), get_path(target)])
        except Exception as e: sublime.error_message(this_package + str(e))

    global curr_win, view_list
    if not view_list:
        sublime.status_message(this_package + 'not enough views')
        return
    if curr_win not in panel_objs: panel_objs.append(curr_win)
    curr_win.run_command('hide_overlay')
    curr_win.show_quick_panel(items=view_list, selected_index=-1, on_select=on_select)

def anything_selected(view):
    return(any(map(lambda x: not x.empty(), view.sel())))

def get_path(view):
    global prefer_selection
    path = view.file_name()
    selection = (prefer_selection and anything_selected(view))
    if not (path is not None and os.path.exists(path) and os.path.isfile(path) and not view.is_dirty() and not selection):
        content = ''
        if selection:
            for region in view.sel():
                content = '\n'.join(filter(None, [content, view.substr(region)]))
        else: content = view.substr(sublime.Region(0, view.size()))

        fd, tmp_path = tempfile.mkstemp(suffix = '.txt')
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(content)
        if path is not None:
            path = os.path.join(os.path.dirname(tmp_path), os.path.basename(path))
            os.replace(tmp_path, path)
        else: path = tmp_path
    return(path)

