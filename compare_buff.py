import sublime
import sublime_plugin
import os
import os.path
import tempfile
import subprocess

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
    settings = sublime.load_settings('CompareBuff.sublime-settings')
    settings.clear_on_change('show_in_context_menu')
    settings.add_on_change('show_in_context_menu', implement_context_menu)

def implement_context_menu():
    global context_menu_file, context_content
    if (sublime.load_settings('CompareBuff.sublime-settings').get('show_in_context_menu')):
        package_dir = os.path.dirname(context_menu_file)
        if not os.path.exists(package_dir): os.makedirs(package_dir)
        with open(context_menu_file, 'w') as f:
            f.write(context_content)
    else:
        try: os.remove(context_menu_file)
        except: pass

class CompareBuffCommand(sublime_plugin.WindowCommand):
    def run(self, toggle_context_menu=False, toggle_prefer_selection=False, configure_tool_path=False):
        curr_win = self.window
        settings = sublime.load_settings('CompareBuff.sublime-settings')
        if True in locals().values():
            if toggle_context_menu:
                settings.clear_on_change('show_in_context_menu')
                show_in_context_menu = not settings.get('show_in_context_menu')
                settings.set('show_in_context_menu', show_in_context_menu)
                settings.add_on_change('show_in_context_menu', implement_context_menu)
                status = 'enabled' if show_in_context_menu else 'disabled'
                sublime.message_dialog('CompareBuff: Context menu now ' + status)
            elif toggle_prefer_selection:
                prefer_selection = not settings.get('prefer_selection')
                settings.set('prefer_selection', prefer_selection)
                status = 'enabled' if prefer_selection else 'disabled'
                sublime.message_dialog('CompareBuff: prefer_selection is now ' + status)
            elif configure_tool_path:
                external_tool_path = settings.get('external_tool_path')
                def on_done(path):
                    path = path.strip()
                    if path and os.path.exists(path) and os.path.isfile(path):
                        settings.set('external_tool_path', path)
                        sublime.message_dialog('CompareBuff: External tool path updated to \'' + path + '\'')
                    else:
                        sublime.error_message('CompareBuff: External tool path \'' + path + '\' does not exist')
                        curr_win.show_input_panel('External Comparison tool path:', external_tool_path, on_done, None, None)
                        return
                curr_win.show_input_panel('External Comparison tool path:', external_tool_path, on_done, None, None)

            sublime.save_settings('CompareBuff.sublime-settings')
            return

        self.external_tool_path = settings.get('external_tool_path')
        if os.path.exists(self.external_tool_path) and os.path.isfile(self.external_tool_path):
            self.external_tool_name = os.path.basename(self.external_tool_path)
        else:
            sublime.error_message('CompareBuff: External tool path \'' + self.external_tool_path + '\' is invalid.\nPlease check \'self.external_tool_path\' value under Preferences > Package Settings > CompareBuff > Settings')
            return

        self.prefer_selection = settings.get('prefer_selection')
        if self.prefer_selection not in [True, False]: self.prefer_selection = True

        self.curr_view = curr_win.active_view()
        if self.curr_view is None or not self.curr_view.is_valid(): return
        self.view_objs = []
        view_list = []
        win_list = sublime.windows()
        win_list.insert(0, win_list.pop(win_list.index(curr_win)))

        for win in win_list:
            for view in win.views():
                if view == self.curr_view: continue
                self.view_objs.append(view)
                path = view.file_name()
                if path: view_name = os.path.basename(path)
                else:
                    first_line = view.substr(view.full_line(view.text_point(0,0))).strip()
                    view_name = first_line if first_line else 'untitled'

                if win != curr_win: view_name = 'Window [' + str(win_list.index(win) + 1) + ']: ' + view_name
                view_list.append(view_name)

        curr_win.show_quick_panel(view_list, self.on_select)

    def on_select(self, i):
        if i < 0: return
        sublime.status_message('CompareBuff: Opening tool \'' + self.external_tool_name + '\' for comparison...')
        try: subprocess.Popen([self.external_tool_path, self.get_path(self.curr_view), self.get_path(self.view_objs[i])])
        except Exception as e: sublime.error_message('CompareBuff: ' + str(e))

    def anything_selected(self, view):
        for region in view.sel():
            if region.empty(): continue
            else: return(True)
        return(False)

    def get_path(self, view):
        path = view.file_name()
        selection = (self.prefer_selection and self.anything_selected(view))
        if not (path is not None and os.path.exists(path) and os.path.isfile(path) and not view.is_dirty() and not selection):
            content = ''
            if selection:
                for region in view.sel():
                    if region.empty(): continue
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

