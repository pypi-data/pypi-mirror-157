import ipaddress
import logging
from dataclasses import dataclass

import click

import ec2_clone.util as util
from ec2_clone.aws import Aws


class BaseCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.extend(
            [
                click.Option(
                    ("--log-level", "-l"),
                    help="Log level as string",
                    default="INFO",
                    type=click.Choice(
                        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                    ),
                ),
                click.Option(
                    ("--yes",), is_flag=True, help="Assume yes to all prompts"
                ),
            ]
        )


class CommonArgs(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.extend(
            [
                click.Option(
                    ("--region", "-r"),
                    required=True,
                    type=str,
                    help="Region string in long format, e.g. eu-west-1",
                ),
                click.Option(
                    ("--instance-id", "-i"), required=True, type=str, help="Instance ID"
                ),
                click.Option(("--ami-name",), help="Name used when creating new AMI"),
                click.Option(
                    ("--ami-suffix",),
                    help="Suffix used when creating new AMI. Full name will be \{instance-name\}\{suffix\}",
                ),
            ]
        )


class OverrideInstanceArgs(CommonArgs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.extend(
            [
                click.Option(
                    ("--ami-id", "-a"),
                    type=str,
                    help="AMI to use for new instances instead of creating a new one",
                ),
                click.Option(
                    ("--instance-type",),
                    help="Override instance type",
                ),
                click.Option(
                    ("--root-volume-size",),
                    type=int,
                    help="Size of new instances root volume in GB. If not set, root volume will be increased based on instance type to accomodate RAM for hibernation",
                ),
                click.Option(
                    ("--encrypt-root-volume",),
                    type=bool,
                    is_flag=True,
                    help="Encrypt root volume",
                ),
                click.Option(
                    ("--kms-key-id",),
                    type=int,
                    help="KMS key ID to use for root volume encryption. AWS EBS default key used if not specified",
                ),
                click.Option(
                    ("--enable-hibernation",),
                    is_flag=True,
                    help="Increase root volume size, encrypt root volume and enable hibernation",
                ),
            ]
        )

    @dataclass
    class Overrides:
        """
        Override instance settings.
        """

        ami_id: str = None
        instance_type: str = None
        private_ip: str = None
        ipv4_prefix: str = None
        root_volume_size: str = None
        encrypt_root_volume: bool = False
        kms_key_id: str = None
        enable_hibernation: str = None


def validate_options(kwargs):
    log = logging.getLogger(__name__)
    logging.basicConfig(level=kwargs["log_level"])
    log.info("Starting")

    instance_suffix = "instance_suffix" in kwargs and kwargs["instance_suffix"]
    instance_name = "instance_name" in kwargs and kwargs["instance_name"]
    if instance_suffix and instance_name:
        log.error("Cannot specify both --instance-suffix and --instance-name")
        raise ValueError

    template_suffix = "template_suffix" in kwargs and kwargs["template_suffix"]
    template_name = "template_name" in kwargs and kwargs["template_name"]
    if template_suffix and template_name:
        log.error("Cannot specify both --template-suffix and --template-name")
        raise ValueError

    ami_suffix = "ami_suffix" in kwargs and kwargs["ami_suffix"]
    ami_name = "ami_name" in kwargs and kwargs["ami_name"]
    ami_id = "ami_id" in kwargs and kwargs["ami_id"]
    if (ami_id and (ami_name or ami_suffix)) or (ami_name and ami_suffix):
        log.error("Only one of --ami-id, --ami-name, --ami-suffix can be specified")
        raise ValueError

    if "settings_input" in kwargs and kwargs["settings_input"]:
        if (
            kwargs["ami_id"]
            or kwargs["instance_type"]
            or ("private_ip" in kwargs and kwargs["private_ip"])
            or kwargs["root_volume_size"]
            or kwargs["kms_key_id"]
            or kwargs["encrypt_root_volume"]
        ):
            log.error(
                "Cannot use --settings-input with --ami-id, --instance-type, --private-ip, --root-volume-size, or --kms-key-id"
            )
            log.info("Please set these values in the settings file")
            raise ValueError

    if "private_ip" in kwargs and kwargs["private_ip"]:
        try:
            ipaddress.ip_address(kwargs["private_ip"])
        except ValueError:
            log.error(f"Invalid private IP address: {kwargs['private_ip']}")
            raise ValueError
        if not util.vpc.ip_available(instance.subnet_id, kwargs["private_ip"], "", aws):
            return 1, None
    else:
        kwargs["private_ip"] = None

    if "ipv4_prefix" in kwargs and kwargs["ipv4_prefix"]:
        try:
            ipaddress.ip_network(kwargs["ipv4_prefix"])
        except ValueError:
            log.error(f"Invalid private IP prefix: {kwargs['ipv4_prefix']}")
            raise ValueError
        if not util.vpc.ip_prefix_available(
            instance.subnet_id, kwargs["ipv4_prefix"], "", aws
        ):
            return 1, None
    else:
        kwargs["ipv4_prefix"] = None

    try:
        aws = Aws(kwargs["region"])
    except Exception as e:
        log.error(f"Unable to initiate AWS clients: {e}")
        raise ValueError

    instance = util.instance.get(kwargs["instance_id"], aws)
    if not instance:
        log.error(f"Instance: {kwargs['instance_id']} not found in {aws.region}")
        raise ValueError
    if "Name" not in util.get_tag_dict(instance.tags):
        log.warning("Please tag your instance with a Name tag")
        raise ValueError

    return aws, instance
