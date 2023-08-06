
import abc

from opentea.gui_forms._exceptions import GetException


class OTTreeElement(metaclass=abc.ABCMeta):

    def __init__(self, schema, parent, name):
        self.schema = schema
        self.parent = parent
        self.name = name
        self.children = dict()
        self._otroot = None

        self.parent.add_child(self)

        self._status = None

        self.slaves = []
        self.master = None
        self.dependent = self._handle_dependency()

    @property
    def otroot(self):
        if self._otroot is None:
            obj = self.parent
            while hasattr(obj, 'parent'):
                obj = obj.parent

            self._otroot = obj

        return self._otroot

    @property
    def status(self):
        return self._get_status()

    @status.setter
    def status(self, status):
        return self._set_status(status)

    def _get_status(self):
        return self._status

    def _set_status(self, status):
        self._update_parent_status(status)

        self._status = status
        self.on_update_status()

    def _update_parent_status(self, status):
        if status == -1:
            self.parent._status_invalid += 1
        elif status == 0:
            self.parent._status_temp += 1

        if self._status == -1:
            self.parent._status_invalid -= 1
        elif self._status == 0:
            self.parent._status_temp -= 1

        self.parent.status = self.parent.status

    @property
    def properties(self):
        return self.schema.get("properties", [])

    @property
    def _type(self):
        return self.schema['type']

    def add_child(self, child):
        self.children[child.name] = child

    def on_update_status(self):
        """Additional operations to perform when updating status.
        """
        pass

    @abc.abstractmethod
    def validate(self):
        pass

    @abc.abstractmethod
    def get(self):
        pass

    @abc.abstractmethod
    def set(self, value):
        pass

    def _handle_dependency(self):
        # let form handle assignment of dependents
        if 'ot_require' not in self.schema:
            return False

        master_name = self.schema.get('ot_require')
        self.get_form().add_dependency(master_name, self)

        return True

    def _add_dependent(self, slave, data=None):
        self.slaves.append(slave)
        slave.master = self

        if data is not None:
            slave.set(data)

    def add_dependents(self, slaves):
        try:
            data = self.get()
        except GetException:
            data = None

        for slave in slaves:
            self._add_dependent(slave, data)

    def validate_slaves(self):
        for slave in self.slaves:
            slave.validate()

    def set_slaves(self, value):
        for slave in self.slaves:
            slave.set(value)

    def _reset_master(self):
        if self.master is None:
            return

        self.master.slaves.remove(self)
        self.master = None

    def get_form(self):
        form = self
        while not hasattr(form, 'root'):
            form = form.parent

        return form

    def get_child_by_name(self, name):

        # check if child is at this level
        for child in self.children.values():
            if child.name == name:
                return child

        # check children
        for child in self.children.values():
            child_ = child.get_child_by_name(name)

            if child_ is not None:
                return child_

        return None
