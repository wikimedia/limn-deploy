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
    env.hosts           = ['reportcard.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/lib/limn'
    env.target_var_dir  = '/var/lib/limn/reportcard'
    env.target_data_dir = '/var/lib/limn/reportcard-data'
    env.target_data_to  = 'rc'
    env.git_branch      = 'master'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/reportcard/data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-reportcard'
    env.provider        = 'upstart'


@stage
def test():
    """ Set deploy environment to test.
    """
    env.deploy_env      = 'test'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/srv/test-reportcard.wmflabs.org/limn'
    env.target_var_dir  = '/srv/test-reportcard.wmflabs.org/limn/var'
    env.target_data_dir = '/srv/test-reportcard.wmflabs.org/reportcard-data'
    env.target_data_to  = 'rc'
    env.git_branch      = 'master'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/reportcard/data.git'
    env.git_data_branch = 'master'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.provider_job    = 'test-reportcard'
    env.provider        = 'supervisor'


@stage
def gp():
    """ Set deploy environment to gp_dev.
    """
    env.deploy_env      = 'gp'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/srv/gp.wmflabs.org/limn'
    env.target_var_dir  = '/srv/gp.wmflabs.org/limn/var'
    env.target_data_dir = '/srv/gp.wmflabs.org/limn-data'
    env.target_data_to  = 'gp'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/global-dev/dashboard-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.provider_job    = 'gp'
    env.provider        = 'supervisor'


@stage
def dev():
    """ Set deploy environment to dev.
    """
    env.deploy_env      = 'dev'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/srv/dev-reportcard.wmflabs.org/limn'
    env.target_var_dir  = '/srv/dev-reportcard.wmflabs.org/limn/var'
    env.target_data_dir = '/srv/dev-reportcard.wmflabs.org/reportcard-data'
    env.target_data_to  = 'rc'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/reportcard/data.git'
    env.git_data_branch = 'develop'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.provider_job    = 'dev-reportcard'
    env.provider        = 'supervisor'


@stage
def mobile():
    """ Set deploy environment to mobile reportcard.
    """
    env.deploy_env      = 'mobile'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/srv/mobile-reportcard.wmflabs.org/limn'
    env.target_var_dir  = '/srv/mobile-reportcard.wmflabs.org/limn/var'
    env.target_data_dir = '/srv/mobile-reportcard.wmflabs.org/mobile-data'
    env.target_data_to  = 'mobile'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-mobile-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.provider_job    = 'mobile-reportcard'
    env.provider        = 'supervisor'

@stage
def mobile_dev():
    """ Set deploy environment to mobile reportcard.
    """
    env.deploy_env      = 'mobile_dev'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/srv/mobile-reportcard-dev.wmflabs.org/limn'
    env.target_var_dir  = '/srv/mobile-reportcard-dev.wmflabs.org/limn/var'
    env.target_data_dir = '/srv/mobile-reportcard-dev.wmflabs.org/mobile-data'
    env.target_data_to  = 'mobile'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-mobile-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.provider_job    = 'mobile-reportcard-dev'
    env.provider        = 'supervisor'


@stage
def ee_dashboard():
    """ Set deploy environment to editor engagement dashboard
    """
    env.deploy_env      = 'ee_dashboard'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/srv/ee-dashboard.wmflabs.org/limn'
    env.target_var_dir  = '/srv/ee-dashboard.wmflabs.org/limn/var'
    env.target_data_dir = '/srv/ee-dashboard.wmflabs.org/editor-engagement-data'
    env.target_data_to  = 'eee'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-editor-engagement-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.provider_job    = 'ee-dashboard'
    env.provider        = 'supervisor'


@stage
def debugging():
    """ Set deploy environment to debugging
    """
    env.deploy_env      = 'debugging'
    env.hosts           = ['kripke.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/srv/debugging.wmflabs.org/limn'
    env.target_var_dir  = '/srv/debugging.wmflabs.org/limn/var'
    env.target_data_dir = '/srv/debugging.wmflabs.org/debugging-data'
    env.target_data_to  = 'debugging'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-debugging-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'www-data'
    env.group           = 'www'
    env.provider_job    = 'debugging'
    env.provider        = 'supervisor'
