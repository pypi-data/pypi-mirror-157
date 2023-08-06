from __future__ import annotations

from pathlib import Path

from brane.core.base import Context
from brane.core.event import Event
from brane.core.factory import Factory
from brane.core.format import NoneFormat
from brane.core.hook import FunctionHook, Hook
from brane.core.mapper import ExtensionMapper, ObjectFormat2Module
from brane.core.utils import get_extension_from_filname_default, integrate_args, integrate_kwargs
from brane.libs.hooks import check_path_existence, create_parent_directory  # noqa E402
from brane.typing import *  # noqa: F403


class HookManager(object):
    """"""

    pre_read = Event(event_name="pre_read")
    post_read = Event(event_name="post_read")
    pre_write = Event(event_name="pre_write")
    post_write = Event(event_name="post_write")

    pre_readall = Event(event_name="pre_readall")
    post_readall = Event(event_name="post_readall")
    pre_writeall = Event(event_name="pre_writeall")
    post_writeall = Event(event_name="post_writeall")

    #  This is a temporal class.
    # [ARGS]:
    # * moved to hook.py ?
    # * consider better class name if exists
    # * refactor this class

    # @property [TODO]: use when python>=3.9
    @classmethod
    def get_events(cls) -> dict[str, Event]:
        name2event: dict[str, Event] = dict()
        for event in dir(cls):
            if isinstance(event, Event):
                name2event.update({event.event_name: event})
        return name2event

    @classmethod
    def get_hook_class(cls, hook, **hook_kwargs):
        if isinstance(hook, Hook):
            return hook
        else:  ### detail check ?
            return FunctionHook(hook, **hook_kwargs)

    @classmethod
    def connect_hook_and_event(cls, event, hook, **hook_kwargs):
        hook = cls.get_hook_class(hook, **hook_kwargs)
        event.add_hooks(hook)

    @classmethod
    def register_pre_read_hook(cls, hook, **hook_kwargs):
        cls.connect_hook_and_event(cls.pre_read, hook, **hook_kwargs)

    @classmethod
    def register_post_read_hook(cls, hook, **hook_kwargs):
        cls.connect_hook_and_event(cls.post_read, hook, **hook_kwargs)

    @classmethod
    def register_pre_write_hook(cls, hook, **hook_kwargs):
        cls.connect_hook_and_event(cls.pre_write, hook, **hook_kwargs)

    @classmethod
    def register_post_write_hook(cls, hook, **hook_kwargs):
        cls.connect_hook_and_event(cls.post_write, hook, **hook_kwargs)

    @classmethod
    def register_pre_readall_hook(cls, hook, **hook_kwargs):
        cls.connect_hook_and_event(cls.pre_readall, hook, **hook_kwargs)

    @classmethod
    def register_pre_writeall_hook(cls, hook, **hook_kwargs):
        cls.connect_hook_and_event(cls.pre_writeall, hook, **hook_kwargs)

    @classmethod
    def register_post_readall_hook(cls, hook, **hook_kwargs):
        cls.connect_hook_and_event(cls.post_readall, hook, **hook_kwargs)

    @classmethod
    def register_post_writeall_hook(cls, hook, **hook_kwargs):
        cls.connect_hook_and_event(cls.post_writeall, hook, **hook_kwargs)

    @classmethod
    def clear_hooks(cls, event):
        event.clear_hooks()

    @classmethod
    def clear_pre_read_hook(cls):
        cls.clear_hooks(cls.pre_read)

    @classmethod
    def clear_post_read_hook(cls):
        cls.clear_hooks(cls.post_read)

    @classmethod
    def clear_pre_write_hook(cls):
        cls.clear_hooks(cls.pre_write)

    @classmethod
    def clear_post_write_hook(cls):
        cls.clear_hooks(cls.post_write)

    @classmethod
    def clear_pre_readall_hook(cls):
        cls.clear_hooks(cls.pre_readall)

    @classmethod
    def clear_pre_writeall_hook(cls):
        cls.clear_hooks(cls.pre_writeall)

    @classmethod
    def clear_post_readall_hook(cls):
        cls.clear_hooks(cls.post_readall)

    @classmethod
    def clear_post_writeall_hook(cls):
        cls.clear_hooks(cls.post_writeall)

    @classmethod
    def clear_all_hooks(cls):
        for event in cls.get_events():
            cls.clear_hooks(event)

    @classmethod
    def setup_hooks(cls):  # temporal name
        cls.register_pre_read_hook(check_path_existence)  # read_pre.add_hooks(FunctionHook(check_path_existence))
        cls.register_pre_write_hook(
            create_parent_directory
        )  # write_pre.add_hooks(FunctionHook(create_parent_directory))


