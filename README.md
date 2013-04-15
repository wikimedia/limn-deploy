# Limn Deployer

[Fabric][fabric] deployer for the [Wikimedia Foundation][wmf]'s [Limn][limn] instances.


## Installation

Clone this repo; the Python dependencies are installed as usual: `pip install -e .`


## Usage

The simplest usage is just to invoke fabric with no arguments -- `fab` -- and the deployer will walk you through things. Otherwise, you can invoke fabric directly with the stage (aka, target environment) and the action to take: `fab [STAGE] [ACTION]`.


## Fabric Flags of Note

Sometimes you might want override some of fabric's defaults:

    -u USER, --user=USER  username to use when connecting to remote hosts
    -p PASSWORD, --password=PASSWORD
                          password for use with authentication and/or sudo
    -i PATH               path to SSH private key file. May be repeated.
    -g HOST, --gateway=HOST
                          gateway host to connect through
    -a, --no_agent        don't use the running SSH agent
    -A, --forward-agent   forward local agent to remote end



[fabric]: http://fabfile.org "Fabric"
[wmf]: http://wikimediafoundation.org/ "The Wikimedia Foundation"
[limn]: http://github.com/wikimedia/limn "Limn"
