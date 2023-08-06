"""
The root widget
===============

The root widget is the fisrt called by otinker.
It corresponds to the firts node ot the SCHEMA.

At the root widget, the whole window is created.
The root host the main Tab-notebook,
and if necessary the wiew 3D tab.

Tabs callbacks:
===============

As tabs callbacks can change any part of the memory,
These callbacks are passed down to the root widget,
trigerring two subprocesses.

Execute:
--------

Execute is about memory modification.
The callback associated shows the following singature:

nested object > callback > nested object

Update_3d_view:
---------------

Update_3d_view is about 3D feedback.
The callback associated shows the following singature:

nested object, 3D scene > callback > 3D scene

"""

import abc
from tkinter import ttk

import yaml


from opentea.gui_forms.constants import (
    PARAMS,
    load_icons,
    set_system,
)


from opentea.gui_forms.node_widgets import (
    OTNodeWidget,
    OTTabWidget,
)
from opentea.gui_forms.menus import DefaultMenubar


DEFAULT_APPS_FACTORY = {}


try:
    from opentea.gui_forms.viewer_2d import add_viewer_2d
    DEFAULT_APPS_FACTORY['viewer_2d'] = add_viewer_2d

except ImportError:
    pass

try:
    from opentea.gui_forms.viewer_3d import add_viewer_3d
    DEFAULT_APPS_FACTORY['viewer_3d'] = add_viewer_3d

except ImportError:
    pass


