from kabaret import flow
from libreflow.baseflow.shot import (
    ShotCollection,
    Shot as BaseShot,
    Sequence as BaseSequence
)
from libreflow.baseflow.task import ManagedTaskCollection


class Shot(BaseShot):
    
    tasks = flow.Child(ManagedTaskCollection).ui(
        expanded=True
    )

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        return f'{split[3]} · {split[5]}'

    def ensure_tasks(self):
        """
        Creates the tasks of this shot based on the task
        templates of the project, skipping any existing task.
        """
        mgr = self.root().project().get_task_manager()

        for dt in mgr.default_tasks.mapped_items():
            if not self.tasks.has_mapped_name(dt.name()) and not dt.optional.get():
                t = self.tasks.add(dt.name())
                t.enabled.set(dt.enabled.get())
        
        self.tasks.touch()

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            sequence, shot = self.name().rsplit('_', maxsplit=1)
            return dict(sequence=sequence, shot=shot)


class Shots(ShotCollection):

    def add(self, name, object_type=None):
        """
        Adds a shot to the global shot collection, and creates
        its tasks.
        """
        s = super(Shots, self).add(name, object_type)
        s.ensure_tasks()

        return s
