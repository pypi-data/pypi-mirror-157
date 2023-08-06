import logging

import ec2_clone.util as util


def associate(eip, target):
    log = logging.getLogger(__name__)

    try:
        if "eni-" in target:
            log.info(f"Associating EIP: {eip.allocation_id} to NIC: {target}")
            eip.associate(NetworkInterfaceId=target)
        else:
            log.info(f"Associating EIP: {eip.allocation_id} to Instance: {target}")
            eip.associate(InstanceId=target)

        log.info(f"EIP associated: {eip.allocation_id}")
        return True
    except Exception as e:
        log.error(f"Failed to attach EIP: {e}")
        return False


def disassociate(eip, aws):
    log = logging.getLogger(__name__)
    log.info(f"Disassociating EIP: {eip.allocation_id}")

    if not util.confirm():
        return False

    try:
        aws.client.disassociate_address(AssociationId=eip.association_id)
        log.info(f"EIP disassociated: {eip.allocation_id}")
    except Exception as e:
        log.error(f"Failed to disassociate EIP: {e}")
        return False

    return True
