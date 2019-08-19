from lib import juju_cli
import os
from jinja2 import Environment, FileSystemLoader


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
cloud_name = 'openstack'
controller_name = 'openstack'
model_name = 'openstack'
k8s_bundle = "Clouds/Openstack/Bundles/k8s-bundle.yaml"

def render_openstack_cloud_files():
    keystone_ip = '172.27.32.29'
    admin_password = juju_cli.run(model_name, 'keystone/0', 'leader-get admin_passwd')

    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)

    openstack_cloud_sdk = j2_env.get_template('Clouds/Openstack/template/openstack-cloud-sdk.yaml.j2').render(
        keystone_ip=keystone_ip.rstrip(), admin_password=admin_password.rstrip())



    openstack_cloud_juju = j2_env.get_template('Clouds/Openstack/template/openstack-cloud-juju.yaml.j2').render(
        keystone_ip=keystone_ip.rstrip())

    openstack_credentials = j2_env.get_template('Clouds/Openstack/template/openstack-cloud-credentials.yaml.j2').render(
        keystone_ip=keystone_ip.rstrip(), admin_password=admin_password.rstrip())

    with open('Clouds/Openstack/openstack-cloud.yaml', 'w+') as f:
        f.write(openstack_cloud_juju)

    with open('Clouds/Openstack/openstack-credentials.yaml', 'w+') as f:
        f.write(openstack_credentials)

    with open('/home/ubuntu/.config/openstack/clouds.yaml', 'w+') as f:
        f.write(openstack_cloud_sdk)

def bootstrap_juju():
    juju_cli.add_cloud(cloud_name, 'Clouds/Openstack/openstack-cloud.yaml')
    juju_cli.add_credential(cloud_name, 'Clouds/Openstack/openstack-credentials.yaml')
    openstack_utils.create_public_network()
    openstack_utils.create_private_network()
    openstack_utils.create_router()
    openstack_utils.creat_flavor()
    pub_net = openstack_utils.conn.network.find_network(openstack_utils.public_net_name)
    priv_net = openstack_utils.conn.network.find_network(openstack_utils.private_net_name)
    juju_cli.bootstrap(cloud_name, options=['--config', 'network=' + str(priv_net.id),
    '--config', 'external-network=' + str(pub_net.id), '--config','use-floating-ip=true', '-d', model_name])
    juju_cli.deploy(model_name, k8s_bundle)

if __name__ == '__main__':
    render_openstack_cloud_files()
    from lib import openstack_utils
    bootstrap_juju()
