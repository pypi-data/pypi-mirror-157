import ipaddress
import logging

import ec2_clone.util as util
from botocore.exceptions import ClientError


class MutableInstance:
    def _init(self):
        type = self._i.instance_type.split(".")

        self.ebs_volumes_dict = get_volumes_by_device_name(self._i, self.aws)
        self.ebs_volume_tags = {
            dev_name: util.remove_aws_tags(volume.tags)
            for dev_name, volume in self.ebs_volumes_dict.items()
            if volume.tags
        }

        self.size = type[1]
        self.type = type[0]

        self.ami_launch_index = self._i.ami_launch_index
        self.architecture = self._i.architecture
        self.block_device_mappings = self._i.block_device_mappings
        self.boot_mode = self._i.boot_mode
        self.capacity_reservation_id = self._i.capacity_reservation_id
        self.capacity_reservation_specification = (
            self._i.capacity_reservation_specification
        )
        self.client_token = self._i.client_token
        self.cpu_options = self._i.cpu_options
        self.ebs_optimized = self._i.ebs_optimized
        self.elastic_gpu_associations = self._i.elastic_gpu_associations
        self.elastic_inference_accelerator_associations = (
            self._i.elastic_inference_accelerator_associations
        )
        self.ena_support = self._i.ena_support
        self.enclave_options = self._i.enclave_options
        self.hibernation_options = self._i.hibernation_options
        self.hypervisor = self._i.hypervisor
        self.iam_instance_profile = self._i.iam_instance_profile
        self.image_id = self._i.image_id
        self.instance_id = self._i.instance_id
        self.lifecycle = self._i.instance_lifecycle
        self.instance_type = self._i.instance_type
        self.ipv6_address = self._i.ipv6_address
        self.kernel_id = self._i.kernel_id
        self.key_name = self._i.key_name
        self.launch_time = self._i.launch_time
        self.licenses = self._i.licenses
        self.maintenance_options = self._i.maintenance_options
        self.metadata_options = self._i.metadata_options
        self.monitoring = self._i.monitoring
        self.network_interfaces = self._i.network_interfaces
        self.network_interfaces_attribute = self._i.network_interfaces_attribute
        self.outpost_arn = self._i.outpost_arn
        self.placement = self._i.placement
        self.platform = self._i.platform
        self.platform_details = self._i.platform_details
        self.private_dns_name = self._i.private_dns_name
        self.private_dns_name_options = self._i.private_dns_name_options
        self.private_ip_address = self._i.private_ip_address
        self.product_codes = self._i.product_codes
        self.public_dns_name = self._i.public_dns_name
        self.public_ip_address = self._i.public_ip_address
        self.ramdisk_id = self._i.ramdisk_id
        self.root_device_name = self._i.root_device_name
        self.root_device_type = self._i.root_device_type
        self.security_groups = self._i.security_groups
        self.source_dest_check = self._i.source_dest_check
        self.spot_instance_request_id = self._i.spot_instance_request_id
        self.sriov_net_support = self._i.sriov_net_support
        self.state = self._i.state
        self.state_reason = self._i.state_reason
        self.state_transition_reason = self._i.state_transition_reason
        self.subnet_id = self._i.subnet_id
        self.tags = self._i.tags
        self.tpm_support = self._i.tpm_support
        self.usage_operation = self._i.usage_operation
        self.usage_operation_update_time = self._i.usage_operation_update_time
        self.virtualization_type = self._i.virtualization_type
        self.vpc_id = self._i.vpc_id

    def __init__(self, instance, aws):
        self._i = instance
        self.aws = aws
        self.stop_protection = False
        self._init()

    def update(self):
        self._i.load()

    def overwrite(self):
        self._i.load()
        self._init()

    def __str__(self):
        return self.instance_id


def get(id, aws):
    log = logging.getLogger(__name__)

    try:
        reservations = aws.client.describe_instances(InstanceIds=[id])["Reservations"]
        if len(reservations) == 0 or len(reservations[0]["Instances"]) == 0:
            log.error("Instance with id {} not found".format(id))
            return None
        id = reservations[0]["Instances"][0]["InstanceId"]
        instance = aws.resource.Instance(id)
    except Exception as e:
        log.error(f"Error getting instance: {e}")
        return None

    if instance.state["Name"] == "terminated":
        return None

    return MutableInstance(instance, aws)


