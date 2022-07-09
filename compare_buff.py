import sublime
import sublime_plugin
import re
import os
import os.path
import tempfile
import subprocess

package_icon = u'\U0001F5D7 '
this_package =  package_icon + 'CompareBuff: '
package_settings = 'CompareBuff.sublime-settings'
context_menu_file = os.path.join(sublime.packages_path(), 'CompareBuff', 'Context.sublime-menu')
context_content = """[
    {
        "caption": "CompareBuff: compare with...",
        "command": "compare_buff",
    },
    {
        "caption": "-"
    }
]
"""

def plugin_loaded():
    settings = sublime.load_settings(package_settings)
    settings.clear_on_change('show_in_context_menu')
    settings.add_on_change('show_in_context_menu', implement_context_menu)

def implement_context_menu():
    global context_menu_file, context_content
    if (sublime.load_settings(package_settings).get('show_in_context_menu')):
        package_dir = os.path.dirname(context_menu_file)
        if not os.path.exists(package_dir): os.makedirs(package_dir)
        with open(context_menu_file, 'w') as f:
            f.write(context_content)
    else:
        try: os.remove(context_menu_file)
        except: pass

class CompareBuffCommand(sublime_plugin.WindowCommand):
    def run(self, toggle_context_menu=False, toggle_prefer_selection=False, configure_tool_path=False):
        self.curr_win = self.window
        settings = sublime.load_settings(package_settings)
        if True in locals().values():
            if toggle_context_menu:
                settings.clear_on_change('show_in_context_menu')
                show_in_context_menu = not settings.get('show_in_context_menu')
                settings.set('show_in_context_menu', show_in_context_menu)
                settings.add_on_change('show_in_context_menu', implement_context_menu)
                sublime.save_settings(package_settings)
                status = 'enabled' if show_in_context_menu else 'disabled'
                sublime.message_dialog(this_package + 'Context menu now ' + status)
            elif toggle_prefer_selection:
                prefer_selection = not settings.get('prefer_selection')
                settings.set('prefer_selection', prefer_selection)
                sublime.save_settings(package_settings)
                status = 'enabled' if prefer_selection else 'disabled'
                sublime.message_dialog(this_package + 'prefer_selection is now ' + status)
            elif configure_tool_path:
                external_tool_path = settings.get('external_tool_path')
                def on_done(path):
                    path = re.sub("""^["']|["']$""", '', path.strip())
                    if path and os.path.exists(path) and os.path.isfile(path):
                        settings.set('external_tool_path', path)
                        sublime.save_settings(package_settings)
                        sublime.message_dialog(this_package + 'External tool path updated to \'' + path + '\'')
                    else:
                        sublime.error_message(this_package + 'External tool path \'' + path + '\' does not exist')
                        self.curr_win.show_input_panel('External Comparison tool path:', path, on_done, None, None)
                self.curr_win.show_input_panel('External Comparison tool path:', external_tool_path, on_done, None, None)
            return

        self.external_tool_path = settings.get('external_tool_path')
        if os.path.exists(self.external_tool_path) and os.path.isfile(self.external_tool_path):
            self.external_tool_name = os.path.basename(self.external_tool_path)
        else:
            sublime.error_message(this_package + 'External tool path \'' + self.external_tool_path + '\' is invalid.\nPlease check \'self.external_tool_path\' value under Preferences > Package Settings > CompareBuff > Settings')
            return

        self.prefer_selection = settings.get('prefer_selection')
        if self.prefer_selection not in [True, False]: self.prefer_selection = True

        self.curr_view = self.curr_win.active_view()
        if self.curr_view is None or not self.curr_view.is_valid(): return
        self.view_objs = []
        self.view_list = []
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
        win_list.insert(0, win_list.pop(win_list.index(self.curr_win)))

        valid_file_icon = u'\U0001F5CE '
        scratch_icon = u'\U0001F5CB '
        window_icon = u'\U0001F5D4 '
        ellipsis_icon = u'\u2026 '
        for win in win_list:
            if win == self.curr_win:
                if len(win.views()) - 1 <= 0: continue
                win_str = 'this window'
            else:
                if not win.views(): continue
                win_str = 'window ' + str(win.id())

            self.view_objs.append(win)
            win_str = window_icon + win_str
            self.view_list.append(win_str)

            for view in win.views():
                if view == self.curr_view: continue
                self.view_objs.append(view)
                path = view.file_name()
                if path: view_name = valid_file_icon + os.path.basename(path)
                else:
                    first_line = view.substr(sublime.Region(0,75)).encode('unicode_escape').decode()
                    view_name = scratch_icon + (first_line + ellipsis_icon if first_line else 'untitled')
                self.view_list.append('    ' + view_name)
        self.user_input()

    def user_input(self):
        self.curr_win.show_quick_panel(items=self.view_list, selected_index=-1, on_select=self.on_select)

    def on_select(self, i):
        if i == -1: return
        target = self.view_objs[i]

        if not target.is_valid():
            sublime.error_message('window or view does not exist')
            return

        if target in sublime.windows():
            if not target.views():
                sublime.error_message('window has no open views')
                return
            v_start = i + 1
            offset = len(target.views()) - (1 if target == self.curr_win else 0)
            v_end = v_start + offset
            self.view_objs = self.view_objs[v_start:v_end]
            self.view_list = list(map(lambda x: re.sub(r'^\s*', '', x), self.view_list[v_start:v_end]))
            self.user_input()
            return

        sublime.status_message(this_package + 'Opening tool \'' + self.external_tool_name + '\' for comparison...')
        try: subprocess.Popen([self.external_tool_path, self.get_path(self.curr_view), self.get_path(target)])
        except Exception as e: sublime.error_message(this_package + str(e))

    def anything_selected(self, view):
        return(any(map(lambda x: not x.empty(), view.sel())))

    def get_path(self, view):
        path = view.file_name()
        selection = (self.prefer_selection and self.anything_selected(view))
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

