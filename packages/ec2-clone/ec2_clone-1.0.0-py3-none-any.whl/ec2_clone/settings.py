import json
import logging

import ec2_clone as ec
import ec2_clone.util as util


def prepare_kwargs(instance, ami, overrides, aws):
    """
    Generate instance settings.
    Currently only generates tags for instance.
    Tags for volumes are manually copied across as they may differ for each volume.
    """
    log = logging.getLogger(__name__)
    try:
        if overrides.encrypt_root_volume or overrides.enable_hibernation:
            ami = util.ami.encrypt_root_volume(ami, overrides.kms_key_id)

        if overrides.root_volume_size:
            ami = util.ami.increase_root_volume(ami, set=overrides.root_volume_size)

        elif overrides.enable_hibernation:
            ram_size = ec.RAM_SIZE[instance.size]
            ami = util.ami.increase_root_volume(ami, increase=max(ram_size, 4))

        tag_spec = util.get_tag_specifications(instance.tags, "instance")

        nics = util.instance.get_nics(
            instance, overrides.private_ip, overrides.ipv4_prefix
        )

        instance.metadata_options.pop("State")
        kwargs = {
            # Without ovderrides
            "MaxCount": 1,
            "MinCount": 1,
            "TagSpecifications": tag_spec,
            "ImageId": ami.image_id,
            "KeyName": instance.key_name,
            "Placement": instance.placement,
            "MetadataOptions": instance.metadata_options,
            "EnclaveOptions": instance.enclave_options,
            "MaintenanceOptions": instance.maintenance_options,
            "CapacityReservationSpecification": instance.capacity_reservation_specification,
            "Monitoring": {
                "Enabled": True if instance.monitoring["State"] == "enabled" else False
            },
            "EbsOptimized": instance.ebs_optimized,
            "PrivateDnsNameOptions": instance.private_dns_name_options,
            "InstanceInitiatedShutdownBehavior": instance._i.describe_attribute(
                Attribute="instanceInitiatedShutdownBehavior"
            )["InstanceInitiatedShutdownBehavior"]["Value"],
            "DisableApiTermination": instance._i.describe_attribute(
                Attribute="disableApiTermination"
            )["DisableApiTermination"]["Value"],
            "InstanceInitiatedShutdownBehavior": instance._i.describe_attribute(
                Attribute="instanceInitiatedShutdownBehavior"
            )["InstanceInitiatedShutdownBehavior"]["Value"],
            # With overrides
            "BlockDeviceMappings": ami.ebs_mappings,
            "HibernationOptions": {
                "Configured": overrides.enable_hibernation
                if overrides.enable_hibernation
                else instance.hibernation_options["Configured"],
            },
            "InstanceType": overrides.instance_type
            if overrides.instance_type
            else instance.instance_type,
            "NetworkInterfaces": nics,
        }
        if instance.stop_protection == 1:
            kwargs["DisableApiStop"] = True

        if instance.licenses:
            kwargs["LicenseSpecifications"] = instance.licenses

        cpu_credit_spec = util.instance.get_credit_specification(instance, aws)
        if cpu_credit_spec:
            kwargs["CreditSpecification"] = cpu_credit_spec

        market_options = util.instance.get_instance_market_options(instance, aws)
        if market_options:
            kwargs["InstanceMarketOptions"] = market_options

        cpu_options = util.instance.get_cpu_options(instance, aws)
        if cpu_options:
            kwargs["CpuOptions"] = cpu_options

        elastic_gpus = util.instance.get_elastic_gpu_specifications(instance, aws)
        if elastic_gpus:
            kwargs["ElasticGpuSpecifications"] = elastic_gpus

        inference_accelerators = util.instance.get_elastic_inference_specifications(
            instance, aws
        )
        if inference_accelerators:
            kwargs["ElasticInferenceAccelerators"] = inference_accelerators

        instance_profile = util.instance.get_instance_profile(instance)
        if instance_profile:
            kwargs["IamInstanceProfile"] = instance_profile

        return kwargs
    except Exception as e:
        log.error(f"Unable to generate instance settings: {e}")
        return 1


def rename(i_settings, name):
    log = logging.getLogger(__name__)
    for tag_spec in i_settings["TagSpecifications"]:
        if tag_spec["ResourceType"] == "instance":
            for tag in tag_spec["Tags"]:
                if tag["Key"] == "Name":
                    tag["Value"] = name
                    return True

    log.error("Failed to rename new instance")
    return False


def load(path=ec.SETTINGS_FILE):
    """
    Load instance settings.
    """
    log = logging.getLogger(__name__)
    try:
        with open(path, "r") as f:
            i_settings = json.load(f)
            return i_settings
    except Exception as e:
        log.error(f"Error loading settings: {e}")
        return False


def dump(settings, path=ec.SETTINGS_FILE):
    """
    Dump instance settings.
    """

    log = logging.getLogger(__name__)
    log.info(f"Saving settings to: {path}")
    try:
        with open(path, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        log.error(f"Error saving settings: {e}")
        return False

    return True
