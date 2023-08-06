import collections.abc
import pathlib
import toml

from .attribute_mapping import AttributeMapping

KILOBYTE = 1024
MEGABYTE = 1024 * KILOBYTE

HARDCODED = {
    "logging": {
        "level": 20,
        "message_format": "%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "file_format": "[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s",
        "file_size": 100 * MEGABYTE,
        "file_generations": 5,
    },
}

CONFIG_PATH = pathlib.Path.home() / ".netlink"

MANDATORY = tuple(['logging', ])

_default = HARDCODED.copy()
if (CONFIG_PATH / "default.toml").exists():
    with (CONFIG_PATH / "default.toml").open("r", encoding="utf-8-sig") as f:
        _default.update(toml.load(f))
_cache = {'default': AttributeMapping(_default)}


def get_config(section: str = None) -> AttributeMapping:
    section = 'default' if not section else section
    if section not in _cache:
        data = {k: v for k, v in _default.get(section, {}).items()}
        for i in MANDATORY:
            if i not in data:
                data[i] = {k: v for k, v in _default[i].items()}
        if CONFIG_PATH.exists():
            section_path = CONFIG_PATH / f"{section}.toml"
            if section_path.exists():
                with section_path.open("r") as f:
                    data.update(toml.load(f))
        _cache[section] = AttributeMapping(data)
    return _cache[section]
