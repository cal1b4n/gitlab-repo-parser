# Gitlab group and repository parser

## Description

This script parses any Gitlab group and repository and searches for specified keyword in every single file except for excluded file formats which are already predefined.

Predefined excluded file formats are:

* .exe
* .dll
* .jpg
* .jpeg
* .png
* .svg
* .gif
* .ico

### Requirements

* Python 3.6+
* Requests

```bash
pip3 install requests
```

### Examples

```bash
python3 gitlab_parser.py -g *group_id* -p *project_id* -k *keyword* 
```

## TODO

* Polish the script
* ~~Add command line arguments for the script~~
