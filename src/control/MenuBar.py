from tkinter import *
from tkinter import Menu

from src.Utils import Utils


class MenuBar:
    def __init__(self, master, model, app):
        self.app = app
        self.master = master
        self.model = model
        self.model.subject.project.attach(self._update_project)

        top_menu = Menu(self.master)
        self.master.config(menu=top_menu)

        file_menu = Menu(top_menu)
        # edit_menu = Menu(top_menu)
        # debug_menu = Menu(top_menu)

        top_menu.add_cascade(label="File", menu=file_menu)
        # top_menu.add_cascade(label="Edit", menu=edit_menu)
        # top_menu.add_cascade(label="Debug", menu=debug_menu)

        self._disable_loaded = []
        self._disable_unloaded = []
        self._init_file_menu(file_menu)
        # self._init_edit_menu(edit_menu)
        # self._init_debug_menu(debug_menu)

    def _init_file_menu(self, menu):
        menu.add_command(label="New", command=self.model.prompt_create_project)
        menu.add_command(label="Open", command=self.model.prompt_load_project)
        menu.add_command(label="Save", command=self.model.save, state=DISABLED)
        menu.add_command(label="Save as", command=self.model.prompt_save_as, state=DISABLED)
        menu.add_separator()
        menu.add_command(label="Close Project", command=self.model.unload_project, state=DISABLED)
        menu.add_command(label="Export Image", command=self.model.subject.export.notify, state=DISABLED)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.master.quit)

        self._disable_unloaded.append((menu, menu.index("Save")))
        self._disable_unloaded.append((menu, menu.index("Save as")))
        self._disable_unloaded.append((menu, menu.index("Close Project")))
        self._disable_unloaded.append((menu, menu.index("Export Image")))

        # for testing that inverse works
        # self.disable_loaded.append((menu, menu.index("Open")))

    @staticmethod
    def _init_edit_menu(menu):
        menu.add_command(label="Redo", command=Utils.do_nothing)

    def _init_debug_menu(self, menu):
        menu.add_command(label="Break App", command=self.app.breakpoint_app)

    def _update_project(self):
        def set_item_state(items, state):
            for menu, index in items:
                menu.entryconfigure(index, state=state)

        if self.model.isProjectLoaded:
            set_item_state(self._disable_unloaded, NORMAL)
            set_item_state(self._disable_loaded, DISABLED)
        else:
            set_item_state(self._disable_unloaded, DISABLED)
            set_item_state(self._disable_loaded, NORMAL)