class OTRoot:

    def __init__(self, schema, tksession, style, data_file, apps_factory=None,
                 apps_schema=None):

        # TODO: clear tmp_dir and delete at the end (.tmp?)

        self.schema = schema
        self.tksession = tksession

        self.apps_factory = apps_factory or DEFAULT_APPS_FACTORY
        self.apps_schema = apps_schema

        self._form = None

        self.apps = dict()
        self._data_file = data_file

        # TODO: rethink use of global variables
        self.icons = load_icons()
        set_system()
        # TODO: check need to set_root

        self._config_style(style)
        self._config_frame()

        self._set_menubar()
        self._menubars = [self._menubar]

        self._create_form()

        if self.apps_schema is not None:
            self._connect_apps()

    @property
    def title(self):
        return f"{self.schema.get('title', '')} - {self.data_file}"

    @property
    def properties(self):
        # TODO: check if this is required
        return self.schema.get('properties', {})

    @property
    def data_file(self):
        return self._data_file

    @data_file.setter
    def data_file(self, value):
        self._data_file = value
        self._set_title()

    def _set_title(self):
        self.tksession.title(self.title)

    def _config_frame(self):
        self.tksession.columnconfigure(0, weight=1)
        self.tksession.rowconfigure(0, weight=1)

        self.frame = ttk.Frame(self.tksession, padding="3 3 12 12")
        self.frame.grid(column=0, row=0, sticky="news")

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", padx=2, pady=3, expand=True)

        self._set_title()

        self.notebook.bind('<<NotebookTabChanged>>', self._on_change_tab)

    def _on_change_tab(self, event):
        # TODO: add action on change tab
        index = self.notebook.index('current')
        self._menubars[index].activate()

    def add_child(self, form):
        self._form = form

    def add_app(self, name, app):
        self.apps[name] = app
        menubar = app.menubar or self._menubar
        self._menubars.append(menubar)

    def mainloop(self):
        self.tksession.mainloop()

    def _config_style(self, style):
        # TODO: from configuration file?
        style.configure("Highlighted.TMenubutton", background=PARAMS['hl_bg'])
        style.configure('Highlighted.TRadiobutton', background=PARAMS['hl_bg'])
        style.configure('Highlighted.TLabel', background=PARAMS['hl_bg'])
        style.configure('Highlighted.TEntry', fieldbackground=PARAMS['hl_bg'])
        style.configure('Linkable.TLabel', foreground="blue")
        style.configure('Status.TLabel', foreground='red')

        style.map('TCombobox', fieldbackground=[('readonly', '#FFFFFF')],
                  foreground=[('readonly', '#000000')],
                  selectforeground=[('readonly', '#000000')],
                  selectbackground=[('readonly', '#FFFFFF')])
        style.map('Highlighted.TCombobox', fieldbackground=[('readonly', PARAMS['hl_bg'])],
                  selectforeground=[('readonly', '#000000')],
                  selectbackground=[('readonly', PARAMS['hl_bg'])])

    def _create_form(self):
        # automatically added to children (OTTreeWidget)
        Form(self.schema, self)

    def _connect_apps(self):
        for obj_name, obj_schema in self.apps_schema.items():
            set_app = self.apps_factory.get(obj_schema.get('type'))
            app = set_app(self, obj_name, obj_schema)
            self.add_app(obj_name, app)

    def _set_menubar(self):
        self._menubar = DefaultMenubar(self)
        self._menubar.activate()

    def get_state(self):
        return self._form.get_state()

    def save_project(self, data_file=None):
        if data_file is None:
            data_file = self.data_file

        state = self.get_state()
        with open(data_file, 'w') as file:
            yaml.dump(state, file, default_flow_style=False)

    def load_project(self, data_file):
        state = self.load_state(data_file)
        self.set(state)

    def _load_data_file(self, data_file=None):
        if data_file is None:
            data_file = self.data_file

        with open(data_file, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        return data or {}

    def load_state(self, data_file=None):
        return self._form.load_state(data_file=data_file)

    def get(self):
        return self._form.get()

    def set(self, data):
        self._form.set(data)


class RootTabWidget(OTNodeWidget, metaclass=abc.ABCMeta):
    # TODO: make private?
    # TODO: is this abstraction really needed?

    def __init__(self, schema, parent, name):
        super().__init__(schema, parent, name)

    @property
    def root(self):
        # TODO: required?
        return self.parent


class Form(RootTabWidget):

    def __init__(self, schema, root, name='forms'):
        self.title = 'Forms'
        super().__init__(schema, root, name)
        # TODO: validate schema (in parent?)

        self._config_frame()

        # to handle dependents
        self._global_dependents = dict()
        self._xor_dependents = dict()
        self._xor_level = 0
        self._dependents = self._global_dependents

        self._dependent_names = set()

        self._initialize_tabs()

    @property
    def data_file(self):
        # TODO: is it required?
        return self.parent.data_file

    def prepare_to_receive_xor_dependents(self):
        self._xor_level += 1
        self._dependents = self._xor_dependents

    def assign_xor_dependents(self):
        self._xor_level -= 1

        if self._xor_level == 0:
            self.assign_dependents()
            self._dependents = self._global_dependents

    def add_dependency(self, master_name, slave):

        slaves_list = self._dependents.get(master_name, [])
        self._dependents[master_name] = slaves_list

        self._dependent_names.add(slave.name)

        slaves_list.append(slave)

    def assign_dependents(self):

        # find by name and add dependency
        for master_name, slaves in self._dependents.items():
            master = self.get_child_by_name(master_name)
            master.add_dependents(slaves)

        # reset dependents
        self._dependents.clear()

    @property
    def status(self):
        return self._get_status()

    @status.setter
    def status(self, status):
        if status == self._status:
            return

        self._status = status

    def _config_frame(self):
        self.frame = ttk.Frame(self.parent.frame)
        self.parent.notebook.add(self.frame, text=self.title)

        self.notebook = ttk.Notebook(self.frame, name="tab_nb")
        self.notebook.pack(fill="both", padx=2, pady=3, expand=True)

    def _initialize_tabs(self):

        for tab_name, tab_obj in self.properties.items():
            OTTabWidget(tab_obj, self, tab_name)  # goes to children when creating tab

        # TODO: check need for validation (should happen at beginning)
        # default_state = nob_complete(self.schema)
        # default_state = opentea_clean_data(default_state)

        self.assign_dependents()

        # set saved state
        state = self.load_state(data_file=self.data_file)
        self.set(state)

        # validate
        self.validate()

        # save file after import and validation
        self.parent.save_project()

    def load_state(self, data_file=None, data=None):
        if data is None:
            data = self.parent._load_data_file(data_file)

        return data

    def get_state(self):
        state = self.get()

        # TODO: can meta be removed? if yes remove _get_validated
        # meta = {"meta": {"validated": self._get_validated()}}
        # state.update(meta)

        return state

    def _get_validated(self):
        return {tab.name: tab.status for tab in self.children.values()}
