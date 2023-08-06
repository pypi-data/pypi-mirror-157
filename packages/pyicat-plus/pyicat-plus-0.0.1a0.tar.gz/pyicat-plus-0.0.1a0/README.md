# PyIcat-Plus

A python client for ICAT+.

## Test

With threads

```bash
python -m pip install -e .[test]
pytest
```

With gevent

```bash
python -m pip install -e .[test]
python -m pip install gevent
python -m gevent.monkey --module pytest
```

## Documentation

https://pyicat-plus.readthedocs.io/
