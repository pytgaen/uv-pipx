# uvpipx

![unpipx logo](https://gitlab.com/pytgaen-group/uvpipx/-/raw/main/uvpipx_logo.jpg)  
_A small tool like **pipx** using **uv** behind the scene._ _**Fast, Small ...**_

Can be used in a container or CI, (so with unix) and ⭕ dependency except uv ... not garbage your global python environnement

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

## Live action / Performance

Using uvpipx to build a container may seem unintuitive, but take a look at the installation times.
It's not true all the time, but if the installation time exceeds the uvpipx installation time, you'll save time.
It's possible because uvpipx has only itself and uv in dependency to download

### Install poetry study timing

![uvpipx demo](https://gitlab.com/pytgaen-group/uvpipx/-/raw/main/docs/assets/perf_uvpipx_poetry.png)  
![pip demo](https://gitlab.com/pytgaen-group/uvpipx/-/raw/main/docs/assets/perf_pip_poetry.png)  

Timing:

Tool| Time | Time total | Difference
---------|----------|---------|---------
 Uvpipx | 2.8(uvpipx)+1.1(poetry) | 3.9 seconds | reference
 Pip | 8.8 | 8.8 seconds | +4,9 seconds



## More documentation

[Gitlab pages uvpipx](https://uvpipx-pytgaen-group-cc4651f865d7ce5bdaea510cdc656d736634827532.gitlab.io)
