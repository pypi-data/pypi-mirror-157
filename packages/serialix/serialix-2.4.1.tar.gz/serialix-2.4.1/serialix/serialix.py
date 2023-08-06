from typing import Union, Type

from .core import BaseLang


class Serialix:
    """
    ``serialix`` unified instance generator for any officially supported language.

    This class should be used for creation of the basic ``serialix`` object for one of the officially supported languages. Currently supported languages: ``json``, ``yaml``, ``toml``

    :param file_format: Format of data serialization language to be used. Can be class of language parser with ``serialix`` implementation via ``.core.BaseLang`` inheritance or string  - ``json``, ``yaml`` (or ``yml``), ``toml`` (or ``tml``)
    :param file_path: Path to preferred local file destination.
        If the file does not exist at the specified path, it will be created
    :param default_dictionary: Default local file path ``str`` or ``dict``
        that will be used for local file start values, defaults to ``{}`` *(empty dict)*
    :param auto_file_creation: Automatic local file creation on object initialization, defaults to True
    :param force_overwrite_file: Whether the file needs to be overwritten if it already exists, defaults to False
    :param parser_write_kwargs: Pass custom arguments to parser's *write to local file* action, defaults to ``{}`` *(empty dict)*
    :param parser_read_kwargs: Pass custom arguments to parser's *read from local file* action, defaults to ``{}`` *(empty dict)*
    :param ignore_inheritance_check: Disable the "inherited from ``BaseLang``" check for passed to ``file_format`` argument class

    :return: Instance of ``.formats.*``, depending on the file format provided

    :raises ValueError: If provided data type in argument ``default_dictionary`` can't
        be represented as path ``str`` or ``dict``
    :raises ValueError: If provided data in argument ``file_format`` is not one of the supported languages

    .. versionadded:: 2.1.0
    """
    def __new__(
        self,
        file_format: Union[str, Type[BaseLang], object], file_path: str,
        default_dictionary: dict = {},
        auto_file_creation: bool = True, force_overwrite_file: bool = False,
        parser_write_kwargs: dict = {}, parser_read_kwargs: dict = {},
        ignore_inheritance_check=False
    ) -> Type[BaseLang]:
        if isinstance(file_format, str):
            file_format = file_format.lower()

            if file_format == 'json':
                from .formats.json import JSON_Format

                return JSON_Format(file_path=file_path, default_dictionary=default_dictionary, auto_file_creation=auto_file_creation, force_overwrite_file=force_overwrite_file, parser_write_kwargs=parser_write_kwargs, parser_read_kwargs=parser_read_kwargs)
            elif file_format in ('yaml', 'yml'):
                from .formats.yaml import YAML_Format

                return YAML_Format(file_path=file_path, default_dictionary=default_dictionary, auto_file_creation=auto_file_creation, force_overwrite_file=force_overwrite_file, parser_write_kwargs=parser_write_kwargs, parser_read_kwargs=parser_read_kwargs)
            elif file_format in ('toml', 'tml'):
                from .formats.toml import TOML_Format

                return TOML_Format(file_path=file_path, default_dictionary=default_dictionary, auto_file_creation=auto_file_creation, force_overwrite_file=force_overwrite_file, parser_write_kwargs=parser_write_kwargs, parser_read_kwargs=parser_read_kwargs)
            else:
                raise ValueError("'file_format' should be one of the supported languages name, not '{}'".format(file_format))

        elif isinstance(file_format, object):
            if issubclass(file_format, BaseLang) or ignore_inheritance_check:
                return file_format(file_path=file_path, default_dictionary=default_dictionary, auto_file_creation=auto_file_creation, force_overwrite_file=force_overwrite_file, parser_write_kwargs=parser_write_kwargs, parser_read_kwargs=parser_read_kwargs)
            else:
                raise ValueError("'file_format' class should be inherited from 'serialix.core.BaseLang'")

        else:
            raise ValueError("Wrong 'file_format' data type provided, should be 'class' or 'str'")
