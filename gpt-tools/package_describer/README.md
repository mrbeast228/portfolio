# Package describer
This tool creates XLSX table with descriptions of Maven, Yarn, Node.JS, Golang, PyPI and Nuget packages

## Requirments
+ pandas
+ wheel_inspect

## Usage
At first you need to configure script via it global variables
+ `openai.api_key` - your OpenAI token, which you can create on https://platform.openai.com/account/api-keys. Please remember it's not free
+ `cache_dir_path` - path to Maven, Yarn, etc. cache directory which contains many packages. Of course you can _git clone_ some packages by yourself and place them in some directory - it'll work too
+ `path_to_append` - path to be automatically appended to relative path of package. For example you may have `/home/Builder.John.2023/sources/` appended
+ `pkgType` - type of packages you want to describe. Must be one of `maven`, `yarn`, `npm`, `yarn6`, `go`, `nuget`, `pip` (global classes)

After it you can run:
```
python3 package_describer.py
```
Script requesting OpenAI API in 384 threads for more speed (it doesn't take CPU resources). Result will be placed in _pkgType_.xlsx file. It'll contain **Relative path**, **Package**, **Version**, **Legacy description** and **Description** columns
