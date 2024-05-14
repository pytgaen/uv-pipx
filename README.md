# uvpipx

![unpipx logo](https://gitlab.com/pytgaen-group/uvpipx/-/raw/main/uvpipx_logo.jpg)
_A small tool like __pipx__ using __uv__ behind the scene._ ___Fast, Small ...___

The first intention is to use it in a container or CI, (so with unix) and ⭕ dependency except uv

## Install the tool (himself 🎉)

```bash
pip install uvpipx
```

## Install a package

To install package [jc](https://pypi.org/project/jc/)

```bash
uvpipx install jc
```

Maybe you should check the path with the command `ensurepath`

```bash
uvpipx ensurepath
```

Now let use the program

```bash
wc README.md | jc --wc
[{"filename":"README.md","lines":30,"words":56,"characters":357}]
```

## List all package

```bash
uvpipx list
```

## Uninstall a package

To uninstall package [jc](https://pypi.org/project/jc/)

```bash
uvpipx uninstall jc
```

## Info on a package

To uninstall package [jc](https://pypi.org/project/jc/)

```bash
uvpipx info jc
```

or to get the venv path

```bash
uvpipx info jc --get-venv
```

## Run a package in venv

```bash
wc README.md | uvpipx venv jc -- jc --wc 
```