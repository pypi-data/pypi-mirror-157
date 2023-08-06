import logging

import ec2_clone.settings as settings
import ec2_clone.util as util
from ec2_clone.rollback import Rollback


def detach_secondary_nics(instance, rollback, aws):
    log = logging.getLogger(__name__)

    if len(instance.network_interfaces) > 1:
        log.info(f"Instance: {instance.instance_id} has multiple nics")
        rollback.secondary_nics = []

        for nic in instance.network_interfaces_attribute:
            if nic["Attachment"]["DeviceIndex"] == 0:
                continue

            detached_nic = util.instance.detach_nic(nic, aws)
            if not detached_nic:
                log.error(f"Failed to detach nic: {nic}")
                rollback.roll()
                return False, None

            rollback.secondary_nics.append(detached_nic)
        return rollback, rollback.secondary_nics
    else:
        return rollback, None


def detach_eip(instance, rollback, aws):
    log = logging.getLogger(__name__)

    instance.update()
    if instance._i.public_ip_address:
        log.info(f"Instance: {instance.instance_id} has static EIP address")

        rollback.eip = util.instance.disassociate_public_ip(instance, aws)
        if not rollback.eip:
            log.error("Failed to disassociate EIP")
            rollback.roll()
            return False, None

        return rollback, rollback.eip
    else:
        return rollback, None


def detach_associations(instance, rollback, aws):
    stopped = util.instance.stop(instance, aws)
    if stopped < 0:
        rollback.roll()
        return False

    rollback, nics = detach_secondary_nics(instance, rollback, aws)
    if not rollback:
        return False

    rollback, eip = detach_eip(instance, rollback, aws)
    if not rollback:
        return False

    return rollback, {"nics": nics, "eip": eip}


def cleanup(instance, new_instance, associations, launch_new=True):
    log = logging.getLogger(__name__)
    if associations["eip"]:
        if associations["nics"]:
            primary = util.instance.get_primary_nic(
                new_instance.network_interfaces_attribute
            )
            util.eip.associate(associations["eip"], primary["NetworkInterfaceId"])
        else:
            util.eip.associate(associations["eip"], new_instance.instance_id)

    if instance.stop_protection:
        if not util.instance.enable_stop_protection(new_instance):
            log.warn(
                "Failed to enable stop protection for new instance, please enable manually"
            )
        if launch_new:
            if not util.instance.enable_stop_protection(instance):
                log.warn(
                    "Failed to enable stop protection for old instance, please enable manually"
                )


def replace_instance(instance, i_settings, rollback, aws):
    """
    Remove secondary nics
    Remove EIP
    Terminate Old instance
    Launch new instance
    Reassocaite EIP
    """
    log = logging.getLogger(__name__)
    try:
        rollback, associations = detach_associations(instance, rollback, aws)
        if not rollback:
            return False

        terminated = util.instance.terminate(instance)
        if terminated < 0:
            rollback.roll()
            return False

        # Reset rollback because instance has been terminated
        rollback = Rollback(instance, aws)

        new_instance = run_instance(instance, i_settings, aws)
        if not new_instance:
            settings.dump(i_settings)
            return False

        cleanup(instance, new_instance, associations)

        return new_instance
    except Exception as e:
        log.error(f"Unexpected Failure: {e}")
        rollback.roll()
        return False


def launch_new_instance(instance, i_settings, rollback, aws):
    """
    Remove secondary nics
    Remove EIP
    Rename old instance
    Launch new instance
    Reassociate EIP
    """
    log = logging.getLogger(__name__)

    try:
        rollback, associations = detach_associations(instance, rollback, aws)
        if not rollback:
            return False

        new_instance = run_instance(instance, i_settings, aws)
        if not new_instance:
            settings.dump(i_settings)
            rollback.roll()
            return False

        cleanup(instance, new_instance, associations, launch_new=False)

        return new_instance
    except Exception as e:
        log.error(f"Unexpected Failure: {e}")
        rollback.roll()
        return False


def run_instance(instance, i_settings, aws):
    log = logging.getLogger(__name__)
    try:
        new_instance = util.instance.run(i_settings, aws)
        if not new_instance:
            return False

        util.instance.copy_volume_tags(instance, new_instance, aws)

        return new_instance
    except Exception as e:
        log.error(f"Unexpected Failure: {e}")
        return False
