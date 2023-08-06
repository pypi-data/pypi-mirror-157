import website
testinfra_hosts = ['ansible://website-host']


def test_website(host):
    with host.sudo():
        cmd = host.run("""
        set -xe
??? capture the headers and
check that Host: is set as expected
x-forwarded-for is set as expected

add a server_name

        """)
        print(cmd.stdout)
        print(cmd.stderr)
        assert 0 == cmd.rc

        host.run("apt-get install -y curl")

        assert host.run("curl -m 5 -I https://$(hostname -d)").rc == 0
        assert host.run("curl -m 5 -I https://www.$(hostname -d)").rc == 0