def get_by_name(name, aws):
    log = logging.getLogger(__name__)

    try:
        instances = aws.client.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": [name]}]
        )
        for reservation in instances["Reservations"]:
            for instance in reservation["Instances"]:
                if instance["State"]["Name"] == "terminated":
                    continue
                return MutableInstance(
                    aws.resource.Instance(instance["InstanceId"]), aws
                )
    except Exception as e:
        log.error(f"Error getting instance with tag:Name: {name} in {aws.region}: {e}")
        return None

    log.warning(f"No instance found with tag:Name {name} in {aws.region}")

    return None


def get_credit_specification(instance: MutableInstance, aws):
    log = logging.getLogger(__name__)
    if "t" not in instance.type.lower():
        return None

    try:
        spec = aws.client.describe_instance_credit_specifications(
            InstanceIds=[instance.instance_id]
        )
        if len(spec["InstanceCreditSpecifications"]) == 0:
            return {"CpuCredits": spec["InstanceCreditSpecifications"][0]["CpuCredits"]}
    except Exception as e:
        log.error(f"Unable to get credit specification for instance: {e}")
        return None


def get_instance_market_options(instance: MutableInstance, aws):
    log = logging.getLogger(__name__)
    if not instance.spot_instance_request_id:
        return None

    try:
        spot_request = aws.client.describe_spot_instance_requests(
            SpotInstanceRequestIds=[instance.spot_instance_request_id]
        )["SpotInstanceRequests"][0]

        market_options = {
            "MarketType": "spot",
        }
        spot_options = {}
        if "Type" in spot_request:
            spot_options["SpotInstanceType"] = spot_request["Type"]

        if "SpotPrice" in spot_request:
            spot_options["MaxPrice"] = spot_request["SpotPrice"]

        if "ValidUntil" in spot_request:
            spot_options["ValidUntil"] = spot_request["ValidUntil"]

        if "InstanceInterruptionBehavior" in spot_request:
            spot_options["InstanceInterruptionBehavior"] = spot_request[
                "InstanceInterruptionBehavior"
            ]

        market_options["SpotOptions"] = spot_options
        return market_options
    except Exception as e:
        log.error(f"Unable to gather instance market options for: {e}")
        return None


def get_cpu_options(instance: MutableInstance, aws):
    log = logging.getLogger(__name__)

    try:
        vcpu_info = aws.client.describe_instance_types(
            InstanceTypes=[instance.instance_type]
        )["InstanceTypes"][0]["VCpuInfo"]

        if "ValidCores" in vcpu_info and type(vcpu_info["ValidCores"]) is list:
            return instance.cpu_options

        return None
    except Exception as e:
        log.warning(
            f"Unable to gather cpu options for instance {instance.instance_id}: {e}"
        )
        return None


def get_elastic_gpu_specifications(instance: MutableInstance, aws):
    log = logging.getLogger(__name__)
    if not instance.elastic_gpu_associations:
        return None

    try:
        filters = [{"Name": "instance-id", "Values": [instance.instance_id]}]
        type = aws.client.describe_elastic_gpus(Filters=filters)["ElasticGpuSet"][0][
            "ElasticGpuType"
        ]
        return [{"Type": type}]
    except Exception as e:
        log.error(
            f"Unable to gather elastic GPU specifications for instance {instance.instance_id}: {e}"
        )
        return None


def get_elastic_inference_specifications(instance: MutableInstance, aws):
    log = logging.getLogger(__name__)

    if not instance.elastic_inference_accelerator_associations:
        return None

    try:
        types = {}
        filters = [{"name": "instance-id", "values": [instance.instance_id]}]
        for accelerator in aws.inference_client.describe_accelerators(filters=filters)[
            "acceleratorSet"
        ]:
            type = accelerator["acceleratorType"]
            if type in types:
                types[type] += 1
            else:
                types[type] = 1

        inference_accelerators = []
        for type, count in types.items():
            inference_accelerators.append({"Type": type, "Count": count})
        return inference_accelerators

    except Exception as e:
        log.error(
            f"Unable to gather elastic inference specifications for instance {instance.instance_id}: {e}"
        )
        return None


def get_instance_profile(instance: MutableInstance):
    log = logging.getLogger(__name__)

    if not instance.iam_instance_profile:
        return None

    try:
        return {"Arn": instance.iam_instance_profile["Arn"]}
    except Exception as e:
        log.error(
            f"Unable to gather instance profile for instance {instance.instance_id}: {e}"
        )
        return None


