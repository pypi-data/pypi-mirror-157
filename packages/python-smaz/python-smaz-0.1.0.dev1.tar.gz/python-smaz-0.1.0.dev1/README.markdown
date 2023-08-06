<h1 align="center"><i>✨ Pysmaz ✨ </i></h1>

<h3 align="center">The python binding for <a href="https://github.com/antirez/smaz">smaz</a> </h3>

[![pypi](https://img.shields.io/pypi/v/pysmaz.svg)](https://pypi.org/project/pysmaz/)
![python](https://img.shields.io/pypi/pyversions/pysmaz)
![implementation](https://img.shields.io/pypi/implementation/pysmaz)
![wheel](https://img.shields.io/pypi/wheel/pysmaz)
![license](https://img.shields.io/github/license/synodriver/pysmaz.svg)
![action](https://img.shields.io/github/workflow/status/synodriver/pysmaz/build%20wheel)

# usage
```python
def compress(data: bytes, output_size: int = ...) -> bytes: ...
def decompress(data: bytes, output_size: int = ...) -> bytes: ...
def compress_into(data: bytes, output: bytearray) -> int: ...
def decompress_into(data: bytes, output: bytearray) -> int: ...
```