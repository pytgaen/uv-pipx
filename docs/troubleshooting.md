# Solve Apps problems

## gita

Install

```bash
uvpipx install gita 
```

But try to run and you get

```bash
gita

Traceback (most recent call last):
  File "/home/xxxxx/.local/bin/gita", line 5, in <module>
    from gita.__main__ import main
  File "/home/xxxxx/.local/uv-pipx/venvs/gita/.venv/lib/python3.10/site-packages/gita/__init__.py", line 1, in <module>
    import pkg_resources
ModuleNotFoundError: No module named 'pkg_resources'
```

Solution: inject setuptools

```bash
uvpipx inject gita setuptools
```

all is good now !!
