import os


def set_env_variable(name: str, value: str, system=False):
    import ctypes
    import winreg

    try:
        root_key = winreg.HKEY_LOCAL_MACHINE if system else winreg.HKEY_CURRENT_USER
        subkey = (
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            if system
            else "Environment"
        )

        key = winreg.OpenKey(root_key, subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)

        ctypes.windll.user32.SendMessageW(65535, 0x001A, 0, "Environment")

        os.environ[name] = value
    except Exception as e:
        print(f"Error while setting environment variable: {e}")


def get_env_variable(name: str, system=False) -> str:
    """
    Lit une variable d'environnement.

    :param name: Le nom de la variable d'environnement
    :param system: Si True, lit la variable au niveau système, sinon au niveau utilisateur
    :return: La valeur de la variable d'environnement ou None si elle n'existe pas
    """
    import winreg

    try:
        root_key = winreg.HKEY_LOCAL_MACHINE if system else winreg.HKEY_CURRENT_USER
        subkey = (
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            if system
            else "Environment"
        )

        key = winreg.OpenKey(root_key, subkey, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    except WindowsError:
        return None


# Exemple d'utilisation
if __name__ == "__main__":
    # var_name = input("Entrez le nom de la variable d'environnement : ")
    # var_value = input("Entrez la valeur de la variable d'environnement : ")
    # set_env_variable(var_name, var_value)
    pat = get_env_variable("PATH")
    print(pat)
    pass
