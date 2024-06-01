FROM python:3.12-slim

ENV UVPIPX_HOME=/opt/uvpipx

RUN apt update && apt install --no-install-recommends -y bash-completion git curl && \
    curl -o ./pkgx --compressed -f --proto '=https' https://pkgx.sh/$(uname)/$(uname -m) && \
    install -m 755 pkgx /usr/local/bin && \
    pkgx install task && \
    useradd -ms /bin/bash vscode && \
    mkdir -p /opt/uvpipx && \
    chown -R vscode:vscode $UVPIPX_HOME 

USER vscode

ENV PATH="/home/vscode/.local/bin:${PATH}"

RUN pip install --no-cache-dir uvpipx && \
    uvpipx install poetry && \
    curl -o /home/vscode/.task.bash https://raw.githubusercontent.com/go-task/task/main/completion/bash/task.bash  && \
    printf "%b" "\nsource /home/vscode/.task.bash\n" >> /home/vscode/.bashrc

# maybe need if you want to use poetry without venv
# RUN chown -R vscode:root /usr/local $UVPIPX_HOME

WORKDIR /workspace
COPY . /workspace

# EXPOSE 8000