class IOLogger(object):
    # for debug at this stage
    log = []


class ExtendedIO(HookManager):
    """"""

    # [ARGS]
    # * refactor for better implementation
    # * use mixin ?
    factory = Factory()

    get_extension_from_filename = get_extension_from_filname_default
    logger = IOLogger()

    @classmethod
    def read(
        cls,
        path: Optional[PathType] = None,
        file: Optional[FileType] = None,
        ext: str = "",
        module_name: str = "",
        read_args: Optional[tuple] = None,
        read_kwargs: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Args:
            path: File path to read. Currently, only local file system path is available.
            file: File object such as byte stream to read.
            ext: The extension name. Used only when the extension is not given in the path.
            module_name: The module name. Specified only in the case the module is fixed.

        Returns:
            loaded object.

        Note:
            The priority order is module_name > ext > path

        """
        if read_args is None:
            read_args = tuple()
        if read_kwargs is None:
            read_kwargs = dict()

        # ?path xor ?file
        if path is None and file is None:
            raise AssertionError()
        if path is not None and file is not None:
            raise AssertionError()
        if file is not None and ext == "":
            raise AssertionError()

        if module_name:
            if module_name in cls.factory.className2Module:
                Mdl = cls.factory.className2Module[module_name]
                assert Mdl  # temporal (currently, there is possibility that NoneModule comes in)
            else:
                raise NameError(f"No module name: {module_name}. Check the `all_modules` propetry.")  ###
        else:
            ext = ext if ext else cls.get_extension_from_filename(path)
            Mdl = ExtensionMapper.get_module_class_from_extension(ext)
            if not Mdl:
                raise NotImplementedError(f"Cannot find the corresponding module for given extension {ext}")
        Mdl.load_modules()

        context: ContextInterface = Context(
            {"path": path, "file": file, "ext": ext, "Module": Mdl}
        )  # add Fmt as supplementary ?
        context = cls.pre_read.fire(context)
        base_args = context.get("args", ())
        base_kwargs = context.get("kwargs", {})
        base_args = integrate_args(base_args, read_args)
        base_kwargs = integrate_kwargs(base_kwargs, read_kwargs)
        base_args = integrate_args(base_args, args)
        base_kwargs = integrate_kwargs(base_kwargs, kwargs)

        path = context["path"]
        file = context["file"]
        cls.logger.log.append(
            ("read", {"path": path, "file": file, "ext": ext, "module": Mdl.name, "args": args, "kwargs": kwargs})
        )  ### temporal
        obj = Mdl.read(path=path, file=file, *base_args, **base_kwargs)

        context.update({"object": obj})
        context = cls.post_read.fire(context)
        obj = context["object"]
        return obj

    @classmethod
    def read_all_as_list(
        cls,
        multiple_paths: Union[str, list[PathType]],
        read_args: Optional[tuple] = None,
        read_kwargs: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> list[Any]:
        """
        Args:
            multiple_paths: Several file paths to read once. The glob format is also allowed.
                Currently, only local file system paths are available.
            read_args:
            read_kwargs:

        Returns:
            loaded objects as list. The ordering is same as given paths.
            If the specified path is in the glob format, paths will be sorted.
        """
        if read_args is None:
            read_args = tuple()
        if read_kwargs is None:
            read_kwargs = dict()
        # flles not supported yet
        paths: list = []
        if isinstance(multiple_paths, str):
            import glob

            paths = glob.glob(multiple_paths, recursive=True)
            paths.sort()
        elif isinstance(multiple_paths, list):  # [TODO]: include tuple ?
            assert all(map(lambda path: isinstance(path, str), multiple_paths))
            paths = multiple_paths
        else:
            raise NotImplementedError
        if len(paths) == 0:
            return {}

        context: ContextInterface = Context({"paths": paths})
        context = cls.pre_readall.fire(context)
        objs = []
        for path in paths:
            obj = cls.read(path=path, read_args=read_args, read_kwargs=read_kwargs)
            objs.append(obj)
        context.update({"objects": objs})

        # experimental
        if "sort_func" in kwargs:
            sort_func = kwargs["sort_func"]
            context = sort_func(context)

        context = cls.post_readall.fire(context)
        if "object" in context:
            return context["object"]
        else:
            return context["objects"]

    @classmethod
    def read_all_as_dict(
        cls,
        multiple_paths: dict[str, PathType],
        read_args: Optional[tuple] = None,
        read_kwargs: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> dict[str, Any]:
        if read_args is None:
            read_args = tuple()
        if read_kwargs is None:
            read_kwargs = dict()

        # flles not supported yet
        paths: dict[str, PathType] = {}
        if isinstance(multiple_paths, str):
            import glob

            paths = {path: path for path in glob.glob(multiple_paths, recursive=True)}
        elif isinstance(multiple_paths, list):
            assert all(map(lambda path: isinstance(path, str), multiple_paths))
            paths = {path: path for path in multiple_paths}
        elif isinstance(multiple_paths, dict):
            assert all(map(lambda path: isinstance(path, str), multiple_paths.values()))
            paths = multiple_paths
        else:
            raise NotImplementedError
        if len(paths) == 0:
            return {}

        context: ContextInterface = Context({"paths": paths})
        context = cls.pre_readall.fire(context)
        objs = {}
        for key, path in paths.items():
            obj = cls.read(
                path=path, read_args=read_args, read_kwargs=read_kwargs
            )  # [ARG]: parameter 'file' (stream or path ?)
            objs.update({key: obj})
        context.update({"objects": objs})

        # experimental
        if "sort_func" in kwargs:
            sort_func = kwargs["sort_func"]
            context = sort_func(context)

        context = cls.post_readall.fire(context)
        if "object" in context:
            return context["object"]
        else:
            return context["objects"]

    @classmethod
    def write(
        cls,
        obj: Any,
        path: PathType = Optional[None],
        file: Optional[FileType] = None,
        ext: str = "",
        module_name: str = "",
        write_args: Optional[tuple] = None,
        write_kwargs: Optional[dict] = None,
        *args,
        **kwargs,
    ):
        """
        Args:
            obj: Any object to save.
            path: File path to write. Currently, only local file system path is available.
            file: File object such as byte stream to write.
            ext: The extension name. Used only when the extension is not given in the path.
            module_name: The module name. Specified only in the case the module is fixed.
        """
        if write_args is None:
            write_args = tuple()
        if write_kwargs is None:
            write_kwargs = dict()

        # ?path xor ?file
        if path is None and file is None:
            raise AssertionError()
        if path is not None and file is not None:
            raise AssertionError()
        if file is not None and ext == "":
            raise AssertionError()

        if module_name:
            if module_name in cls.factory.className2Module:
                Mdl = cls.factory.className2Module[module_name]
                assert Mdl  # temporal (currently, there is possibility that NoneModule comes in)
            else:
                raise NameError(f"No module name: {module_name}. Check the `all_modules` propetry.")  ### temporal
        else:
            if ext:
                ext_from_path = cls.get_extension_from_filename(path)
                if ext != ext_from_path:
                    path = Path(path).with_suffix(ext)
                Fmt = ExtensionMapper.get_format_class_from_extension(ext)
            else:
                ext_from_path = cls.get_extension_from_filename(path)
                if ext_from_path:
                    Fmt = ExtensionMapper.get_format_class_from_extension(ext_from_path)
                else:
                    Fmt = NoneFormat
            Mdl = ObjectFormat2Module.get_module_from_object(obj, fmt=Fmt)
            if not Mdl:
                raise NotImplementedError(f"Cannot find the corresponding module for given object type {type(obj)}")
        Mdl.load_modules()

        context: ContextInterface = Context({"path": path, "file": file, "object": obj, "Module": Mdl})
        context = cls.pre_write.fire(context)
        base_args = context.get("args", ())
        base_kwargs = context.get("kwargs", {})
        base_args = integrate_args(base_args, write_args)
        base_kwargs = integrate_kwargs(base_kwargs, write_kwargs)
        base_args = integrate_args(base_args, args)
        base_kwargs = integrate_kwargs(base_kwargs, kwargs)

        path = context["path"]
        file = context["file"]
        cls.logger.log.append(
            ("write", {"path": path, "file": file, "ext": ext, "module": Mdl.name, "args": args, "kwargs": kwargs})
        )  ### temporal
        Mdl.write(obj=obj, file=file, path=path, *base_args, **base_kwargs)
        context = cls.post_write.fire(context)

    @classmethod
    def write_all_from_list(
        cls,
        obj_list: list[Any],
        output_dir: Optional[PathType] = None,
        path_ruler: Optional[Callable[int, str]] = None,
        write_args: Optional[tuple] = None,
        write_kwargs: Optional[dict] = None,
        *args,
        **kwargs,
    ):
        if write_args is None:
            write_args = tuple()
        if write_kwargs is None:
            write_kwargs = dict()
        # flles notg supported yet
        # [ARG]: list case is the special case of dict, to say, the index can be seen as the key -> unify two ??
        # [TODO]: should allow the iterator...
        # path assignemtn option
        # 1. output_dir + str(idx)
        # 2. path_ruler(obj_list)
        # 3. output_dir + path_ruler(obj_list)
        if not isinstance(obj_list, list):  # [NOTE]: This is used for dynamical check
            raise ValueError(
                f"obj_list should be python `list` but the actual type is {type(obj_list)}"
            )  # [TODO]: implement some function for value check

        paths: list[PathType] = []
        if output_dir is not None:
            if path_ruler is None:
                path_ruler = lambda idx: str(idx)  # noqa: E731
            paths = [Path(output_dir) / path_ruler(idx) for idx in range(len(obj_list))]
        elif path_ruler is not None:
            paths = [path_ruler(idx) for idx in range(len(obj_list))]
        else:
            raise ValueError("Either output_dir or path_ruler should not be None")

        context: ContextInterface = Context({"paths": paths, "objects": obj_list})
        context = cls.pre_writeall.fire(context)
        for idx, obj in enumerate(obj_list):
            path = paths[idx]
            cls.write(obj=obj, path=path, *write_args, **write_kwargs)

        context = cls.post_writeall.fire(context)

    @classmethod
    def write_all_from_dict(
        cls,
        obj_dict: dict[str, Any],
        output_dir: Optional[PathType] = None,
        path_ruler: Optional[Callable[str, str]] = None,
        write_args: Optional[tuple] = None,
        write_kwargs: Optional[dict] = None,
        *args,
        **kwargs,
    ):
        if write_args is None:
            write_args = tuple()
        if write_kwargs is None:
            write_kwargs = dict()
        # flles notg supported yet
        # path assignemtn option
        # 1. output_dir + key
        # 2. path_ruler(obj_dict)
        # 3. output_dir + path_ruler(obj_dict)
        if not isinstance(obj_dict, dict):  # [NOTE]: This is used for dynamical check
            raise ValueError(f"obj_dict should be python `dict` but the actual type is {type(obj_dict)}")

        paths: dict[str, PathType] = {}
        if output_dir is not None:
            if path_ruler is None:
                path_ruler = lambda key: key  # noqa: E731
            paths = {key: Path(output_dir) / path_ruler(key) for key in obj_dict.keys()}
        elif path_ruler is not None:
            paths = {key: path_ruler(key) for key in obj_dict.keys()}
        else:
            raise ValueError("Either output_dir or path_ruler should not be None")

        context: ContextInterface = Context({"paths": paths, "objects": obj_dict})
        context = cls.pre_writeall.fire(context)
        for key, obj in obj_dict.items():
            path = paths[key]
            cls.write(obj=obj, path=path, *write_args, **write_kwargs)

        context = cls.post_writeall.fire(context)

    @classmethod
    def reload(cls, config_path: Optional[PathType] = None):
        cls.factory.activate(config_path=config_path)

    @classmethod
    def all_modules(cls):
        return list(cls.factory.className2Module.keys())

    @classmethod
    def all_formats(cls):
        return list(cls.factory.className2Format.keys())

    @classmethod
    def all_objects(cls):
        return list(cls.factory.className2Object.keys())
