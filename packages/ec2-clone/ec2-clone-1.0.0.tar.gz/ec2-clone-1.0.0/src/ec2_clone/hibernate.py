import logging

import ec2_clone as ec
import ec2_clone.util as util


def validate_instance(instance, instance_type, aws):
    log = logging.getLogger(__name__)
    log.info(f"Validating hibernation can be enabled for instance: {instance.instance_id}")

    instance_type_details = aws.client.describe_instance_types(
        InstanceTypes=[instance_type if instance_type else instance.instance_type]
    )["InstanceTypes"][0]

    if instance_type_details["HibernationSupported"] == False:
        log.error(
            f"Instance type: {instance.instance_type} does not support hibernation in region: {aws.region}"
        )
        return 2

    if instance.root_device_type != "ebs":
        log.error("Instance root volume is not EBS backed")
        return 2

    root_volume = util.instance.get_root_ebs_volume(instance)
    if not root_volume:
        return 1

    if root_volume.volume_type not in ec.HIBERNATION_SUPPORTED_VOLUME_TYPES:
        log.error(f"Root volume type {root_volume['VolumeType']} is not supported")
        return 2

    if instance.platform == "Windows":
        log.error("Windows instances are not supported")
        if instance.size == "nano":
            log.warning("Recommended minimum size for windows instances is micro")
            if not util.confirm("Continue with instance size nano? (y/n)"):
                return 1

        if instance_type_details["MemoryInfo"]["SizeInMiB"] > 16384:
            log.error("Maximum memory for Windows instances is 16GB")
            return 2

        if instance.virtualization_type != "hvm":
            log.warning(
                "Windows instances must be HVM. This script is not configured to handle PV instances. Please manually override settings as required."
            )
            if not util.confirm("Are necessary settings overrides configured? (y/n): "):
                return 2

    else:
        if instance_type_details["MemoryInfo"]["SizeInMiB"] > 153600:
            log.error("Maximum memory for Linuex instances is 150GB")
            return 2

    return 0
