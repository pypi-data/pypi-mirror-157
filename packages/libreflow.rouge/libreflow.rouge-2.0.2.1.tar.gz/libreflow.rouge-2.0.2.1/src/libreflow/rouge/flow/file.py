import pathlib

from libreflow.baseflow.file import (
    TrackedFile            as BaseTrackedFile,
    TrackedFolder          as BaseTrackedFolder,
    Revision               as BaseRevision,
    TrackedFolderRevision  as BaseTrackedFolderRevision,
    FileSystemMap          as BaseFileSystemMap
)
from libreflow.utils.flow import get_contextual_dict


class Revision(BaseRevision):
    pass


class TrackedFolderRevision(BaseTrackedFolderRevision):
    pass


class TrackedFile(BaseTrackedFile):
    pass


class TrackedFolder(BaseTrackedFolder):
    pass


class FileSystemMap(BaseFileSystemMap):
    
    def add_file(self, name, extension, display_name=None, base_name=None, tracked=False, default_path_format=None):
        if default_path_format is None:
            default_path_format = get_contextual_dict(self, 'settings').get(
                'path_format', None
            )
        return super(FileSystemMap, self).add_file(name, extension, display_name, base_name, tracked, default_path_format)

    def add_folder(self, name, display_name=None, base_name=None, tracked=False, default_path_format=None):
        if default_path_format is None:
            default_path_format = get_contextual_dict(self, 'settings').get(
                'path_format', None
            )
        return super(FileSystemMap, self).add_folder(name, display_name, base_name, tracked, default_path_format)
