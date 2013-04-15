#!/usr/bin/env fab
# -*- coding: utf-8 -*-

from __future__ import with_statement
from contextlib import contextmanager
from functools import wraps
from path import path as p # renamed to avoid conflict w/ fabric.api.path

from fabric.api import *
from fabric.colors import white, blue, cyan, green, yellow, red, magenta

__all__ = (
    'InvalidChoice',
    'quietly', 'msg', 'branches', 'working_branch', 'coke', 'update_version',
    'defaults', 'expand', 'expand_env', 'format', 'expand_env',
    'validate_command', 'get_commands',
)

class InvalidChoice(Exception):
    "Exception thrown when user makes an invalid choice in a prompt."


### Context Managers

@contextmanager
def quietly(txt):
    "Wrap a block in a message, suppressing other output."
    puts(txt + "...", end='', flush=True)
    with hide('everything'): yield
    puts("woo.", show_prefix=False, flush=True)


### Decorators

def msg(txt, quiet=False):
    "Decorator to wrap a task in a message, optionally suppressing all output."
    def outer(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            if quiet:
                puts(green(txt + '...', bold=True), end='', flush=True)
                with hide('everything'):
                    result = fn(*args, **kwargs)
                puts(white('Woo.\n'), show_prefix=False, flush=True)
            else:
                puts(green(txt + '...', bold=True))
                result = fn(*args, **kwargs)
                puts(white('Woo.\n'))
            return result
        return inner
    return outer



### Git Integration

def branches(remotes=False, all=False):
    "List of git branches."
    opts = {
        'remotes' : '--remotes' if remotes else '',
        'all'     : '--all' if all else ''
    }
    return [ branch.strip().split()[-1] for branch in run('git branch --no-color %(remotes)s %(all)s' % opts).split('\n') ]

def working_branch():
    "Determines the working branch."
    return [ branch.split()[1] for branch in local('git branch --no-color', capture=True).split('\n') if '*' in branch ][0]



### Coke Integration

def coke(args, capture=False):
    """ Invokes project Cokefile.
    """
    return local('coke %s' % args, capture=capture)

@runs_once
def update_version():
    """ Ensure `lib/version.js` has up to date git revision.
    """
    coke('update_version')
    print ''



### Misc

def defaults(target, *sources):
    "Update target dict using `setdefault()` for each key in each source."
    for source in sources:
        for k, v in source.iteritems():
            target.setdefault(k, v)
    return target

def expand(s):
    "Recursively expands given string using the `env` dict."
    is_path = isinstance(s, p)
    prev = None
    while prev != s:
        prev = s
        s = s % env
    return p(s) if is_path else s

def format(s):
    "Recursively formats string using the `env` dict."
    is_path = isinstance(s, p)
    prev = None
    while prev != s:
        prev = s
        s = s.format(**env)
    return p(s) if is_path else s


@runs_once
def _expand_env():
    for k, v in env.iteritems():
        if not isinstance(v, basestring): continue
        env[k] = expand(env[k])

def expand_env(fn):
    "Decorator expands all strings in `env`."
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        _expand_env()
        return fn(*args, **kwargs)
    
    return wrapper


def validate_command(cmd):
    """ Tests whether a command-name is valid:
        
            name = fabric.api.prompt(msg, validate=validate_command)
    """
    import fabric.state
    from fabric.main import _task_names
    
    cmd = cmd.strip()
    if cmd not in _task_names(fabric.state.commands):
        raise InvalidChoice("%r is not a valid command!" % cmd)
    
    return cmd

def get_commands():
    """ Attempts to figure out what commands the user wants to run, returning
        a list of tuples of: (cmd_name, args, kwargs, hosts, roles, exclude_hosts)
    """
    # Note: Most of this is lifted from fabric.main
    
    from fabric import state, api
    from fabric.main import parse_options, parse_arguments, parse_remainder
    
    # Parse command line options
    parser, options, arguments = parse_options()
    
    # Handle regular args vs -- args
    arguments = parser.largs
    remainder_arguments = parser.rargs
    
    # Parse arguments into commands to run (plus args/kwargs/hosts)
    commands_to_run = parse_arguments(arguments)
    
    # Parse remainders into a faux "command" to execute
    remainder_command = parse_remainder(remainder_arguments)
    
    # Generate remainder command and insert into commands, commands_to_run
    if remainder_command:
        commands_to_run.append(('<shell>', [remainder_command], {}, [], [], []))
    
    return commands_to_run


# def prompt_for_command(fn):
#     "Decorator which prompts for a non-stage command to execute."
#     
#     @wraps(fn)
#     def wrapper(*args, **kwargs):
#         cmds = [ cmd[0] for cmd in get_commands() ]
#         if not cmds:
#             import stages
#             from fabric.main import _task_names
#             import fabric.state
#             non_stage_commands = '\n'.join(' - ' + name for name in fabric.state.commands.keys() if name not in stages.STAGE_NAMES )
#             prompt("Please select a command: %s")
#         # Must call `execute` on the supplied task, otherwise the host-lists won't be updated.
#         execute(fn, *args, **kwargs)
#     
#     return wrapper
# 
