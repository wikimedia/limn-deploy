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
def reportcard():
    """ reportcard.wmflabs.org
    """
    env.deploy_env      = 'reportcard'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/reportcard'
    env.target_data_dir = '/var/lib/limn/reportcard/data-repository'
    env.target_data_to  = 'rc'
    env.git_branch      = 'develop'
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
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/test-reportcard'
    env.target_data_dir = '/var/lib/limn/test-reportcard/data-repository'
    env.target_data_to  = 'rc'
    env.git_branch      = 'develop'
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
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/gp'
    env.target_data_dir = '/var/lib/limn/gp/gp-data-repository'
    env.target_data_to  = 'gp'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/global-dev/dashboard-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-gp'
    env.provider        = 'upstart'


@stage
def gp_zero():
    """ gp.wmflabs.org (wp-zero data)
    """
    env.deploy_env      = 'gp'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/gp'
    env.target_data_dir = '/var/lib/limn/gp/gp-zero-data-repository'
    env.target_data_to  = 'gp_zero'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/analytics/wp-zero/data'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-gp'
    env.provider        = 'upstart'

@stage
def gp_geowiki():
    """ gp.wmflabs.org (wp-zero data)
    """
    env.deploy_env      = 'gp'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/gp'
    env.target_data_dir = '/var/lib/limn/gp/gp-geowiki-data-repository'
    env.target_data_to  = 'gp_geowiki'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/analytics/geowiki/data-public'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-gp'
    env.provider        = 'upstart'


@stage
def mobile_reportcard():
    """ mobile-reportcard.wmflabs.org
    """
    env.deploy_env      = 'mobile_reportcard'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/mobile-reportcard'
    env.target_data_dir = '/var/lib/limn/mobile-reportcard/data-repository'
    env.target_data_to  = 'mobile'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/limn-mobile-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-mobile-reportcard'
    env.provider        = 'upstart'


@stage
def flow():
    """ flow-reportcard.wmflabs.org
    """
    env.deploy_env      = 'flow'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/flow-reportcard'
    env.target_data_dir = '/var/lib/limn/flow-reportcard/data-repository'
    env.target_data_to  = 'flow'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/limn-flow-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-flow-reportcard'
    env.provider        = 'upstart'


@stage
def ee_dashboard():
    """ ee-dashboard.wmflabs.org
    """
    env.deploy_env      = 'ee_dashboard'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/ee-dashboard'
    env.target_data_dir = '/var/lib/limn/ee-dashboard/data-repository'
    env.target_data_to  = 'eee'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-editor-engagement-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-ee-dashboard'
    env.provider        = 'upstart'


@stage
def debugging():
    """ debugging.wmflabs.org
    """
    env.deploy_env      = 'debugging'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/debugging'
    env.target_data_dir = '/var/lib/limn/debugging/data-repository'
    env.target_data_to  = 'debugging'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-debugging-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-debugging'
    env.provider        = 'upstart'


@stage
def example():
    """ debugging.wmflabs.org/dashboards/sample
    """
    env.deploy_env      = 'debugging'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/debugging'
    env.target_data_dir = '/var/lib/limn/example/data-repository'
    env.target_data_to  = 'example'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/wikimedia/limn-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-debugging'
    env.provider        = 'upstart'


@stage
def multimedia():
    """ multimedia-metrics.wmflabs.org
    """
    env.deploy_env      = 'multimedia_metrics'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/multimedia-metrics'
    env.target_data_dir = '/var/lib/limn/multimedia-metrics/data-repository'
    env.target_data_to  = 'multimedia'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/analytics/multimedia/config'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-multimedia-metrics'
    env.provider        = 'upstart'


@stage
def glam():
    """ multimedia-metrics.wmflabs.org
    """
    env.deploy_env      = 'glam_metrics'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/glam-metrics'
    env.target_data_dir = '/var/lib/limn/glam-metrics/data-repository'
    env.target_data_to  = 'glam'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://github.com/Commonists/limn-glam.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-glam-metrics'
    env.provider        = 'upstart'


@stage
def edit():
    """ edit-reportcard.wmflabs.org
    """
    env.deploy_env      = 'edit'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/edit-reportcard'
    env.target_data_dir = '/var/lib/limn/edit-reportcard/data-repository'
    env.target_data_to  = 'edit'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/limn-edit-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-edit-reportcard'
    env.provider        = 'upstart'


@stage
def language():
    """ language-reportcard.wmflabs.org
    """
    env.deploy_env      = 'language'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/language-reportcard'
    env.target_data_dir = '/var/lib/limn/language-reportcard/data-repository'
    env.target_data_to  = 'language'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/limn-language-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-language-reportcard'
    env.provider        = 'upstart'


@stage
def extdist():
    """ extdist-reportcard.wmflabs.org
    """
    env.deploy_env      = 'extdist'
    env.hosts           = ['limn1.eqiad.wmflabs']
    env.gateway         = 'bastion-eqiad.wmflabs.org'
    env.target_dir      = '/usr/local/share/limn'
    env.target_var_dir  = '/var/lib/limn/extdist-reportcard'
    env.target_data_dir = '/var/lib/limn/extdist-reportcard/data-repository'
    env.target_data_to  = 'extdist'
    env.git_branch      = 'develop'
    env.git_data_origin = 'https://gerrit.wikimedia.org/r/p/analytics/limn-extdist-data.git'
    env.git_data_branch = 'master'
    env.owner           = 'limn'
    env.group           = 'limn'
    env.provider_job    = 'limn-extdist-reportcard'
    env.provider        = 'upstart'
