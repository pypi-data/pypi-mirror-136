from app.controllers.setup_controller import Setup
from app.controllers.credentials_controller import CredentialsController
from app.controllers.status_controller import StatusController
from app.controllers.addresses_controller import AddressController
from app.controllers.tx_controller import TxController
from app.utilities.decorators import creds, check_status
from app.utilities.terraform import Tf

import boto3
import click
import os


class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
                          ' NOTE: This argument is mutually exclusive with %s' %
                          self.not_required_if
                          ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        not_required_true = ctx.params.get(self.not_required_if)

        if not_required_true:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with `%s`" % (
                        self.name, self.not_required_if))
            else:
                self.prompt = None
                self.required = False

        return super(NotRequiredIf, self).handle_parse_result(ctx, opts, args)


@click.group()
def piggy():
    pass


@piggy.command()
@click.option('-path', 'path', prompt='Path', required=True, help='File path to your external drive')
@click.option('-region', 'aws_region', prompt='AWS Region', required=True, help='AWS region code')
@click.option('-id', 'aws_access_key_id', prompt='AWS Access Key ID', required=True, help='AWS access key ID')
@click.option('-key', 'aws_secret_access_key', prompt='AWS Secret Access Key', required=True, help='AWS secret Access Key')
@click.option('-customer-ca-key-password', 'customer_ca_key_password', prompt='Customer CA Key Password', required=True, help='User generated, 7-32 digits')
@click.option('-crypto-officer-password', 'crypto_officer_password', prompt='Crypto Officer Password', required=True, help='User generated password, 7-32 digits')
@click.option('-crypto-user-username', 'crypto_user_username', prompt='Crypto User Username', required=True, help='User generate username')
@click.option('-crypto-user-password', 'crypto_user_password', prompt='Crypto User Password', required=True, help='User generated password, 7-32 digits')
def setup(**kwargs):
    aws_access_key_id = kwargs['aws_access_key_id']
    aws_secret_access_key = kwargs['aws_secret_access_key']
    aws_region = kwargs['aws_region']

    ec2 = boto3.client('ec2', region_name=aws_region, aws_access_key_id=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key)
    cloudhsmv2 = boto3.client('cloudhsmv2', region_name=aws_region,
                              aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    resource = boto3.resource('ec2', region_name=aws_region,
                              aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    setup = Setup(
        ec2=ec2,
        cloudhsmv2=cloudhsmv2,
        resource=resource,
        base_path=kwargs['path'],
        aws_region=kwargs['aws_region'],
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        customer_ca_key_password=kwargs['customer_ca_key_password'],
        crypto_officer_password=kwargs['crypto_officer_password'],
        crypto_user_username=kwargs['crypto_user_username'],
        crypto_user_password=kwargs['crypto_user_password']
    )

    resp = setup.run()
    data = resp.get('data')
    if data is None:
        click.secho(resp['error'], fg='red')
    else:
        click.echo()
        click.secho(
            f"AWS cluster: {data['cluster_id']} and all associated resources have been created.", fg='green')
        click.echo()
        click.secho(
            "A folder with the files needed to access the cluster has been created on your external Piggy drive.", fg='green')
        click.echo()
        click.secho(
            "Piggy status is awake and available to create address by running piggy address create.", fg='green')
        click.echo()
        click.secho(
            "Run piggy status -sleep whenever your done using AWS CloudHSM to stop AWS from charging your account.", fg='red')
        click.echo()


@piggy.group()
def credentials():
    pass


# @credentials.command()
# @click.option('-path', 'path', type=click.Path(), prompt='Path', required=True)
# @click.option('-region', 'aws_region', prompt='AWS Region', required=True)
# @click.option('-ssh_key_name', 'ssh_key_name', prompt='SSH Key Name', required=True)
# @click.option('-cluster_id', 'cluster_id', prompt='Cluster ID', required=True)
# @click.option('-instance_id', 'instance_id', prompt='Instance ID', required=True)
# @click.option('-aws_access_key_id', 'aws_access_key_id', prompt='AWS Access Key ID', required=True)
# @click.option('-aws_secret_access_key', 'aws_secret_access_key', prompt='AWS Secret Access Key', required=True)
# @click.option('-customer_ca_key_password', 'customer_ca_key_password', prompt='Customer CA Key Password', required=True)
# @click.option('-crypto_officer_password', 'crypto_officer_password', prompt='Crypto Officer Password', required=True)
# @click.option('-crypto_user_username', 'crypto_user_username', prompt='Crypto User Username', required=True)
# @click.option('-crypto_user_password', 'crypto_user_password', prompt='Crypto User Password', required=True)
# def create(**kwargs):
#     credentials = CredentialsController()
#     resp = credentials.create(**kwargs)
#     click.echo()
#     click.secho(resp, fg='green')
#     click.echo()


# @credentials.command()
# @click.option('-ssh_key_name', 'ssh_key_name', required=False)
# @click.option('-aws-access-key-id', 'aws_access_key_id', required=False)
# @click.option('-aws-secret-access-key', 'aws_secret_access_key', required=False)
# @click.option('-crypto-officer-password', 'crypto_officer_password', required=False)
# @click.option('-crypto-user-username', 'crypto_user_username', required=False)
# @click.option('-crypto-user-password', 'crypto_user_password', required=False)
# @click.option('-creds', 'credentials_file_path', type=click.Path(), required=False)
# @creds
# def update(credentials, **kwargs):
#     update_dict = {}
#     for key, value in kwargs.items():
#         if bool(value):
#             update_dict[key] = value

#     resp = credentials.update(
#         credentials_file_path=credentials.credentials_file_path, **update_dict)

#     click.echo()
#     click.secho(resp.data, fg='green')
#     click.echo()


@piggy.command()
@click.option('-creds', 'credentials_file_path', type=click.Path(), required=False)
@click.option('-sleep', 'action', flag_value='sleep', default=False)
@click.option('-wake', 'action', flag_value='wake', default=False)
@creds
def status(credentials, action):
    status = StatusController(credentials=credentials)

    if action == 'wake':
        click.echo()
        if click.confirm(click.style('Are you sure you want to wake the pig, starting an HSM costs money?', fg='red')):
            resp = status.wake()
            click.echo()
            click.secho(resp, fg='green')
            click.echo()
    elif action == 'sleep':
        click.echo()
        if click.confirm(click.style('Are you sure you want to put the pig to sleep?', fg='red')):
            resp = status.sleep()
            click.echo()
            click.secho(resp, fg='green')
            click.echo()
    else:
        resp = status.show()
        click.echo()
        click.secho(resp, fg='green')
        click.echo()


@piggy.group()
def address():
    pass


@address.command()
@click.option('-creds', 'credentials_file_path', type=click.Path(), required=False)
@creds
def list(credentials):
    controller = AddressController(credentials=credentials)
    resp = controller.index()
    click.echo('')
    for address in resp['data']['addresses']:
        if address.spent is True:
            color = 'red'
        elif address.confirmed_balance > 0:
            color = 'green'
        else:
            color = 'blue'

        click.secho(
            f"id: {address.id}, address: {address.address}, confirmed_balance: {address.confirmed_balance}, spent: {address.spent}", fg=color)
    click.echo()


@address.command()
@click.option('-creds', 'credentials_file_path', type=click.Path(), required=False)
@creds
@check_status
def create(credentials):
    controller = AddressController(credentials=credentials)
    resp = controller.create()
    address = resp['data']['address']
    click.echo()
    click.secho(f'id: {address.id}', fg='green')
    click.secho(f'address: {address.address}', fg='green')
    click.secho(
        f'confirmed_balance: {address.confirmed_balance}', fg='green')
    click.secho(f'spent: {address.spent}', fg='green')
    click.echo()
    click.secho(f'public_key_handle: {address.pub_key_handle}', fg='green')
    click.secho(
        f'private_key_handle: {address.private_key_handle}', fg='green')
    click.echo()
    click.secho('public_key_pem: ', fg='green')
    click.secho(address.pub_key_pem, fg='green')
    click.echo()


@address.command()
@click.option('-creds', 'credentials_file_path', type=click.Path(), required=False)
@click.option('-id', 'id', prompt='Address ID', required=True)
@creds
def show(credentials, id):
    controller = AddressController(credentials=credentials)
    resp = controller.show(id=id)
    address = resp['data']['address']

    click.echo()
    click.secho(f'id: {address.id}', fg='green')
    click.secho(f'address: {address.address}', fg='green')
    click.secho(
        f'confirmed_balance: {address.confirmed_balance}', fg='green')
    click.secho(f'spent: {address.spent}', fg='green')
    click.echo()
    click.secho(f'public_key_handle: {address.pub_key_handle}', fg='green')
    click.secho(
        f'private_key_handle: {address.private_key_handle}', fg='green')
    click.echo()
    click.secho('public_key_pem: ', fg='green')
    click.secho(address.pub_key_pem, fg='green')
    click.echo()
    click.secho('txrefs:', fg='green')
    click.secho(address.txrefs, fg='green')
    click.echo()


@address.command()
@click.option('-id', 'id', prompt='Address ID', required=True)
@click.option('-creds', 'credentials_file_path', type=click.Path(), required=False)
@creds
def update(credentials, id):
    controller = AddressController(credentials=credentials)
    resp = controller.update(id=id)
    address = resp['data']['address']

    click.echo()
    click.secho(f'id: {address.id}', fg='green')
    click.secho(f'address: {address.address}', fg='green')
    click.secho(
        f'confirmed_balance: {address.confirmed_balance}', fg='green')
    click.secho(f'spent: {address.spent}', fg='green')
    click.echo()
    click.secho(f'public_key_handle: {address.pub_key_handle}', fg='green')
    click.secho(
        f'private_key_handle: {address.private_key_handle}', fg='green')
    click.echo()
    click.secho('public_key_pem: ', fg='green')
    click.secho(address.pub_key_pem, fg='green')
    click.echo()
    click.secho('txrefs:', fg='green')
    click.secho(address.txrefs, fg='green')
    click.echo()


@piggy.command()
@click.option('-all', 'all', is_flag=True, required=True, prompt="Send recipient all the BTC in address", cls=NotRequiredIf, not_required_if='partial')
@click.option('-some', 'partial', is_flag=True)
@click.option('-from', 'address_id', prompt='Sending Address ID', required=True)
@click.option('-to', 'recipient', prompt='Recipient Addreess', required=True)
@click.option('-fee', 'fee', type=click.INT, prompt='Mining Fee', required=True)
@click.option('-qty', 'value', type=click.INT, prompt='Quantity to send',  cls=NotRequiredIf, not_required_if='all')
@click.option('-change', 'change_address', required=True, prompt='Change address',
              cls=NotRequiredIf, not_required_if='all')
@click.option('-creds', 'credentials_file_path', type=click.Path(), required=False)
@creds
@check_status
def send(credentials, address_id, recipient, all, partial, fee, value, change_address):
    controller = TxController(credentials=credentials)
    valid = controller.validate(address_id=address_id, recipient=recipient,
                                all=all, fee=fee, value=value, change_address=change_address)

    if valid.get('error') is not None:
        click.echo()
        click.secho(f"Danger Will Robinson! {valid['error']}", fg="red")
        click.echo()

    elif all:
        click.echo()
        click.secho('Transation Details:', fg='green')
        click.echo()
        click.secho(
            f"Address {valid['address'].address} will send:", fg='green')
        click.secho(
            f"  * {valid['value']} SATs to {valid['recipient']}, and", fg='green')
        click.secho(f"  * pay a {fee} SATs mining fee.", fg='green')
        click.echo()

        if click.confirm('Confirm details'):
            tx_hex = controller.create(**valid)

            click.echo()
            click.secho('Raw Tx Hex:', fg='green')
            click.echo()
            click.secho(tx_hex, fg='green')
            click.echo()
    else:
        click.echo()
        click.secho('Transation Details:', fg='green')
        click.echo()
        click.secho(
            f"Address {valid['address'].address} will sends:", fg='green')
        click.secho(
            f"  * {valid['value']} SATs to {valid['recipient']},", fg='green')
        click.secho(
            f"  * {valid['change']} SATs to {valid['change_address']}, and", fg='green')
        click.secho(f"  * pay a {fee} SATs mining fee.", fg='green')
        click.echo()

        if click.confirm('Confirm details'):
            tx_hex = controller.create(**valid)

            click.echo()
            click.secho('Raw Tx Hex:', fg='green')
            click.secho(tx_hex, fg='green')
            click.echo()


@piggy.command()
@click.option('-creds', 'credentials_file_path', type=click.Path(), required=False)
@creds
def destroy(credentials):
    tf = Tf(region=credentials.data['aws_region'],
            ssh_key_name=credentials.data['ssh_key_name'],
            aws_access_key_id=credentials.data['aws_access_key_id'],
            aws_secret_access_key=credentials.data['aws_secret_access_key'])

    click.echo()
    click.secho('Piggy will destroy the following:', fg='green')
    click.echo()
    click.secho(
        f"  - AWS Cluster {credentials.data['cluster_id']}, ", fg='green')
    click.secho(
        f"  - AWS EC2 Instance {credentials.data['instance_id']}, and ", fg='green')
    click.secho(f"  - The associated AWS VPC and Subnets.", fg='green')
    click.echo()

    if click.confirm(click.style('Confirm you want to delete / destroy the above?', fg='red')):
        if click.confirm(click.style("Are you sure, this cannot be undone?", fg='red')):
            try:
                initialized = tf.init()
                assert initialized, 'Terraform initialize failed'
                destroyed = tf.destroy()
                assert destroyed, 'Terraform destroy failed'
                tf._clean_up()

            except Exception as e:
                click.secho(e.args[0], fg='red')
        else:
            pass
    else:
        pass
