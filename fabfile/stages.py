#!/usr/bin/env fab
# -*- coding: utf-8 -*-
"Setup Staging Environments"

import sys
from functools import wraps
from fabric.api import env, abort, prompt, execute, task
from fabric.colors import white, blue, cyan, green, yellow, red, magenta
from fabric.contrib.console import confirm
from util import InvalidChoice


__all__ = [
    'STAGES', 'STAGE_NAMES', 'prompt_for_stage', 'ensure_stage', 'list_stages',
    'working_branch', 'check_branch',
]


STAGES = {}
STAGE_NAMES = []

def stage(fn):
    """ Decorator indicating this function sets a stage environment.
    """
    STAGES[fn.__name__] = fn
    STAGE_NAMES.append(fn.__name__)
    __all__.append(fn.__name__)
    return fn

def validate_stage(name):
    """ Tests whether given name is a valid staging environment.
        
            name = fabric.api.prompt(msg, validate=validate_stage)
    """
    name = name.strip()
    if name not in STAGE_NAMES:
        raise InvalidChoice("%r is not a valid staging environment!" % name)
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
            abort(red('You must specify a staging environment (%s) prior to deploy!' % ', '.join(STAGE_NAMES), bold=True))
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

@task(default=True)
def list_stages():
    "List deployment enviornments."
    print "Stages:\n"
    maxlen = max(map(len, STAGE_NAMES))
    for name, stage in STAGES.iteritems():
        print '    %s  %s' % (name.ljust(maxlen), stage.__doc__.strip())

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
    """ reportcard.wmflabs.org
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
def test_reportcard():
    """ test-reportcard.wmflabs.org
    """
    env.deploy_env      = 'test_reportcard'
    env.hosts           = ['limn0.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/test-reportcard'
    env.target_data_dir = '/var/lib/limn/test-reportcard/data'
    env.target_data_to  = 'rc'
    env.git_branch      = 'master'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/reportcard/data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-test-reportcard'
    env.provider        = 'upstart'


@stage
def gp():
    """ gp.wmflabs.org
    """
    env.deploy_env      = 'gp'
    env.hosts           = ['limn0.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/gp'
    env.target_data_dir = '/var/lib/limn/gp/data'
    env.target_data_to  = 'gp'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/global-dev/dashboard-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-gp'
    env.provider        = 'upstart'


@stage
def dev_reportcard():
    """ dev-reportcard.wmflabs.org
    """
    env.deploy_env      = 'dev_reportcard'
    env.hosts           = ['limn0.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/dev-reportcard'
    env.target_data_dir = '/var/lib/limn/dev-reportcard/data'
    env.target_data_to  = 'rc'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/reportcard/data.git'
    env.git_data_branch = 'develop'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-dev-reportcard'
    env.provider        = 'upstart'


@stage
def mobile():
    """ mobile-reportcard.wmflabs.org
    """
    env.deploy_env      = 'mobile'
    env.hosts           = ['limn0.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/mobile-reportcard'
    env.target_data_dir = '/var/lib/limn/mobile-reportcard/data'
    env.target_data_to  = 'mobile'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/limn-mobile-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-mobile-reportcard'
    env.provider        = 'upstart'

@stage
def mobile_dev():
    """ mobile-reportcard-dev.wmflabs.org
    """
    env.deploy_env      = 'mobile_dev'
    env.hosts           = ['limn0.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/mobile-reportcard-dev'
    env.target_data_dir = '/var/lib/limn/mobile-reportcard-dev/data'
    env.target_data_to  = 'mobile'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/limn-mobile-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-mobile-reportcard-dev'
    env.provider        = 'upstart'


@stage
def ee_dashboard():
    """ ee-dashboard.wmflabs.org
    """
    env.deploy_env      = 'ee_dashboard'
    env.hosts           = ['limn0.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/ee-dashboard'
    env.target_data_dir = '/var/lib/limn/ee-dashboard/data'
    env.target_data_to  = 'eee'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-editor-engagement-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-ee-dashboard'
    env.provider        = 'upstart'


@stage
def gerrit_stats():
    """ gerrit-stats.wmflabs.org
    """
    env.deploy_env      = 'gerrit_stats'
    env.hosts           = ['limn0.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/gerrit-stats'
    env.target_data_dir = '/var/lib/limn/gerrit-stats/data'
    env.target_data_to  = 'gs'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/gerrit-stats/data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-gerrit-stats'
    env.provider        = 'upstart'


@stage
def debugging():
    """ debugging.wmflabs.org
    """
    env.deploy_env      = 'debugging'
    env.hosts           = ['limn0.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/debugging'
    env.target_data_dir = '/var/lib/limn/debugging/data'
    env.target_data_to  = 'debugging'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-debugging-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-debugging'
    env.provider        = 'upstart'


@stage
def stats_limn001():
    """ stats.wmflabs.org
    """
    env.deploy_env      = 'stats_limn001'
    env.hosts           = ['stats-limn001.pmtpa.wmflabs']
    env.gateway         = 'bastion2.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/stats'
    env.target_data_dir = '/var/lib/limn/stats/data'
    env.target_data_to  = 'example'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-stats'
    env.provider        = 'upstart'



# NOTE: this is how the old supervisor deploy stage looked, for reference
#@stage
#def debugging():
    #""" debugging.wmflabs.org
    #"""
    #env.deploy_env      = 'debugging'
    #env.hosts           = ['kripke.pmtpa.wmflabs']
    #env.gateway         = 'bastion2.wmflabs.org'
    #env.target_dir      = '/srv/debugging.wmflabs.org/limn'
    #env.target_var_dir  = '/srv/debugging.wmflabs.org/limn/var'
    #env.target_data_dir = '/srv/debugging.wmflabs.org/debugging-data'
    #env.target_data_to  = 'debugging'
    #env.git_branch      = 'develop'
    #env.git_data_origin = 'https://github.com/wikimedia/limn-debugging-data.git'
    #env.git_data_branch = 'master'
    #env.owner           = 'www-data'
    #env.group           = 'www'
    #env.provider_job    = 'debugging'
    #env.provider        = 'supervisor'
