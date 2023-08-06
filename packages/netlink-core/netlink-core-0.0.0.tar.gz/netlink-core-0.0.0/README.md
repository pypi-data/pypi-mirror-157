# netlink-core

Core components of NetLink tools

This provides a small set of functionality share by my collection of tools:

- [netlink-crypt](https://pypi.org/project/netlink-crypt/)
- [netlink-logging](https://pypi.org/project/netlink-logging/)
- [netlink-sap-rfc](https://pypi.org/project/netlink-sap-rfc/)
- [netlink-sharepoint](https://pypi.org/project/netlink-sharepoint/)


## Contents

- Centralized configuration using [TOML](https://toml.io/en/) 
in the users home directory (subdirectory `.netlink`).

### Classes

- `netlink.core.AttributeMapping` behaves like an immutable mapping, adding access to all items via property notation:
    
      a['b'] == a.b

  This is propagated through all levels:

      a['b']['c']['d'] == a.b.c.d

### Scripts

- `create_netlink_defaults` creates a TOML file containing all currently internal defaults in the users home directory (subdirectory `.netlink`). If the file already exist, the current file is copied as a backup with extension `.001`.


## Installation

Use your preferred tool to install from [PyPI](https://pypi.org/). I prefer [Poetry](https://python-poetry.org/).

[//]: # (## Roadmap)

[//]: # (## Contributing)

## License

MIT
