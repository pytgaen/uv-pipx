# uvpipx

![uvpipx logo](https://gitlab.com/pytgaen-group/uvpipx/-/raw/main/uvpipx_logo.jpg)

**uvpipx** is a lightweight tool similar to **pipx**, using **uv** behind the scenes. It's designed to install and run Python applications in isolated environments, ensuring that your global Python setup remains clean and uncluttered.

## Key Features

- 🚀 Fast and lightweight: Leverages the speed of uv for quick installations
- 📦 Containerization-friendly: Ideal for use in containers or CI environments (Unix-based systems)
- 🔗 Minimal dependencies: Requires only uv, reducing potential conflicts
- 🌐 Environment preservation: Keeps your global Python environment clean

## Why use uvpipx?

uvpipx solves the common problem of installing Python applications without affecting your system-wide Python setup. It creates isolated environments for each application, allowing you to:

1. Install and use CLI tools without worrying about dependency conflicts
2. Easily manage and remove applications without impacting other tools
3. Experiment with different versions of the same tool

## Installation

To get started with uvpipx, simply install it using pip:

```bash
pip install uvpipx
```

## Usage

### Install a package

Use the `install` command to add a new package:

```bash
uvpipx install <package_name>
```

Example:

```bash
uvpipx install jc
```

This command creates a new virtual environment and installs the specified package along with its dependencies.

### Check the path

After installation, ensure that the uvpipx bin directory is in your PATH:

```bash
uvpipx ensurepath
```

This command helps you set up your environment correctly to use installed applications.

### Inject a program during installation (since v0.6.0)

You can install additional programs alongside the main package:

```bash
uvpipx install <package_name> --inject <program_name>
```

Example:

```bash
uvpipx install jc --inject art
```

This feature is useful when you need complementary tools in the same environment.

### List all installed packages

To see what you've installed with uvpipx:

```bash
uvpipx list
```

This provides an overview of all packages managed by uvpipx.

### Uninstall a package

Remove a package and its isolated environment:

```bash
uvpipx uninstall <package_name>
```

This command completely removes the package and its dedicated environment.

### Get information about a package

For details about an installed package:

```bash
uvpipx info <package_name>
```

To get the virtual environment path:

```bash
uvpipx info <package_name> --get-venv
```

This is useful for debugging or when you need to interact directly with the virtual environment.

### Run a package in its virtual environment

Execute a command in a package's isolated environment:

```bash
uvpipx venv <package_name> -- <command>
```

Example:

```bash
wc README.md | uvpipx venv jc -- jc --wc 
```

This allows you to use the installed tools without activating the virtual environment manually.

### Modify exposure rules

Exposure rules determine which programs from the venv are made available in your PATH:

- `__main__`: exposes all programs from the main package
- `__eponym__`: exposes only the program with the same name as the package
- `__all__`: exposes all programs in the venv (except python and pip)
- A list of specific program names

Change the exposure rule:

```bash
uvpipx expose <package_name> <rule>
```

Example:

```bash
uvpipx expose jc __main__
```

#### Changes since v0.6.0

In previous versions, uvpipx exposed programs by default with the `__all__` rule. Now, the default rule is `__main__`. This is a significant change but is more consistent with pipx behavior. To update all your existing venvs to the new rule:

```bash
uvpipx expose-all __main__
```

You can still install with the `__all__` rule if desired:

```bash
uvpipx install <package_name> --expose __all__
```

These exposure options give you fine-grained control over which tools are accessible from each installed package.

## Performance

uvpipx can significantly speed up container builds and CI processes. Here's a comparison of installation times for poetry:

| Tool   | Time                    | Total Time  | Difference     |
|--------|-------------------------|-------------|----------------|
| Uvpipx | 2.8 (uvpipx) + 1.1 (poetry) | 3.9 seconds | reference      |
| Pip    | 8.8                     | 8.8 seconds | +4.9 seconds   |

![uvpipx demo](https://gitlab.com/pytgaen-group/uvpipx/-/raw/main/docs/assets/perf_uvpipx_poetry.png)  
![pip demo](https://gitlab.com/pytgaen-group/uvpipx/-/raw/main/docs/assets/perf_pip_poetry.png)

As shown, uvpipx can offer significant time savings, especially in scenarios where multiple tools need to be installed quickly, such as in CI/CD pipelines or container builds.

## Additional Documentation

For more detailed information, advanced usage, and troubleshooting, visit the [uvpipx GitLab page](https://uvpipx-pytgaen-group-cc4651f865d7ce5bdaea510cdc656d736634827532.gitlab.io).

## Contributing

Contributions, suggestions, and bug reports are welcome. Please fill an issue on the GitLab repository.

## License

uvpipx is open-source software. Please see the LICENSE file in the repository for more details.
