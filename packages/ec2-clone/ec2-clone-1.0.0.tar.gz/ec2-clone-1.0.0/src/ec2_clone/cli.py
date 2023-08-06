import click

import ec2_clone as ec
import ec2_clone.args as args
import ec2_clone.clone as clone
import ec2_clone.settings as settings


@click.group()
def main():
    """Utility for cloning and modifying EC2 instances"""
    return 0


@main.command(cls=args.CommonArgs)
def create_ami(**kwargs):
    """Create AMI from source instance"""
    try:
        aws, instance = args.validate_options(kwargs)
    except ValueError:
        return 1

    ami, _ = clone.create_ami(aws, instance, **kwargs)
    return ami


@main.command(cls=args.OverrideInstanceArgs)
@click.option(
    "--output-file",
    "-o",
    default=ec.SETTINGS_FILE,
    help="Output file when dumping settings",
)
@click.option("--private-ip", help="Override instance private IP")
@click.option("--ipv4-prefix", help="Override instance IPv4 prefix")
def create_settings_json(**kwargs):
    """Create instance JSON file from source instance"""
    try:
        aws, instance = args.validate_options(kwargs)
    except ValueError:
        return 1

    i_settings, _ = clone.create_settings(aws, instance, **kwargs)
    if type(i_settings) == int:
        return 1

    settings.dump(i_settings, kwargs["output_file"])
    return 0


@main.command(cls=args.OverrideInstanceArgs)
@click.option("--private-ip", type=str, help="Instance settings input file")
@click.option("--ipv4-prefix", help="Override instance IPv4 prefix")
@click.option("--template-name", help="Name used when creating launch template")
@click.option(
    "--template-suffix",
    help="Suffix used when creating launch template. Full name will be \{instance-name\}\{suffix\}",
)
def create_launch_template(**kwargs):
    """Create launch template from source instance"""
    try:
        aws, instance = args.validate_options(kwargs)
    except ValueError:
        return 1

    return clone.create_launch_template(aws, instance, **kwargs)


@main.command(cls=args.OverrideInstanceArgs)
@click.option("--settings-input", type=str, help="Instance settings input file")
def replace_instance(**kwargs):
    """Clone instance and terminate the source instance"""
    try:
        aws, instance = args.validate_options(kwargs)
    except ValueError:
        return 1

    return clone.replace_instance(aws, instance, **kwargs)


"""
TODO: Clone Instance improvements
- Don't move EIP
- Don't move nics
- Create new EIP
"""


@main.command(cls=args.OverrideInstanceArgs)
@click.option("--private-ip", help="Override instance private IP")
@click.option("--ipv4-prefix", help="Override instance IPv4 prefix")
@click.option("--settings-input", type=str, help="Instance settings input file")
@click.option("--instance-name", help="Name used when creating new instance")
@click.option(
    "--instance-suffix",
    help="Suffix used when creating new instance. Full name will be \{instance-name\}\{suffix\}",
)
def clone_instance(**kwargs):
    """Clone instance without terminating the source instance"""
    try:
        aws, instance = args.validate_options(kwargs)
    except ValueError:
        return 1

    return clone.clone_instance(aws, instance, **kwargs)
