import os


def set_env_variable(name: str, value: str, system=False):  # type: ignore[no-untyped-def]
    import ctypes
    import winreg  # type: ignore[import-not-found]

    try:
        root_key = winreg.HKEY_LOCAL_MACHINE if system else winreg.HKEY_CURRENT_USER  # type: ignore[attr-defined]
        subkey = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment" if system else "Environment"

        key = winreg.OpenKey(root_key, subkey, 0, winreg.KEY_ALL_ACCESS)  # type: ignore[attr-defined]
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)  # type: ignore[attr-defined]
        winreg.CloseKey(key)  # type: ignore[attr-defined]

        ctypes.windll.user32.SendMessageW(65535, 0x001A, 0, "Environment")  # type: ignore[attr-defined]

        os.environ[name] = value
    except Exception as e:
        print(f"Error while setting environment variable: {e}")


def get_env_variable(name: str, system=False) -> str | None:  # type: ignore[no-untyped-def]
    """
    Lit une variable d'environnement.

    :param name: Le nom de la variable d'environnement
    :param system: Si True, lit la variable au niveau système, sinon au niveau utilisateur
    :return: La valeur de la variable d'environnement ou None si elle n'existe pas
    """
    import winreg  # type: ignore[import-not-found]

    try:
        root_key = winreg.HKEY_LOCAL_MACHINE if system else winreg.HKEY_CURRENT_USER  # type: ignore[attr-defined]
        subkey = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment" if system else "Environment"

        key = winreg.OpenKey(root_key, subkey, 0, winreg.KEY_READ)  # type: ignore[attr-defined]
        value, _ = winreg.QueryValueEx(key, name)  # type: ignore[attr-defined]
        winreg.CloseKey(key)  # type: ignore[attr-defined]
        return value  # type: ignore[return-value]
    except OSError:
        return None


# Exemple d'utilisation
if __name__ == "__main__":
    # var_name = input("Entrez le nom de la variable d'environnement : ")
    # var_value = input("Entrez la valeur de la variable d'environnement : ")
    # set_env_variable(var_name, var_value)
    pat = get_env_variable("PATH")
    print(pat)
    pass
