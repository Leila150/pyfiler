"""Custom exception hierarchy for pyfiler."""

class PyFilerError(Exception):
    """Base class for every pyfiler-specific exception."""

class PathError(PyFilerError): pass
class InvalidPathError(PathError, ValueError): pass
class EmptyPathError(InvalidPathError): pass
class PathOutsideRootError(PathError, PermissionError): pass
class PathNotFoundError(PathError, FileNotFoundError): pass

class FileOperationError(PyFilerError): pass
class PyFilerFileNotFoundError(FileOperationError, FileNotFoundError): pass
class PyFilerFileExistsError(FileOperationError, FileExistsError): pass
class NotAFileError(FileOperationError, IsADirectoryError): pass
class FileReadError(FileOperationError): pass
class FileWriteError(FileOperationError): pass
class FileAppendError(FileOperationError): pass
class FileDeleteError(FileOperationError): pass
class FileCopyError(FileOperationError): pass
class FileMoveError(FileOperationError): pass
class FileRenameError(FileOperationError): pass

class FolderOperationError(PyFilerError): pass
class FolderNotFoundError(FolderOperationError, FileNotFoundError): pass
class FolderExistsError(FolderOperationError, FileExistsError): pass
class NotAFolderError(FolderOperationError, NotADirectoryError): pass
class FolderNotEmptyError(FolderOperationError, OSError): pass
class FolderCreateError(FolderOperationError): pass
class FolderDeleteError(FolderOperationError): pass
class FolderCopyError(FolderOperationError): pass
class FolderMoveError(FolderOperationError): pass
class FolderRenameError(FolderOperationError): pass

class ContentError(PyFilerError): pass
class ContentTypeError(ContentError, TypeError): pass
class LineError(ContentError, ValueError): pass
class InvalidLineError(LineError): pass
class LineOutOfRangeError(LineError, IndexError): pass
class InvalidLineListError(LineError): pass

class SearchError(PyFilerError): pass
class InvalidPatternError(SearchError, ValueError): pass
class InvalidExtensionError(SearchError, ValueError): pass

class StorageError(PyFilerError): pass
class StoragePermissionError(StorageError, PermissionError): pass
class StorageUnavailableError(StorageError, OSError): pass
class StorageSetupError(StorageError): pass
class PlatformNotSupportedError(StorageError, NotImplementedError): pass
class AndroidStorageError(StorageError): pass
class AndroidPermissionError(StoragePermissionError): pass
class IOSStorageError(StorageError): pass
class IOSPermissionError(StoragePermissionError): pass

class SecurityError(PyFilerError): pass
class RootAccessDeniedError(SecurityError, PermissionError): pass

class OperationError(PyFilerError): pass
class InvalidOperationError(OperationError, ValueError): pass
class OperationConflictError(OperationError): pass
class DestinationExistsError(OperationConflictError, FileExistsError): pass
class SourceEqualsDestinationError(OperationConflictError, ValueError): pass
class RecursiveOperationError(OperationError): pass

class ConfigurationError(PyFilerError): pass
class InvalidRootError(ConfigurationError, ValueError): pass
class RootNotFoundError(ConfigurationError, FileNotFoundError): pass
class InvalidEncodingError(ConfigurationError, ValueError): pass

class MetadataError(PyFilerError): pass
class MetadataUnavailableError(MetadataError): pass
class HashingError(PyFilerError): pass
class UnsupportedHashAlgorithmError(HashingError, ValueError): pass
class ComparisonError(PyFilerError): pass
class TreeError(PyFilerError): pass
class TreeDepthError(TreeError, ValueError): pass
