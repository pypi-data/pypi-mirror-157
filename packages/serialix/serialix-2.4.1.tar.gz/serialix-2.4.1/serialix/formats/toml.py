""" ``TOML`` language support """
from ..core import BaseLang

import toml


class TOML_Format(BaseLang):
    """TOML data serialization format implementation

    :param file_path: Path to preferred local file destination.
        If the file does not exist at the specified path, it will be created
    :param default_dictionary: Default local file path ``str`` or ``dict``
        that will be used for local file start values, defaults to ``{}`` *(empty dict)*
    :param auto_file_creation: Automatic local file creation on object initialization, defaults to True
    :param force_overwrite_file: Whether the file needs to be overwritten if it already exists, defaults to False
    :param parser_write_kwargs: Pass custom arguments to parser's *write to local file* action, defaults to ``{}`` *(empty dict)*
    :param parser_read_kwargs: Pass custom arguments to parser's *read from local file* action, defaults to ``{}`` *(empty dict)*
    :raises ValueError: If provided data type in argument ``default_dictionary`` can't
        be represented as path ``str`` or ``dict``

    .. note::
        Methods ``.clear()``, ``.fromkeys()``, ``.get()``, ``.items()``, ``.keys()``, ``values()``,
        ``pop()``, ``popitem()``, ``setdefault()``, ``update()`` are bound to the attribute ``dictionary``,
        so executing:

        >>> this_object.update({'check': True})

        Is equal to:

        >>> this_object.dictionary.update({'check': True})
    """
    def _core__read_file_to_dict(self, file_path: str) -> dict:
        """Method for reading custom local files from path ``str`` as dictionary

        :param file_path: Path to local file in ``toml`` format

        :return: Parsed local file dictionary
        """
        with open(file_path, 'rt') as f:
            config_dict = toml.load(f, **self.parser_read_kwargs)

        return config_dict

    def _core__write_dict_to_file(self, file_path: str, dictionary: dict):
        """Method to write dictionaries into custom local path ``str``

        :param file_path: Path to local file in ``toml`` format
        :param dictionary: Dictionary which will be written in ``file_path``
        """
        with open(file_path, 'wt') as f:
            toml.dump(dictionary, f, **self.parser_write_kwargs)
