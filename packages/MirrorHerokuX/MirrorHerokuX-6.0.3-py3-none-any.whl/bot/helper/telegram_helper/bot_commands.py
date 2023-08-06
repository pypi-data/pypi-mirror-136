import os

def getCommand(name: str, command: str):
    try:
        if len(os.environ[name]) == 0:
            raise KeyError
        return os.environ[name]
    except KeyError:
        return command
class _BotCommands:
    def __init__(self):
        self.StartCommand = getCommand('START_COMMAND', 'start')
        self.MirrorCommand = getCommand('MIRROR_COMMAND', 'mirrorx')
        self.UnzipMirrorCommand = getCommand('UNZIP_COMMAND', 'unzipmirrorx')
        self.TarMirrorCommand = getCommand('TAR_COMMAND', 'tarmirrorx')
        self.CancelMirror = getCommand('CANCEL_COMMAND', 'cancelx')
        self.CancelAllCommand = getCommand('CANCELALL_COMMAND', 'cancelallx')
        self.ListCommand = getCommand('LIST_COMMAND', 'listx')
        self.SpeedCommand = getCommand('SPEED_COMMAND', 'speedtestx')
        self.CountCommand = getCommand('COUNT_COMMAND', 'countx')
        self.StatusCommand = getCommand('STATUS_COMMAND', 'statusx')
        self.AuthorizeCommand = getCommand('AUTH_COMMAND', 'authorizex')
        self.UnAuthorizeCommand = getCommand('UNAUTH_COMMAND', 'unauthorizex')
        self.PingCommand = getCommand('PING_COMMAND', 'pingx')
        self.RestartCommand = getCommand('RESTART_COMMAND', 'restartx')
        self.StatsCommand = getCommand('STATS_COMMAND', 'statsx')
        self.HelpCommand = getCommand('HELP_COMMAND', 'helpx')
        self.LogCommand = getCommand('LOG_COMMAND', 'logx')
        self.CloneCommand = getCommand('CLONE_COMMAND', 'clonex')
        self.WatchCommand = getCommand('WATCH_COMMAND', 'watchx')
        self.TarWatchCommand = getCommand('TARWATCH_COMMAND', 'tarwatchx')
        self.deleteCommand = getCommand('DELETE_COMMAND', 'delx')

BotCommands = _BotCommands()
