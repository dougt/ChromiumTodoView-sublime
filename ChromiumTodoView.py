import sublime
import sublime_plugin

import json
import os
import re
import string
import subprocess
import sys
import webbrowser

class ChromiumTodoViewHandler(sublime_plugin.EventListener):
    def __init__(self):
      # We are looking for strings that look like:
      # TODO(123456): blah blah blah.
      self._todo_regex = re.compile('.+TODO\(([0-9]+)\):.*')
      self.SETTINGS_FILE = "ChromiumTodoView.sublime-settings"
      self.load_settings()

    def check_setting(self, value):
      self.settings.add_on_change(value, self.load_settings)
      if self.settings.get(value) == None:
        print("ChromiumTodoView: " + value + " is not set in " + self.SETTINGS_FILE)
        sublime.status_message("ChromiumTodoView not loaded.")
        return

    def load_settings(self):
      self.settings = sublime.load_settings(self.SETTINGS_FILE)
      self.check_setting("depot_tools")
      self.check_setting("python_cmd")
      self.check_setting("bug_tracker")

    def on_hover(self, view, point, hover_zone):
        sublime.set_timeout_async(lambda: self.on_hover_async(view, point, hover_zone))

    def on_hover_async(self, view, point, hover_zone):
      if hover_zone == sublime.HOVER_TEXT:
          s = view.substr(view.line(point))
          m = self._todo_regex.match(s)
          if m:
            data = self.get_issue_data(m.group(1))
            if data == None:
              return;
            self.show_popup(view, data, point)

    @staticmethod
    def open_in_browser(url):
      try:
        webbrowser.open_new_tab(url)
      except(webbrowser.Error):
        sublime.error_message('Failed to open browser. See "Customizing the browser" in the README.')

    def get_issue_data(self, issue):
      # In order to easily access chromium's bug tracker, we'd like to reuse the
      # auth code in depot_tools. However, Sublime Text 3 and depot tools use
      # different versions of python. Until that's resolved, we are going to
      # call out to the python version in depot tools. Yes, this is horrible.
      try:
        path_to_python = self.settings.get('python_cmd')
        path_to_get_data_script = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'get_chromium_issue_data.py')
        path_to_depot_tools = self.settings.get('depot_tools')

        si = None
        # On windows, we don't want to show the console starting when we start
        # the subprocess.
        if sys.platform == 'win32':
          si = subprocess.STARTUPINFO()
          si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        output = subprocess.check_output([path_to_python, path_to_get_data_script, issue, path_to_depot_tools], startupinfo=si)

        content = json.loads(output.decode("utf-8"))
        if not content:
          sublime.status_message("ChromiumTodoView: Could not decode server result");
          return None
        return content

      except subprocess.CalledProcessError as e:
        if (e.returncode == 1):
          sublime.status_message("ChromiumTodoView: Unknown error occurred");
          print("ChromiumTodoView: Error! "+ e.output.decode("utf-8").rstrip())

        if (e.returncode == 2):
          sublime.status_message("ChromiumTodoView: "+ e.output.decode("utf-8").rstrip())

        return None

    def show_popup(self, view, data, point):
      issue = str(data['id']);
      summary = data['summary']
      status = data['status']
      url = self.settings.get('bug_tracker') + issue

      html = string.Template("""
                <body id=show-scope>
                    <style>
                        p {
                            margin-top: 0;
                        }
                        a {
                            font-family: sans-serif;
                            font-size: 1.05rem;
                        }
                    </style>
                    <p><b>${summary}</b></p>
                    <a href="${issue_url}">Issue ${issue_number}</a>
                    <p>Status: <b>${status}</b></p>
                </body>
            """)

      values = {
        'summary' : summary,
        'status'  : status,
        'issue_number': issue,
        'issue_url':  url
      }
      html = html.substitute(values)
      view.show_popup(html,
        location=point,
        on_navigate=lambda x: ChromiumTodoViewHandler.open_in_browser(url))