def get_primary_nic(interfaces):
    try:
        device_0 = lambda nic: nic["Attachment"]["DeviceIndex"] == 0
        return next(filter(device_0, interfaces), None)
    except:
        device_0 = lambda nic: nic["DeviceIndex"] == 0
        return next(filter(device_0, interfaces), None)


def get_primary_nic_config(instance: MutableInstance, private_ip, prefix):
    log = logging.getLogger(__name__)

    primary = get_primary_nic(instance.network_interfaces_attribute)
    if not primary:
        raise Exception("No primary network interface found")

    nic = {
        "DeviceIndex": 0,
        "DeleteOnTermination": primary["Attachment"]["DeleteOnTermination"],
        "Description": primary["Description"],
        "SubnetId": primary["SubnetId"],
        "InterfaceType": primary["InterfaceType"],
        # "AssociateCarrierIpAddress": primary["AssociateCarrierIpAddress"], // Not supported
    }
    if len(instance.security_groups) > 0:
        nic["Groups"] = [group["GroupId"] for group in instance.security_groups]

    if len("PrivateIpAddresses") > 0:
        ips = [
            {"Primary": ip["Primary"], "PrivateIpAddress": ip["PrivateIpAddress"]}
            for ip in primary["PrivateIpAddresses"]
        ]
        nic["PrivateIpAddresses"] = ips

    # TODO accept multiple values for PrivateIpAddresses
    if private_ip:
        for ip in nic["PrivateIpAddresses"]:
            if ip["Primary"]:
                ip["PrivateIpAddress"] = private_ip

    if prefix:
        nic["Ipv4Prefixes"] = [{"Ipv4Prefix": prefix}]
    else:
        if "Ipv4Prefixes" in primary and len(primary["Ipv4Prefixes"]) > 0:
            nic["Ipv4Prefixes"] = primary["Ipv4Prefixes"]

    # TODO support Ipv6Addresses
    # if len(primary["Ipv6Addresses"]) > 0:
    #     nic["Ipv6Addresses"] = primary["Ipv6Addresses"]

    # if len(primary["Ipv6Prefixes"]) > 0:
    #     nic["Ipv6Prefixes"] = primary["Ipv6Prefixes"]

    if "Association" in primary:
        if "CarrierIp" in primary["Association"]:
            log.warning(
                "Carrier IPs will not be transferred automatically, please transfer manually"
            )
        if "CustomerOwnedIp" in primary["Association"]:
            log.warning(
                "Customer Owned IPs will not be transferred automatically, please transfer manually"
            )

    return nic


def get_nics(instance: MutableInstance, private_ip, prefix):
    nics = [get_primary_nic_config(instance, private_ip, prefix)]
    if len(instance.network_interfaces) == 1:
        return nics

    for nic in instance.network_interfaces_attribute:
        if nic["Attachment"]["DeviceIndex"] == 0:
            continue
        nics.append(
            {
                "DeviceIndex": nic["Attachment"]["DeviceIndex"],
                "NetworkInterfaceId": nic["NetworkInterfaceId"],
            }
        )

    return nics


def ip_conflict_ip_addreses(nic, other):
    for ip in util.vpc.get_ips(nic):
        for other_ip in util.vpc.get_ips(other):
            if ip == other_ip:
                return True

    return False


def ip_conflict_prefixes(nic, other):
    for prefix in util.vpc.get_prefixes(nic):
        prefix = ipaddress.ip_network(prefix)
        for other_prefix in util.vpc.get_prefixes(other):
            other_prefix = ipaddress.ip_network(other_prefix)
            if prefix.overlaps(other_prefix):
                return True

    return False


def ip_conflict_ip_with_prefix(nic, other):
    for ip in util.vpc.get_ips(nic):
        for other_prefix in util.vpc.get_prefixes(other):
            other_prefix = ipaddress.ip_network(other_prefix)
            if ipaddress.ip_address(ip) in other_prefix:
                return True

    return False


def ip_conflict(nics: list):
    """
    Compares list of nics for ip conflicts

    Returns True if:
        - Any nics have matching private ip addresses
        - Any nics have overlapping prefixes
        - Any nic has an ip contained within a prefix from another nic
    """

    for i, nic in enumerate(nics):
        for j, other in enumerate(nics):
            if i == j:
                continue

            if nic["SubnetId"] != other["SubnetId"]:
                continue

            if ip_conflict_ip_addreses(nic, other):
                return True

            if ip_conflict_prefixes(nic, other):
                return True

            if ip_conflict_ip_with_prefix(nic, other):
                return True

            if ip_conflict_ip_with_prefix(other, nic):
                return True

    return False


