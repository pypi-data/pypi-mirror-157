from kabaret import flow
from libreflow.baseflow.task import ManagedTask


class Task(ManagedTask):
    
    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        return f'{split[3]} · {split[5]} · {split[7]}'
