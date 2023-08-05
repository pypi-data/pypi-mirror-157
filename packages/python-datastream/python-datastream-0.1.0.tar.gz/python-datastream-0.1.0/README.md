
# datastream

Read and write binary files by integer, floats, strings with fixed size.

## Installing

```shell
pip install python-datastream
```

## Usage

Reading:
```python
from datastream import DataInputStream

with open("test.bin", "rb") as f:
    ds = DataInputStream(f)
    print(ds.read_int())
    print(ds.read_strz())
```

Writing:
```python
from datastream import DataOutputStream

with open("test.bin", "wb") as f:
    ds = DataOutputStream(f)
    ds.write_int(42)
    ds.write_strz("Hello world")
```

## License

MIT License. See LICENSE file.