def get_volumes_by_device_name(instance: MutableInstance, aws):
    log = logging.getLogger(__name__)

    try:
        return {
            mapping["DeviceName"]: aws.resource.Volume(mapping["Ebs"]["VolumeId"])
            for mapping in instance.block_device_mappings
            if "Ebs" in mapping
        }

    except Exception as e:
        log.error(f"Error getting volumes: {e}")
        return None


def get_root_ebs_volume(instance: MutableInstance):
    log = logging.getLogger()
    root_volume_id = list(
        filter(
            lambda x: x["DeviceName"] == instance.root_device_name,
            instance.block_device_mappings,
        )
    )[0]["Ebs"]["VolumeId"]

    try:
        root_volume = list(instance._i.volumes.filter(VolumeIds=[root_volume_id]))[0]
        return root_volume
    except Exception as e:
        log.error(f"Error getting root volume: {e}")
        return False


def rename(instance: MutableInstance, name):
    log = logging.getLogger(__name__)
    try:
        log.info(f"Renaming instance: {instance.instance_id} as: {name}")
        if not util.confirm():
            raise Exception("User aborted")
        instance._i.create_tags(Tags=[{"Key": "Name", "Value": name}])
    except Exception as e:
        log.error(f"Error renaming instance: {e}")
        return False

    return True


def dry_run(kwargs, aws):
    log = logging.getLogger(__name__)

    kwargs = kwargs.copy()
    kwargs["DryRun"] = True
    try:
        log.info(f"Attempting to dry run launch instance")
        aws.client.run_instances(**kwargs)

    except ClientError as e:
        if e.response["Error"]["Code"] == "DryRunOperation":
            log.info(f"Dry run successful")
            return True
        raise

    except Exception as e:
        log.error(f"Error attempting dry run: {e}")
        return False

    return False


def run(kwargs, aws):
    log = logging.getLogger(__name__)

    try:
        log.info("Launching new instance")
        if not util.confirm():
            raise Exception("User aborted")
        instance = aws.client.run_instances(**kwargs)
        instance_id = instance["Instances"][0]["InstanceId"]
        aws.client.get_waiter("instance_running").wait(InstanceIds=[instance_id])
    except Exception as e:
        log.error(f"Error launching new instance: {e}")
        return False

    log.info(f"Instance launched: {instance_id}")
    return MutableInstance(aws.resource.Instance(instance_id), aws)


def start(instance: MutableInstance):
    log = logging.getLogger(__name__)

    try:
        log.info(f"Starting instance: {instance.instance_id}")
        instance._i.start()
        instance._i.wait_until_running()
    except Exception as e:
        log.error(f"Failed to start instance: {e}")
        return False

    log.info(f"Instance started: {instance.instance_id}")
    return True


def stop(instance: MutableInstance, skip_prompt=False):
    """
    Stops an instance and will disable stop protection if required

    Return:
    -1 - Instance not stopped
    -2 - Error
    0 - Instance stopped
    1 - Instance not stopped and stop protection disabled
    2 - Instance already stopped
    """
    log = logging.getLogger(__name__)

    if instance.state["Name"] == "stopped":
        return 2

    log.info(f"Stopping instance: {instance.instance_id}")
    if not util.confirm("Continue? (y/n): ", skip_prompt):
        return -1

    try:
        instance._i.stop()
        instance._i.wait_until_stopped()
        log.info(f"Instance stopped: {instance.instance_id}")
        return 0
    except ClientError as e:
        stop_protection = (
            "Modify its 'disableApiStop' instance attribute and try again."
        )
        error = e.response["Error"]
        if (
            error["Code"] == "OperationNotPermitted"
            and stop_protection in error["Message"]
        ):
            log.warning(f"Instance has stop protection enabled: {instance.instance_id}")
            if util.confirm("Disable stop protection and continue? (y/n): "):
                instance._i.modify_attribute(DisableApiStop={"Value": False})
                instance.stop_protection = True
                stop(instance, True)
                return 1

        raise e
    except Exception as e:
        log.error(f"Error stopping instance: {e}")
        return -2


