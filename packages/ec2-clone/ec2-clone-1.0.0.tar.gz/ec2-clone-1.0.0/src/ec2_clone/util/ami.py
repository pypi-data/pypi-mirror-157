import logging
from datetime import datetime, timedelta

import ec2_clone.util as util


class MutableAmi:
    def _init(self):
        self.ebs_mappings = get_ebs_mappings(self._ami)

        self.architecture = self._ami.architecture
        self.block_device_mappings = self._ami.block_device_mappings
        self.boot_mode = self._ami.boot_mode
        self.creation_date = self._ami.creation_date
        self.deprecation_time = self._ami.deprecation_time
        self.description = self._ami.description
        self.ena_support = self._ami.ena_support
        self.hypervisor = self._ami.hypervisor
        self.image_id = self._ami.image_id
        self.image_location = self._ami.image_location
        self.kernel_id = self._ami.kernel_id
        self.name = self._ami.name
        self.owner_id = self._ami.owner_id
        self.platform = self._ami.platform
        self.platform_details = self._ami.platform_details
        self.product_codes = self._ami.product_codes
        self.public = self._ami.public
        self.ramdisk_id = self._ami.ramdisk_id
        self.root_device_name = self._ami.root_device_name
        self.root_device_type = self._ami.root_device_type
        self.sriov_net_support = self._ami.sriov_net_support
        self.state = self._ami.state
        self.state_reason = self._ami.state_reason
        self.tags = self._ami.tags
        self.tpm_support = self._ami.tpm_support
        self.usage_operation = self._ami.usage_operation
        self.virtualization_type = self._ami.virtualization_type

    def __init__(self, ami):
        self._ami = ami
        self._init()

    def update(self):
        self._ami.load()

    def overwrite(self):
        self._ami.load()
        self._init()


def get(id, aws):
    log = logging.getLogger(__name__)

    try:
        images = aws.client.describe_images(ImageIds=[id])["Images"]
        if len(images) == 0:
            log.error(f"No AMI found with ID: {id}")
            return False
        id = images[0]["ImageId"]
        image = aws.resource.Image(id)
    except Exception as e:
        log.error(f"Error getting AMI: {id}: {e}")
        return None

    return MutableAmi(image)


def get_ebs_mappings(ami: MutableAmi) -> MutableAmi:
    log = logging.getLogger(__name__)
    log.debug(f"Gathering EBS mappings for AMI: {ami.image_id}")

    ebs_mappings = []
    for ebs_mapping in ami.block_device_mappings:
        if "Ebs" in ebs_mapping:
            ebs_mappings.append(ebs_mapping)

    return ebs_mappings


def tag_snapshots(
    ami: MutableAmi, aws, tags=None, TagSpecifications=None
) -> MutableAmi:
    log = logging.getLogger(__name__)
    log.info("Taggin AMI snapshots")
    try:
        snapshot_ids = []
        for ebs_mapping in ami.ebs_mappings:
            if "SnapshotId" not in ebs_mapping["Ebs"]:
                log.warn(
                    f"Not snapshot ID found for EBS mapping: {ebs_mapping['DeviceName']}"
                )
                continue
            snapshot_ids.append(ebs_mapping["Ebs"]["SnapshotId"])

        if not tags and TagSpecifications:
            tags = list(
                filter(lambda x: x["ResourceType"] == "snapshot", TagSpecifications)
            )[0]["Tags"]

        aws.client.create_tags(Resources=snapshot_ids, Tags=tags)
        return True
    except Exception as e:
        log.error(f"Error tagging AMI snapshots: {e}")
        return False


def get_root_volume_index(ami: MutableAmi):
    log = logging.getLogger(__name__)
    try:
        log.info("Getting AMI root volume")
        for i, ebs_mapping in enumerate(ami.ebs_mappings):
            if ebs_mapping["DeviceName"] == ami.root_device_name:
                return i
    except Exception as e:
        log.error(f"Error getting root volume for AMI {e}", e)
        return False
    return ami


