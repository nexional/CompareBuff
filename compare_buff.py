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
space = '    '
package_settings = 'CompareBuff.sublime-settings'

def plugin_loaded():
    global settings, icons
    settings = sublime.load_settings(package_settings)
    settings.clear_on_change('show_in_context_menu')
    settings.add_on_change('show_in_context_menu', CompareBuffContextMenuCommand.is_visible())
    settings.clear_on_change('icons')
    settings.add_on_change('icons', load_icons())

def with_icon(icon, string):
    global icons
    if icons.get(icon): return(' '.join(filter(None, [icons.get(icon), string])))
    else: return string

this_package = with_icon('icon_package', 'CompareBuff: ')

def load_icons():
    global icons
    icons = settings.get('icons')
    if not (icons and icons.get('enable') and icons.get('enable') in [True, False]): icons = {}

class RecentFiles(sublime_plugin.EventListener):
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
            or view == view.window().find_output_panel('package_dev'): \
            return

        for v in rec_objs:
            index = rec_objs.index(v)
            if not v.is_valid():
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
        validate_settings('show_in_context_menu')
        return(settings.get('show_in_context_menu'))

class CompareBuffCommand(sublime_plugin.WindowCommand):
    def run(self):
        global curr_win, curr_view, settings
        curr_win = self.window
        curr_view = curr_win.active_view()
        if curr_view is None or not curr_view.is_valid(): return
        if not validate_settings('external_tool_path','prefer_selection',  'show_in_context_menu', 'number_of_recent_items', 'file_preview_in_panel', 'icons'): return
        load_icons()
        sort_and_place_first()
        prepare_quick_panel()
        launch_quick_panel()

def validate_settings(*params):
    global settings, external_tool_path, prefer_selection
    settings = sublime.load_settings(package_settings)
    for param in params:
        if param == 'external_tool_path':
            external_tool_path = settings.get('external_tool_path')
            if external_tool_path is None or not (os.path.exists(external_tool_path) and os.path.isfile(external_tool_path)):
                sublime.error_message(this_package + 'External tool path \'' + external_tool_path + '\' is not valid')
                return False
        elif param == 'prefer_selection':
            prefer_selection = settings.get('prefer_selection')
            if prefer_selection is None or prefer_selection not in (True, False):
                prefer_selection = True
                settings.set('prefer_selection', prefer_selection)
                sublime.save_settings(package_settings)
        elif param == 'show_in_context_menu':
            show_in_context_menu = settings.get('show_in_context_menu')
            if show_in_context_menu is None or show_in_context_menu not in (True, False):
                show_in_context_menu = False
                settings.set('show_in_context_menu', show_in_context_menu)
                sublime.save_settings(package_settings)
        elif param == 'number_of_recent_items':
            num = str(settings.get('number_of_recent_items'))
            if num is None or not num.isdigit() or int(num) < 0:
                num = 3
                settings.set('number_of_recent_items', int(num))
                sublime.save_settings(package_settings)
        elif param == 'file_preview_in_panel':
            file_preview_in_panel = settings.get('file_preview_in_panel')
            if file_preview_in_panel is None or file_preview_in_panel not in (True, False):
                file_preview_in_panel = True
                settings.set('file_preview_in_panel', file_preview_in_panel)
                sublime.save_settings(package_settings)
        elif param == 'icons':
            icons = settings.get('icons')
            if icons is None:
                icons = {}
                icons['enable'] = true
            if icons['enable'] is None or icons['enable'] not in (True, False):
                icons['enable'] = true
                settings.clear_on_change('icons')
                settings.set('icons', icons)
                sublime.save_settings(package_settings)
                settings.add_on_change('icons', load_icons())
    return True

def prepare_quick_panel():
    global settings, view_objs, win_list, view_list, rec_list, max_rec
    view_objs = []
    view_list = []
    curr_view = curr_win.active_view()
    for win in win_list:
        if win == curr_win:
            if len(win.views()) <= 1: continue
            win_str = 'THIS WINDOW'
        else:
            if not win.views(): continue
            win_str = 'WINDOW#' + str(win.id())

        win_content = ''
        folder_bases = []
        proj = win.project_data()
        if proj:
            for folder in proj['folders']:
                folder_base = os.path.basename(folder['path'])
                if folder_base: folder_bases.append(folder_base)
            if folder_bases: win_content = space + '(' + ', '.join(folder_bases) + ')'

        view_objs.append(win)
        win_str = with_icon('icon_window', win_str)
        if settings.get('file_preview_in_panel'): win_str = [win_str, win_content]
        else: win_str = [win_str + win_content, '']
        view_list.append(win_str)

        for view in win.views():
            if view == curr_view: continue
            view_objs.append(view)
            view_list.append(get_view_name(view))

    if max_rec and len(rec_list) > 1:
        for v in rec_objs:
            index = rec_objs.index(v)
            if v.is_valid():
                rec_list[index] = get_view_name(v)

        view_list = rec_list[1:] + view_list
        view_list.insert(0, with_icon('icon_recent_files', 'RECENT FILES'))
        view_objs = rec_objs[1:] + view_objs
        view_objs.insert(0, 'RECENT FILES')

def check_active(view, view_name):
    w = view.window()
    return('[' + view_name + ']' if (w and view == w.active_view()) else view_name)

def get_view_name(view):
    global settings
    path = view.file_name()
    if path:
        view_name = os.path.basename(path) + ('*' if view.is_dirty() else '')
        view_name = space + with_icon('icon_valid_file', check_active(view, view_name))
    else:
        view_name = space + with_icon('icon_scratch_file', check_active(view, 'untitled'))

    first_line = view.substr(sublime.Region(0,75)).encode('unicode_escape').decode()
    view_content = space * 2 + (first_line + with_icon('icon_ellipsis', '') if first_line else '<empty>')
    return([view_name, view_content if settings.get('file_preview_in_panel') else ''])

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

        if target in sublime.windows() + ['RECENT FILES']:
            if (target != 'RECENT FILES' and isinstance(target, sublime.Window) and not target.views()):
                sublime.error_message(this_package + 'window has no open views')
                return
            v_start = i + 1
            views = rec_objs[1:] if target == 'RECENT FILES' else target.views()
            offset = len(views) - (1 if target == curr_win else 0)
            v_end = v_start + offset
            view_objs = view_objs[v_start:v_end]
            view_sub_list = []
            for view_name in view_list[v_start:v_end]:
                view_sub_list.append(list(map(lambda x: re.sub(r'^    ', '', x), view_name)))
            view_list = view_sub_list
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

