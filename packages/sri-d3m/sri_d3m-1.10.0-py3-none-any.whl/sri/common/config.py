D3M_API_VERSION = 'primitives'
VERSION = '1.10.0'
TAG_NAME = '1.10.0'

REPOSITORY = 'https://gitlab.com/datadrivendiscovery/contrib/sri-d3m'
ISSUES_URL = 'https://gitlab.com/datadrivendiscovery/contrib/sri-d3m/-/issues'
PACKAGE_NAME = 'sri-d3m'

D3M_PERFORMER_TEAM = 'SRI'
MAINTAINER = 'Remi Rampin'
EMAIL = 'remi.rampin@nyu.edu'

# Note, any docker image that is based on the latest stable D3M docker image will have what is needed to generate the
# primitive definitions and sample pipelines. The image listed below is an SRI ta2 docker image that uses
# registry.gitlab.com/datadrivendiscovery/images/primitives:ubuntu-bionic-python36-stable-20201201-223410 as a base.
DOCKER_IMAGE = "registry.datadrivendiscovery.org/j18_ta2eval/sri_tpot:20201103"
DATASET_HOME = "/datasets/seed_datasets_current"

PACKAGE_URI = ''
if TAG_NAME:
    PACKAGE_URI = "git+%s@%s" % (REPOSITORY, TAG_NAME)
else:
    PACKAGE_URI = "git+%s" % (REPOSITORY)

PACKAGE_URI = "%s#egg=%s" % (PACKAGE_URI, PACKAGE_NAME)


if TAG_NAME:
    INSTALLATION = {
        'type' : 'PIP',
        'package': PACKAGE_NAME,
        'version': TAG_NAME,
    }
else:
    INSTALLATION = {
        'type' : 'PIP',
        'package_uri': PACKAGE_URI,
    }

INSTALLATION_JAVA = {
    'type' : 'UBUNTU',
    'package': 'openjdk-8-jdk-headless',
    'version': '8u252-b09-1~18.04'
}

INSTALLATION_POSTGRES = {
    'type' : 'UBUNTU',
    'package': 'postgresql',
    'version': '9.5+173ubuntu0.1'
}

SOURCE = {
    'name': D3M_PERFORMER_TEAM,
    'uris': [ REPOSITORY, ISSUES_URL ],
    'contact': "mailto:%s" % (EMAIL),
}
