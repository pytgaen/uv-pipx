# uvpipx Configuration Guide

## Introduction

This guide will help you understand and configure uvpipx effectively.

## Show current configuration

To see your current configuration, use the following command:

```bash
uvpipx environnement
```

This will display detailed information about your configuration, by example:

```bash
uvpipx version 0.7.0

🔍 Uvpipx configuration:
💻 platform = linux
💻 python version = 3.10.12
💻 uv version = 0.2.32
🏠 user home = /home/pytgaen

🌳 uvpipx home = /home/pytgaen/.local/uv-pipx
    Path to the main directory of uvpipx.
    🎚️  Defined by the UVPIPX_HOME environment variable or defaults to ~/.local/uv-pipx

🌿 uvpipx venvs = /home/pytgaen/.local/uv-pipx/venvs
    Path to the directory of uvpipx virtual environments.
    🎚️  Defined by the UVPIPX_LOCAL_VENVS environment variable or defaults to $UVPIPX_HOME/venvs

📁 exposing bin directory = /home/pytgaen/.local/bin
    Default path for exposed executables.
    Default:
            ~/.local/bin for normal users or
            /usr/local/bin for root.
    🎚️  Can be defined by the UVPIPX_BIN_DIR environment variable
```

## Understanding and Modifying Configuration

uvpipx uses environment variables for its configuration. Here are the main variables and their purposes:

### 🌳 UVPIPX_HOME

The path to the main directory of uvpipx. This variable is used to define the location of the uvpipx home directory, which contains the virtual environments and the bin directory.

🎚️ Default value is `~/.local/uv-pipx`.

### 🌿 UVPIPX_LOCAL_VENVS

The path to the directory of uvpipx virtual environments. This variable is used to define the location of the uvpipx virtual environments directory.

🎚️ Default value is `$UVPIPX_HOME/venvs`.

### 📁 UVPIPX_BIN_DIR

The path to the directory where the executables of uvpipx are exposed. This variable is used to define the location of the uvpipx exposed bin directory.  

💡**Tip**: Ensure that `UVPIPX_BIN_DIR` is in your PATH. Use `uvpipx ensurepath` to check and add it if necessary.

🎚️ Default value:
- on unix: `~/.local/bin` for normal users or `/usr/local/bin` for root.
- on windows: `%HOME%\.local\bin`.

Next page [Use to build container image](concainer.md)
