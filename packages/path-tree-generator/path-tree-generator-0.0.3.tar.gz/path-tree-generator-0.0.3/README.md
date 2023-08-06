# path-tree-generator

Generate tree-like directory listings also for humans, output them as `str`, `list[str]`, `dict` or `json`.

    from path_tree_generator import PathTree
    pt = PathTree('/my/path/to/generate')
    print(
        pt.get_human_readable()
    )

----------------------------------------------------------------------------------------------------

**ATTENTION: NOT FULLY IMPLEMENTED YET :construction:**

:warning: CURRENTLY THIS PACKAGE IS UNDER HEAVY DEVELOPMENT AND NOT FULLY IMPLEMENTED YET! :warning:

The fist working (early) version is released as **path-tree-generator v0.0.2** 
and contains the most base implementations.

[More to come for **path-tree-generator v0.1.0**:][issue-tracker]
- Adding a "better" getter methods naming
- ...

But keep in mind that classes, methods and their signatures 
might change anytime during development till the first official release 1.0.0.

----------------------------------------------------------------------------------------------------

## Table of Contents

- [Requirements](#requirements)
- [Usage](#usage)
  - [Installation](#installation)
  - [Example](#example)
- [Support](#support)
- [Contributing](#contributing)
- [License](#license)
- [Known Issues](#known-issues)

## Requirements

[Python 3.10][python]+

`path-tree-generator` depends on the following packages:

- [Pydantic][pydantic] for data models and validation

## Usage

### Installation

    pip install path-tree-generator

### Example

    from path_tree_generator import PathTree
    pt = PathTree('/my/path/to/generate')
    print(
        pt.get_human_readable()
    )

The code above outputs a tree-like formatted recursive directory listing.
Directories are wrapped in square brackets, files aren't.

    [data]
    ├── data.json
    ├── data.tree
    ├── [myDirectory-1]
    │   ├── myFile.txt
    │   └── [subdirectory]
    │       └── green.gif
    └── [myDirectory-2]
        ├── [subdirectory1]
        │   └── green.gif
        └── [subdirectory2]
            ├── myFile.txt
            └── myFile2.txt

## Support

If you're opening [issues][issue-tracker], please mention the version that the issue relates to. 

## Contributing

To contribute to this project, fork the repository, make your changes and create a pull request.

## License

This project is licensed under the terms of the MIT license.

## Known Issues

- Python version compatibility < v3.10 is not tested yet
- Getter methods aren't named perfectly, this will be solved in a future version
- Not all tests are fully implemented yet



[issue-tracker]: https://github.com/dl6nm/path-tree-generator/issues
[pydantic]: https://pydantic-docs.helpmanual.io/
[python]: https://www.python.org/