def terminate(instance: MutableInstance, retry=1, skip_prompt=False):
    """
    Terminates an instance.
    Will disable termination protection if enabled.

    Return:
    -1 - Instance not terminated
    -2 - Error
    0 - Instance terminated
    1 - Instance terminated and termination protection disabled
    """
    log = logging.getLogger(__name__)

    try:
        log.info(f"Terminating instance: {instance.instance_id}")
        if not util.confirm("Continue (y/n): ", skip_prompt):
            return -1
        stop(instance, True)

        instance._i.terminate()
        instance._i.wait_until_terminated()
        log.info(f"Instance terminated: {instance.instance_id}")
        return 0
    except ClientError as e:
        termination_protection = (
            "Modify its 'disableApiTermination' instance attribute and try again."
        )
        error = e.response["Error"]
        if (
            error["Code"] == "OperationNotPermitted"
            and termination_protection in error["Message"]
        ):
            log.warning(
                f"Instance has termination protection enabled: {instance.instance_id}"
            )
            if util.confirm("Disable termination protection and continue? (y/n): "):
                instance._i.modify_attribute(DisableApiTermination={"Value": False})
                terminate(instance, retry, True)
                return 1

        raise e
    except Exception as e:
        log.error(f"Error terminating instance: {e}")
        if retry > 0:
            log.warning("Retrying...")
            return terminate(instance, retry=retry - 1)

        try:
            log.warning("Double-checking...")
            instance.overwrite()
            state = instance.state["Name"]
            if state == "terminated" or state == "shutting-down":
                instance._i.wait_until_terminated()

            else:
                raise Exception("Instance not terminated")

        except Exception as e:
            log.error(f"Error terminating instance: {e}")
            log.error(
                f"Instance may be stuck terminating, last known state: {instance.state}."
            )
            return -2


def enable_stop_protection(instance: MutableInstance):
    log = logging.getLogger(__name__)
    log.info(f"Enabling stop protection for instance: {instance.instance_id}")
    try:
        instance._i.modify_attribute(DisableApiStop={"Value": True})
        return True
    except Exception as e:
        log.error(f"Error enabling stop protection: {e}")
        return False


def copy_volume_tags(source, destination, aws):
    log = logging.getLogger(__name__)

    try:
        log.info(
            f"Copying volume tags from instance: {source.instance_id} to: {destination.instance_id}"
        )

        destination_volumes = get_volumes_by_device_name(destination, aws)

        for dev_name, tags in source.ebs_volume_tags.items():
            if len(source.ebs_volume_tags[dev_name]) == 0:
                continue
            destination_volumes[dev_name].create_tags(Tags=tags)

    except Exception as e:
        log.error(f"Error copying volume tags. Please manually copy: {e}")
        return False

    return True


def disassociate_public_ip(instance: MutableInstance, aws):
    log = logging.getLogger(__name__)
    log.info(f"Disassociating public IP from instance: {instance.instance_id}")

    try:
        if instance.public_ip_address:
            eip_id = aws.client.describe_addresses(
                PublicIps=[instance.public_ip_address]
            )["Addresses"][0]["AllocationId"]

            eip = aws.resource.VpcAddress(eip_id)
            if not util.eip.disassociate(eip, aws):
                return False
        else:
            log.info(f"Instance: {instance.instance_id} has no EIP address")
            return False
    except Exception as e:
        log.error(f"Error disassociating EIP: {e}")
        return False

    return eip


def detach_nic(nic, aws):
    log = logging.getLogger(__name__)
    log.info(f"Detaching NIC: {nic['NetworkInterfaceId']}")
    if not util.confirm():
        return False

    try:
        nic_resource = aws.resource.NetworkInterface(nic["NetworkInterfaceId"])
        nic_resource.detach()
        aws.client.get_waiter("network_interface_available").wait(
            NetworkInterfaceIds=[nic["NetworkInterfaceId"]],
            WaiterConfig={"MaxAttempts": 20},
        )
        return nic
    except Exception as e:
        log.error(f"Unable to detach NIC: {nic['NetworkInterfaceId']}: {e}")
        return None


def attach_nic(instance: MutableInstance, nic, aws):
    log = logging.getLogger(__name__)

    try:
        aws.client.attach_network_interface(
            DeviceIndex=nic["Attachment"]["DeviceIndex"],
            NetworkInterfaceId=nic["NetworkInterfaceId"],
            InstanceId=instance.instance_id,
        )
        return True
    except Exception as e:
        log.error(f"Unable to attach NIC: {nic['NetworkInterfaceId']}: {e}")
        return None
