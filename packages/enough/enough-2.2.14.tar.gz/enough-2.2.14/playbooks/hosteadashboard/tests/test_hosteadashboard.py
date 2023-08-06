import requests
import sh
import yaml

from enough.common import retry

from playbooks.hostea.roles.hostea.files import hosteasetup
from playbooks.hostea.tests.test_hostea import (
    wait_for_bootstrap,
    wait_for_destruction,
    get_fleet_domain,
)
from playbooks.hosteadashboard.tests.hostea import Hostea
from playbooks.hosteadashboard.tests.gitea import GiteaSSO

testinfra_hosts = ['ansible://gitea-host']


def get_domain(inventory):
    vars_dir = f'{inventory}/group_vars/all'
    return yaml.safe_load(open(vars_dir + '/domain.yml'))['domain']


def test_hosteadashboard_create_delete_vm(pytestconfig, host, tmpdir):
    #
    # Wait until the Hostea fleet is ready to sail, i.e. when the DNS answers
    #
    gitea_domain = get_domain(pytestconfig.getoption("--ansible-inventory"))
    d = f"{tmpdir}/hostea"
    git = sh.git.bake("-c", "http.sslVerify=false")
    wait_for_bootstrap(git, d, gitea_domain)

    #
    # Under which pavillion is the Hostea fleet sailing, i.e. what is its domain name?
    #
    fleet_domain = get_fleet_domain(d)

    #
    # Create the shipyard, i.e. run manage.py vm
    #
    def manage_vm(command):
        with host.sudo():
            cmd = host.run(f"""
            set -ex
            cd /srv/hosteadashboard/dashboard
            /srv/hosteadashboard/venv/bin/python3 manage.py vm {command}
            """)
            print(cmd.stdout)
            print(cmd.stderr)
            assert 0 == cmd.rc

    #
    # Commandeer a new ship, i.e. ask the dashboard to create a new Gitea instance
    #
    vm = "thevm"
    manage_vm(f"create {vm} --owner=adminuser --flavor=small")

    #
    # Wait for the shipyard to deliver, i.e. wait until the Gitea instance is ready
    #
    @retry.retry(AssertionError, tries=60, delay=30, exponential=False)
    def wait_for_vm():
        try:
            page = sh.curl("--max-time", "10", "--insecure", f"https://{vm}.{fleet_domain}")
            assert "Gitea" in page
        except sh.ErrorReturnCode_6:
            assert 0, "cloud not resolve"
        except sh.ErrorReturnCode_28:
            assert 0, "timeout"
        except sh.ErrorReturnCode_7:
            assert 0, "Failed to connect"
    wait_for_vm()

    #
    # Decommission the ship, i.e. destroy the Gitea instance
    #
    manage_vm(f"delete {vm}")

    #
    # Wait until the last piece is gone, i.e. wait for the host
    # to no longer exist from the OpenStack point of view
    #
    wait_for_destruction(f"{vm}-host")


def test_hosteadashboard_support(
        pytestconfig, host, gitea_hostname, make_user, make_project, certs, tmpdir):
    domain = get_domain(pytestconfig.getoption("--ansible-inventory"))

    dash_username = "adminuser"
    dash_password = "etiquofEtseudett"
    dash_email = f"contact@{domain}",
    dash_host = f"https://hosteadashboard.{domain}"
    dash_project = "support"

    forge = hosteasetup.Gitea(gitea_hostname)
    forge.certs(certs)
    make_user(forge, dash_username, dash_password)
    forge.authenticate(username=dash_username, password=dash_password)
    make_project(forge, dash_username, dash_project)

    dash_c = requests.Session()
    dash_c.verify = certs
    dash_c.headers["Referer"] = dash_host

    dash = Hostea(
        username=dash_username,
        email=dash_email,
        password=dash_password,
        host=dash_host,
        c=dash_c,
    )
    dash.login()

    dash_gitea_sso = GiteaSSO(
        username=dash_username,
        email=dash_email,
        gitea_host=f"https://{gitea_hostname}",
        hostea_org=dash_username,
        support_repo=dash_project,
        c=dash_c,
    )
    dash_gitea_sso._sso_login()
