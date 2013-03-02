#!/usr/bin/env fab
# -*- coding: utf-8 -*-
"Deploy Tasks"

from fabric.api import *
from fabric.colors import white, blue, cyan, green, yellow, red, magenta
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project

from stages import ensure_stage
from util import *



@task(default=True)
@expand_env
@ensure_stage
def code_and_data():
    """ Deploy the project.
    """
    only_data()
    only_code()


@task
@expand_env
@ensure_stage
def only_code():
    """ Deploy only the code
    """
    make_directories()
    fix_permissions()
    clone()
    update_branch()
    stop_server()
    remove_derived()
    link_data()
    build()
    bundle()
    
    fix_permissions()
    start_server()


@task
@expand_env
@ensure_stage
def only_data():
    """ Deploy only the data
    """
    make_directories_data()
    fix_permissions_data()
    clone_data()
    update_branch_data()
    fix_permissions_data()


@task
@expand_env
@ensure_stage
@msg('Making Target Directories')
def make_directories():
    if not exists('%(target_dir)s' % env):
        sudo('mkdir -p %(target_dir)s' % env)

@task
@expand_env
@ensure_stage
@msg('Making Target Directories for Data')
def make_directories_data():
    if not exists('%(target_data_dir)s' % env):
        sudo('mkdir -p %(target_data_dir)s' % env)

@task
@expand_env
@ensure_stage
@msg('Fixing Permissions')
def fix_permissions(user=None, group=None):
    """ Recursively fixes permissions on the deployment host.
    """
    if user  is None: user  = env.owner
    if group is None: group = env.group
    sudo('chmod -R g+w %(target_dir)s' % env)
    sudo('chown -R %s:%s %s' % (user, group, env.target_dir))

@task
@expand_env
@ensure_stage
@msg('Fixing Permissions in Data directory')
def fix_permissions_data(user=None, group=None):
    """ Recursively fixes permissions on the deployment host.
    """
    if user  is None: user  = env.owner
    if group is None: group = env.group
    sudo('chmod -R g+w %(target_data_dir)s' % env)
    sudo('chown -R %s:%s %s' % (user, group, env.target_data_dir))

@task
@expand_env
@ensure_stage
@msg('Cloning Origin')
def clone():
    """ Clones source on deployment host if not present.
    """
    if exists('%(target_dir)s/.git' % env): return
    sudo('git clone %(git_origin)s %(target_dir)s' % env)

@task
@expand_env
@ensure_stage
@msg('Cloning Data')
def clone_data():
    """ Clones data repository on deployment host if not present.
    """
    if exists('%(target_data_dir)s/.git' % env): return
    sudo('git clone %(git_data_origin)s %(target_data_dir)s' % env)

@task
@expand_env
@ensure_stage
def checkout():
    """ Checks out proper branch on deployment host.
    """
    # TODO: Locally saved data files will cause yelling?
    with cd(env.target_dir):
        sudo('git fetch --all')
        opts = {'track' : '--track origin/' if env.git_branch not in branches() else ''}
        opts.update(env)
        sudo('git checkout %(track)s%(git_branch)s' % opts)

@task
@expand_env
@ensure_stage
def checkout_data():
    """ Checks out proper data branch on deployment host.
    """
    with cd(env.target_data_dir):
        sudo('git fetch --all')
        opts = {'track' : '--track origin/' if env.git_data_branch not in branches() else ''}
        opts.update(env)
        sudo('git checkout %(track)s%(git_data_branch)s' % opts)

@task
@expand_env
@ensure_stage
@msg('Updating Branch')
def update_branch():
    """ Runs git pull on the deployment host.
    """
    with cd(env.target_dir):
        execute(checkout)
        sudo('git pull origin %(git_branch)s' % env)
        sudo('npm install')

@task
@expand_env
@ensure_stage
@msg('Updating Branch for Data repository')
def update_branch_data():
    """ Runs git pull on the deployment host.
    """
    with cd(env.target_data_dir):
        execute(checkout_data)
        sudo('git pull origin %(git_data_branch)s' % env)

@task
@expand_env
@ensure_stage
@msg('Remove Derived Files')
def remove_derived():
    """ Removes the var directory which contains all derived files
    """
    
    # Remove derived files to ensure they get regenerated
    sudo('rm -rf %(target_dir)s/var' % env)

@task
@expand_env
@ensure_stage
@msg('Sym-Linking Data')
def link_data():
    """ adds Sym-Links to the specified data directory
    """
    if not exists('%(target_var_dir)s' % env):
        sudo('mkdir -p %(target_var_dir)s' % env)
    with cd(env.target_dir):
        sudo('coke -v %(target_var_dir)s -d %(target_data_dir)s -t %(target_data_to)s link_data' % env)

@task
@expand_env
@ensure_stage
@msg('Build sources to output directory')
def build():
    """ Build sources to output directory
    """
    with cd(env.target_dir):
        sudo('coke build' % env)

@task
@expand_env
@ensure_stage
@msg('Bundling sources to support production mode')
def bundle():
    """ Bundling sources to support production mode
    """
    with cd(env.target_dir):
        sudo('coke bundle' % env)

@task
@expand_env
@ensure_stage
@msg('Stop Node.js')
def stop_server():
    """ Stop server on the deployment host.
    """
    if env.provider is 'supervisor':
        sudo("supervisorctl stop %(provider_job)s" % env)
    elif env.provider is 'upstart':
        sudo("service %(provider_job)s stop" % env)

@task
@expand_env
@ensure_stage
@msg('Start Node.js')
def start_server():
    """ Start server on the deployment host.
    """
    if env.provider is 'supervisor':
        sudo("supervisorctl stop %(provider_job)s" % env)
    elif env.provider is 'upstart':
        sudo("service %(provider_job)s stop" % env)
