#!/usr/bin/env fab
# -*- coding: utf-8 -*-
"Setup Staging Environments"

import sys
from functools import wraps
from fabric.api import env, abort, prompt, execute
from fabric.colors import white, blue, cyan, green, yellow, red, magenta
from fabric.contrib.console import confirm


__all__ = [
    'STAGE_NAMES', 'prompt_for_stage', 'ensure_stage', 
    'working_branch', 'check_branch',
]


STAGE_NAMES = []

def stage(fn):
    """ Decorator indicating this function sets a stage environment.
    """
    STAGE_NAMES.append(fn.__name__)
    __all__.append(fn.__name__)
    return fn

def validate_stage(name):
    """ Tests whether given name is a valid staging environment.
        
            name = fabric.api.prompt(msg, validate=validate_stage)
    """
    name = name.strip()
    if name not in STAGE_NAMES:
        raise Exception("%r is not a valid staging environment!" % name)
    return name


def prompt_for_stage(fn):
    "Decorator which prompts for a stage-name if not set."
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'deploy_env' not in env:
            name = prompt(white('Please select a staging target %s:' % STAGE_NAMES, bold=True), validate=validate_stage)
            execute(name)
        # Must call `execute` on the supplied task, otherwise the host-lists won't be updated.
        execute(fn, *args, **kwargs)
    
    return wrapper

def ensure_stage(fn):
    "Decorator that ensures a stage is set."
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'deploy_env' not in env:
            abort(red('You must specify a staging environment (prod, stage) prior to deploy!', bold=True))
        return fn(*args, **kwargs)
    
    return wrapper


def check_branch(fn):
    "Decorator that ensures deploy branch matches current branch."
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        env.working_branch = working_branch()
        if env.working_branch != env.git_branch:
            question = 'Your working branch %(working_branch)r does not match the expected branch %(git_branch)r for %(deploy_env)s. Proceed anyway?' % env
            confirm(yellow(question, bold=True))
        return fn(*args, **kwargs)
    
    return wrapper


### Stages

# env.stages = ['prod', 'staging']

# (otto) There should be a way to do this using stages.
# See: http://tav.espians.com/fabric-python-with-cleaner-api-and-parallel-deployment-support.html
# (dsc) ...except that most of those changes are not actually in Fabric :(



###
# NOTE WELL: These do not have @task as they'd show up as "stages.prod",
# and we want them at the top level. See __init__.py for the wrappers.
# Unfortunately, we can't put them in __init__.py without preventing deploy.py
# from importing them.
###

@stage
def prod():
    """ Set deploy environment to production.
    """
    env.deploy_env      = 'prod'
    env.hosts           = ['reportcard2.pmtpa.wmflabs']
    env.gateway         = 'bastion.wmflabs.org'
    env.target_dir      = '/srv/reportcard/limn'
    env.target_link_dir = '/srv/reportcard/limn/var/data'
    env.target_data_dir = '/srv/reportcard/reportcard-data'
    env.target_data_to  = 'rc'
    env.git_branch      = 'master'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/reportcard/data.git'
    env.git_data_branch = 'master'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.supervisor_job  = 'reportcard'


@stage
def test():
    """ Set deploy environment to test.
    """
    env.deploy_env      = 'test'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion.wmflabs.org'
    env.target_dir      = '/srv/test-reportcard.wmflabs.org/limn'
    env.target_link_dir = '/srv/test-reportcard.wmflabs.org/limn/var/data'
    env.target_data_dir = '/srv/test-reportcard.wmflabs.org/reportcard-data'
    env.target_data_to  = 'rc'
    env.git_branch      = 'master'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/reportcard/data.git'
    env.git_data_branch = 'master'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.supervisor_job  = 'test-reportcard'


@stage
def gp_dev():
    """ Set deploy environment to gp_dev.
    """
    env.deploy_env      = 'gp_dev'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion.wmflabs.org'
    env.target_dir      = '/srv/gp-dev.wmflabs.org/limn'
    env.target_link_dir = '/srv/gp-dev.wmflabs.org/limn/var/data'
    env.target_data_dir = '/srv/gp-dev.wmflabs.org/limn-data'
    env.target_data_to  = 'gp'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/global-dev/dashboard-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.supervisor_job  = 'gp-dev'


@stage
def dev():
    """ Set deploy environment to dev.
    """
    env.deploy_env      = 'dev'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion.wmflabs.org'
    env.target_dir      = '/srv/dev-reportcard.wmflabs.org/limn'
    env.target_link_dir = '/srv/dev-reportcard.wmflabs.org/limn/var/data'
    env.target_data_dir = '/srv/dev-reportcard.wmflabs.org/reportcard-data'
    env.target_data_to  = 'rc'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/reportcard/data.git'
    env.git_data_branch = 'develop'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.supervisor_job  = 'dev-reportcard'


@stage
def lessly():
    """ Set deploy environment to lessly.
    """
    env.deploy_env      = 'lessly'
    env.hosts           = ['less.ly']
    env.target_dir      = '/home/wmf/projects/limn'
    env.target_data_dir = '/home/wmf/projects/reportcard-data'
    env.target_data_to  = 'rc'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/reportcard/data.git'
    env.git_data_branch = 'develop'
    env.owner           = 'wmf'
    env.group           = 'www'
    if 'gateway' in env: del env['gateway']

