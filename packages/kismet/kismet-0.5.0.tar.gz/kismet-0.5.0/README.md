# Kismet
A dice roll parser with personality

## Installation
```bash
pip install kismet
```

### Jupyter
After installation with `pip`, you may optionally install the Jupyter kernel:
```bash
pythom -m kismet.kernel.install
```


## Docker

### Command Line Interface
```bash
docker run autochthe/kismet
```

### Jupyterlab Server
```bash
docker run -p 8888:8888 autochthe/kismet.jupyter
```
#### With vim
```bash
docker run -p 8888:8888 autochthe/kismet.jupyter.vim
```

### Chatbots

#### Discord

Define `DISCORD_CLIENTID` and `DISCORD_TOKEN`.
```bash
DISCORD_CLIENTID=00000 \
DISCORD_TOKEN=xxx.xxx \
docker run \
    -e DISCORD_CLIENTID \
    -e DISCORD_TOKEN \
    autochthe/kismet.discord
```


#### Slack

Define `SLACK_TOKEN`.
```bash
SLACK_TOKEN=xxx-xxx-xxx \
docker run \
    -e SLACK_TOKEN \
    autochthe/kismet.slack
```

## Docker service runners
These scripts manage and run Docker services (eg. on cloud hosting).

WARNING: These runners automatically call `docker image prune`.

### Jupyterlab Server
```bash
wget https://raw.githubusercontent.com/autochthe/kismet-py/master/docker/run/kismet.jupyter
chmod a+x kismet.jupyter
./kismet.jupyter
```
#### With vim
```bash
wget https://raw.githubusercontent.com/autochthe/kismet-py/master/docker/run/kismet.jupyter.vim
chmod a+x kismet.jupyter.vim
./kismet.jupyter.vim
```

### Discord Bot
Define `DISCORD_CLIENTID` and `DISCORD_TOKEN` before execution.
```bash
wget https://raw.githubusercontent.com/autochthe/kismet-py/master/docker/run/kismet.discord
chmod a+x kismet.discord

## Edit `kismet.discord` and
# ./kismet.discord

## OR
# DISCORD_CLIENTID=00000 \
# DISCORD_TOKEN=xxx.xxx \
# ./kismet.discord
```

The OAuth invite link will print to stdout.

#### Discord Permissions
Permissions integer: `377957238848`
* Send Messages
* Send Messages in Threads
* Create Public Threads
* Create Private Threads
* Embed Links
* Attach Files
* Read Message History
* Add Reactions


### Slack Bot
Define `SLACK_TOKEN` before execution.
```bash
wget https://raw.githubusercontent.com/autochthe/kismet-py/master/docker/run/kismet.slack
chmod a+x kismet.slack

## Edit `kismet.slack` and
# ./kismet.slack

## OR
# SLACK_TOKEN=xxx.xxx \
# ./kismet.slack
```
