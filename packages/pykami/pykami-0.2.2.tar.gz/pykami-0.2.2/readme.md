# Pykami

A python module that parses kami into HTML.

## Usage

Simply run `pykami.parse()`, which takes a string containing a KAMI input and outputs a string containing the corresponding HTML output.

```python
import pykami
print(pykami.parse("*bold text*")) // <b >bold text</b>
```

For the kami specification, read the [kami-parser readme](https://github.com/lilith-in-starlight/kami-parser/).
