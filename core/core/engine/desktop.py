import os
from . import Engine
from Qt5 import QtWidgets, QtGui

DIR = os.path.dirname(os.path.abspath(__file__))

class DesktopEngine(Engine):

    def initialize(self):
        super(DesktopEngine, self).initialize()
        self._tray_icon = None
        self._menu = None
        self._menu_items = {}
        self._separators = []
        self.register_action(
            "launch",
            self.start_qapp_in_tray_icon,
            display_name="Launch...",
            require_qt_app=True,
        )
    
    def initialize_qt_app(self):
        if not self._qt_app:
            self._qt_app = QtWidgets.QApplication([])
        return self._qt_app
    
    def start_qapp_in_tray_icon(self, *args):
        icon = QtGui.QIcon(ICON_PATH)
        self._tray_icon = QtWidgets.QSystemTrayIcon(icon)
        self._menu = QtWidgets.QMenu()
        self._menu.aboutToShow.connect(self._generate_menu)
        self._tray_icon.setContextMenu(self._menu)
        self._tray_icon.show()
        self.qt_app.exec_()
    
    def destroy(self):
        if self._tray_icon:
            del self._tray_icon
        if self._qt_app:
            self._qt_app.quit()
            self._qt_app = None
    
    def _generate_menu(self):
        self._menu_items = {}
        self._separators = []
        self._menu.clear()
        try:
            # TODO: use list_engine_menu_entries
            for action in self._actions.values():
                for alias in action.get("aliases", []):
                    self._add_menu_item(self._menu, alias, self.execute_action, args=[action["name"]])
            self._separators.append(self._menu.addSeparator())
            for action in self._actions.values():
                self._add_menu_item(self._menu, action["display_name"], self.execute_action, args=[action["name"]])
        finally:
            self._separators.append(self._menu.addSeparator())
            if is_reloader_enabled():
                self._add_menu_item(
                    self._menu,
                    "Reload Engine",
                    reload_engine,
                )
            self._add_menu_item(
                self._menu,
                "Exit",
                self._on_exit,
            )
    
    def _on_exit(self):
        self.destroy()
    
    def _add_menu_item(self, parent, path, callback, args=[]):
        parts = path.split("/")
        current_path = ""
        current = parent
        for p in parts[:-1]:
            current_path += "/{}".format(p)
            if current_path not in self._menu_items:
                current = current.addMenu(p)
                self._menu_items[current_path] = current
            else:
                current = self._menu_items[current_path]
        action = current.addAction(parts[-1])
        def launch_callback(*_args, **_kwargs):
            all_args = args + list(_args)
            return callback(*all_args, **_kwargs)
        action.triggered.connect(launch_callback)
        return action
