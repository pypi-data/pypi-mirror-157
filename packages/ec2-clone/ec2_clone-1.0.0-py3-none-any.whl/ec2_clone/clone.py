import logging

import ec2_clone as ec
import ec2_clone.args as args
import ec2_clone.hibernate as hibernate
import ec2_clone.relaunch as relaunch
import ec2_clone.settings as settings
import ec2_clone.util as util
from ec2_clone.rollback import Rollback


def create_ami(aws, instance, **kwargs):
    """Create AMI from source instance"""
    log = logging.getLogger(__name__)

    if kwargs["yes"]:
        ec.YES = True

    rollback = Rollback(instance, aws)
    try:
        rollback.is_running = True if instance.state["Name"] != "stopped" else False
        util.instance.stop(instance)

        tags = util.get_tag_dict(instance.tags)
        suffix = kwargs["ami_suffix"] if kwargs["ami_suffix"] else "-CLONE"
        ami_name = kwargs["ami_name"] if kwargs["ami_name"] else tags["Name"] + suffix
        ami = util.ami.create(instance, ami_name, aws, tags=tags)

        if not ami:
            rollback.roll()
            return False, None
        rollback.ami = ami

        return ami, rollback
    except Exception as e:
        log.error(f"Unexpected Failure while getting image: {e}")
        rollback.roll()
        return False, None


def create_settings(aws, instance, **kwargs):
    """Create instance JSON file from source instance"""
    if kwargs["yes"]:
        ec.YES = True

    overrides = args.OverrideInstanceArgs.Overrides(
        kwargs["ami_id"],
        kwargs["instance_type"],
        kwargs["private_ip"],
        kwargs["ipv4_prefix"],
        kwargs["root_volume_size"],
        kwargs["encrypt_root_volume"],
        kwargs["kms_key_id"],
        kwargs["enable_hibernation"],
    )

    if overrides.enable_hibernation:
        res = hibernate.validate_instance(instance, overrides.instance_type, aws)
        if res != 0:
            return res, None

    if overrides.ami_id:
        ami = util.ami.get(overrides.ami_id, aws)
        rollback = Rollback(instance, aws)
    else:
        ami, rollback = create_ami(aws, instance, **kwargs)

    if not ami:
        return 1, None

    return settings.prepare_kwargs(instance, ami, overrides, aws), rollback


def create_launch_template(aws, instance, **kwargs):
    """Create launch template from source instance"""
    log = logging.getLogger(__name__)

    if kwargs["yes"]:
        ec.YES = True

    i_settings, rollback = create_settings(aws, instance, **kwargs)
    if type(i_settings) == int:
        return i_settings

    suffix = "-CLONE-TEMPLATE"
    suffix = kwargs["template_suffix"] if kwargs["template_suffix"] else suffix
    name = util.get_tag_dict(instance.tags)["Name"] + suffix
    name = kwargs["template_name"] if kwargs["template_name"] else name

    try:
        log.info("Creating launch template")
        launch_template_data = i_settings
        launch_template_data.pop("MaxCount")
        launch_template_data.pop("MinCount")
        aws.client.create_launch_template(
            LaunchTemplateName=name, LaunchTemplateData=launch_template_data
        )
        log.info("Launch Template Generated")
        return 0
    except Exception as e:
        log.error(f"Unable to create launch template: {e}")
        rollback.roll()
        return 1


def replace_instance(aws, instance, **kwargs):
    """Clone instance and terminate the source instance"""
    log = logging.getLogger(__name__)

    if kwargs["yes"]:
        ec.YES = True

    if kwargs["settings_input"]:
        log.info("Using settings from file")
        i_settings = settings.load(kwargs["settings_input"])
        rollback = Rollback(instance, aws)
    else:
        i_settings, rollback = create_settings(aws, instance, **kwargs)
        if type(i_settings) == int:
            return i_settings

    if not util.instance.dry_run(i_settings, aws):
        rollback.roll()
        return 1

    return relaunch.replace_instance(instance, i_settings, rollback, aws)


def clone_instance(aws, instance, **kwargs):
    """Clone instance without terminating the source instance"""
    log = logging.getLogger(__name__)

    if kwargs["yes"]:
        ec.YES = True

    existing_primary_nic = util.instance.get_primary_nic(
        instance.network_interfaces_attribute
    )
    if not kwargs["private_ip"]:
        kwargs["private_ip"] = util.vpc.generate_different_ip(
            existing_primary_nic["PrivateIpAddress"], instance.subnet_id, aws
        )
        if not kwargs["private_ip"]:
            return 1
        log.info(f"Setting cloned instance private IP to: {kwargs['private_ip']}")
    if not kwargs["ipv4_prefix"] and "Ipv4Prefixes" in existing_primary_nic:
        kwargs["ipv4_prefix"] = util.vpc.generate_different_prefix(
            existing_primary_nic["Ipv4Prefixes"][0]["Ipv4Prefix"],
            instance.subnet_id,
            aws,
        )
        if not kwargs["ipv4_prefix"]:
            return 1
        log.info(f"Setting cloned instance ipv4 prefix to: {kwargs['ipv4_prefix']}")

    if kwargs["settings_input"]:
        log.info("Using settings from file")
        i_settings = settings.load(kwargs["settings_input"])
        rollback = Rollback(instance, aws)
    else:
        i_settings, rollback = create_settings(aws, instance, **kwargs)
        if type(i_settings) == int:
            return i_settings

    suffix = "-CLONE"
    suffix = kwargs["instance_suffix"] if kwargs["instance_suffix"] else suffix
    name = util.get_tag_dict(instance.tags)["Name"] + suffix
    name = kwargs["instance_name"] if kwargs["instance_name"] else name
    if not settings.rename(i_settings, name):
        rollback.roll()
        return 1

    if not util.instance.dry_run(i_settings, aws):
        rollback.roll()
        return 1

    primary_nic = util.instance.get_primary_nic(i_settings["NetworkInterfaces"])
    if util.vpc.ip_conflict(primary_nic, "", aws):
        return 1

    return relaunch.launch_new_instance(instance, i_settings, rollback, aws)
