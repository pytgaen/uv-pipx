cd /mnt/local_dir/dist
pip install uvpipx-*.whl
export UVPIPX_HOME=/opt/uvpipx

mkdir -p /opt/uvpipx 
uvpipx install poetry
useradd -ms /bin/bash vscode

su - vscode