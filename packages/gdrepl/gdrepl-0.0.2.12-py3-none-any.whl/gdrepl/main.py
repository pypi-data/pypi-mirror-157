import os
import re
import subprocess as sb

import click
import pexpect
from dataclasses import dataclass
from click_default_group import DefaultGroup
from prompt_toolkit.completion import (WordCompleter, Completer)
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import prompt
from pygments.lexers.gdscript import GDScriptLexer

from .client import client as wsclient
from .constants import GODOT, KEYWORDS, PORT, VI
from .commands import (Command, COMMANDS)
from .find_godot import godot_command, find_available_port, find_godot

STDOUT_MARKER_START = "----------------STDOUT-----------------------"
STDOUT_MARKER_END = "----------------STDOUT END-----------------------"
TIMEOUT = 0.2

GODOT = find_godot()

history = InMemoryHistory()


@dataclass
class PromptOptions:
    vi: bool = False
    timeout: int = TIMEOUT


class CustomCompleter(Completer):
    """Auto completion and commands"""

    def __init__(self):
        self.word_completer = WordCompleter(
            KEYWORDS + list(COMMANDS.keys()), WORD=True)
        self.document = None
        self.iterator = None

    def _create_iterator(self, completer, document, complete_event):
        self.iterator = completer.get_completions(document, complete_event)

    def get_completions(self, document, complete_event):
        # Only complete after 1st character of last word
        if len(document.text_before_cursor.split(" ")[-1]) < 1:
            return

        cmd = document.text.split()[0]
        if cmd in COMMANDS and len(document.text_before_cursor.strip()) > len(cmd):
            sub_doc = Document(document.text[len(cmd) + 1:])
            self._create_iterator(COMMANDS[cmd].completer,
                                  sub_doc, complete_event)

        elif document != self.document:
            self.document = document
            self._create_iterator(self.word_completer,
                                  document, complete_event)
        for w in self.iterator:
            yield w


def _prompt(options, completer, multiline=False, ident_level=0):
    return prompt(
        ">>> " if not multiline else "... ",
        vi_mode=options.vi,
        default=" " * ident_level,
        history=history,
        lexer=PygmentsLexer(GDScriptLexer),
        completer=completer,
    )


def wait_for_output(server, timeout):
    try:
        server.expect(STDOUT_MARKER_START, timeout=timeout)
        server.expect(STDOUT_MARKER_END, timeout=timeout)
        output = server.before.decode()
        if output.strip():
            print(output.strip())
    except pexpect.exceptions.TIMEOUT:
        pass
    try:
        server.expect(r"SCRIPT ERROR:(.+)", timeout=timeout)
        error = server.match.group(1).decode().strip()
        error = re.sub(
            "\r\n" + r".*ERROR:.* Method failed\..*" + "\r\n.*", "", error
        )
        # if re.match(r".*SCRIPT ERROR:.*at:.*\(<built-in>:(\d+)\).*", )
        print(error)
    except pexpect.exceptions.TIMEOUT:
        pass


def repl_loop(client, options: PromptOptions, server=None):
    # Fill out our auto completion with server commands as well
    helpmsg = client.send("help")
    for line in helpmsg.split("\n"):
        helplist = line.split(":")
        if len(helplist) != 2:
            continue

        cmd = helplist[0]
        help = helplist[1]

        # Let us override the server commands help message
        if cmd in COMMANDS:
            continue
        COMMANDS[cmd] = Command(help=help, send_to_server=True)

    completer = CustomCompleter()
    multiline_buffer = ""
    multiline = False
    ident_level = 0
    while True:
        try:
            cmd = _prompt(options, completer, multiline, ident_level)
        except KeyboardInterrupt:
            multiline = False
            multiline_buffer = ""
            ident_level = 0
            continue
        except EOFError:
            client.close()
            break

        if len(cmd.strip()) == 0:
            if not multiline:
                continue
            multiline = False
            # HACK force run
            multiline_buffer += ";"

        if cmd.strip() in ["quit", "exit"]:
            client.send(cmd, False)
            client.close()
            break

        if not multiline and len(cmd.split()) > 0 and cmd.split()[0] in COMMANDS:
            command = COMMANDS[cmd.split()[0]]
            command.do(client, cmd.split()[1:])
            if not command.send_to_server:
                continue

        history._loaded_strings = list(dict.fromkeys(history._loaded_strings))

        # Switch to multiline until return is pressed twice
        if cmd.strip().endswith(":"):
            multiline = True
            ident_level = len(cmd.rstrip()) - len(cmd.strip()) + 1

        multiline_buffer += cmd
        if multiline:
            multiline_buffer += "\n"
            continue

        resp = client.send(multiline_buffer)
        multiline_buffer = ""
        ident_level = 0

        if resp:
            print(resp)

        if server is not None:
            wait_for_output(server, options.timeout)


def start_message():
    print(
        "Welcome to GDScript REPL. Hit Ctrl+D to exit. If you start having errors type 'reset'"
    )


@click.group(cls=DefaultGroup, default="run", default_if_no_args=True)
def cli():
    pass


@cli.command(help="Launch the godot server and starts the repl")
@click.option("--vi", is_flag=True, default=VI, help="Use vi mode")
@click.option("--godot", default=GODOT, help="Path to godot executable")
@click.option(
    "--command", default="", help="Custom command to run the server script with"
)
@click.option("--timeout", default=TIMEOUT, help="Time to wait for godot output")
def run(vi, godot, command, timeout):
    if not godot:
        return
    server = None

    port = find_available_port(PORT)
    env = os.environ.copy()
    env["PORT"] = str(port)

    if command:
        server = pexpect.spawn(command, env=env)
    else:
        server = pexpect.spawn(godot_command(godot), env=env)
    server.expect(r".*Godot Engine (\S+) .*")
    version = server.match.group(1).decode().strip()
    print("Godot", version, "listening on:", port)

    server.expect("Gdrepl Listening on .*")

    start_message()
    client = wsclient(port=port)
    repl_loop(client, PromptOptions(vi=vi, timeout=timeout), server)


@cli.command(help="Connects to a running godot repl server")
@click.option("--vi", is_flag=True, default=VI, help="Use vi mode")
@click.option("--port", default=PORT, help="Port to connect to")
def client(vi, port):
    client = wsclient(port=port)
    start_message()
    print("Not launching server..")
    repl_loop(client, PromptOptions(vi=vi))


@cli.command(help="Starts the gdscript repl websocket server")
@click.option("--godot", default=GODOT, help="Path to godot executable")
@click.option("--port", default=PORT, help="Port to listen on")
@click.option("--verbose", is_flag=True, default=False, help="Enable debug output")
def server(port, godot, verbose):
    if not godot:
        return
    env = os.environ.copy()
    if port:
        env["PORT"] = str(port)
    else:
        env["PORT"] = str(find_available_port(port))

    if verbose:
        env["DEBUG"] = "1"

    sb.run(godot_command(godot), shell=True, env=env)