def encrypt_root_volume(ami: MutableAmi, kms_key_id) -> MutableAmi:
    log = logging.getLogger(__name__)
    try:
        root_volume_index = get_root_volume_index(ami)
        log.info(
            f"Enabling encryption for AMI root volume {ami.ebs_mappings[root_volume_index]['DeviceName']}"
        )
        if "Ebs" not in ami.ebs_mappings[root_volume_index]:
            log.error("Root volume is not an EBS volume, can't enable encyrption")
            return False

        ami.ebs_mappings[root_volume_index]["Ebs"]["Encrypted"] = True

        if kms_key_id:
            ami.ebs_mappings[root_volume_index]["Ebs"]["KmsKeyId"] = kms_key_id

    except Exception as e:
        log.error("Error enabling root volume encryption: %s", e)
        return False

    return ami


def increase_root_volume(ami: MutableAmi, set=None, increase=None) -> MutableAmi:
    log = logging.getLogger(__name__)

    try:
        root_volume_index = get_root_volume_index(ami)
        if set:
            log.info(f"Setting root volume size for AMI: {ami.image_id} to {set}")
            ami.ebs_mappings[root_volume_index]["Ebs"]["VolumeSize"] = set
        elif increase:
            log.info(
                f"Increasing root volume size for AMI: {ami.image_id} by {increase}GiB"
            )
            current_size = ami.ebs_mappings[root_volume_index]["Ebs"]["VolumeSize"]
            ami.ebs_mappings[root_volume_index]["Ebs"]["VolumeSize"] = (
                current_size + increase
            )
        else:
            raise ValueError("No increase or set value specified")
    except Exception as e:
        log.error(f"Error increasing root volume size: {e}")
        return False

    return ami


def create(
    instance,
    ami_name,
    aws,
    delete_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
    tags=None,
) -> MutableAmi:
    log = logging.getLogger(__name__)

    # TODO it would be nice to only copy some tags to certain resource_types, some kind of tag profile
    TagSpecifications = []
    if tags:
        TagSpecifications = util.get_tag_specifications(
            instance.tags, ["image", "snapshot"]
        )

    log.info(f"Creating AMI, Name: {ami_name}")
    try:
        if not util.confirm():
            raise Exception("User aborted")
        ami = aws.client.create_image(
            InstanceId=instance.instance_id,
            Name=ami_name,
            Description=f"AMI for enabling hibernation. Delete after {delete_date}",
            NoReboot=True,
            TagSpecifications=TagSpecifications,
        )
        aws.client.get_waiter("image_available").wait(ImageIds=[ami["ImageId"]])
    except Exception as e:
        log.error(f"Error creating AMI: {e}")
        max_attempts = "Waiter ImageAvailable failed: Max attempts exceeded"
        if e == max_attempts:
            log.error(
                "AMI Creation timed out, please wait and specify AMI ID or delete AMI and try again"
            )
        return False

    log.info(f"Created AMI: {ami['ImageId']}")
    return MutableAmi(aws.resource.Image(ami["ImageId"]))


def delete(ami: MutableAmi, aws):
    """
    Deletes an AMI and all associated snapshots by ID
    """
    log = logging.getLogger(__name__)

    log.info(f"Deleting AMI: {ami.image_id}")
    if not util.confirm():
        return True

    try:
        log.debug("Deregistering Image")
        ami._ami.deregister()

        log.info("Deleting AMI snapshots")
        for ebs_mapping in ami.ebs_mappings:
            s = aws.resource.Snapshot(ebs_mapping["Ebs"]["SnapshotId"])
            log.info(f"Deleting snapshot: {s.snapshot_id}")
            s.delete()

    except Exception as e:
        log.error(f"Error deleting AMI: {e}")
        return False

    log.info(f"AMI: {ami.image_id} deleted")
    return True
