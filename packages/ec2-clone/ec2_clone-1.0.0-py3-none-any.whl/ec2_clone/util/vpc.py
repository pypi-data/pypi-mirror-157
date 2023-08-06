import ipaddress
import logging
import random

import ec2_clone.util as util


def get_ips(nic):
    ips = []
    if "PrivateIpAddresses" in nic:
        ips.extend([ip["PrivateIpAddress"] for ip in nic["PrivateIpAddresses"]])
    if "PrivateIpAddress" in nic:
        ips.append(nic["PrivateIpAddress"])

    return ips


def get_prefixes(nic):
    prefixes = []
    if "Ipv4Prefixes" in nic:
        prefixes.extend([prefix["Ipv4Prefix"] for prefix in nic["Ipv4Prefixes"]])
    return prefixes


def ip_conflict(nic, ignore_id, aws):
    """
    Checks if any desired IP addresses in a nic are currently in use.
    Returns true if there is a conflict

    ignore_id is the ID of a network interface that should be ignored when checking for conflicts.
    This is useful when checking for conflicts for a nic that will be replaced
    """
    log = logging.getLogger(__name__)
    log.info("Checking for IP conflicts with existing interfaces")

    for ip in get_ips(nic):
        if not ip_available(nic["SubnetId"], ip, ignore_id, aws):
            return True

    for prefix in get_prefixes(nic):
        if not ip_prefix_available(nic["SubnetId"], prefix, ignore_id, aws):
            return True

    log.info("No IP conflicts found")
    return False


def ip_available(subnet_id, private_ip, ignore_id, aws):
    """
    Checks if a given IP is available in a subnet.
    Checks both to ensure that the IP address is within the range of the subnet and that it is not already taken
    """
    log = logging.getLogger(__name__)

    filters = [{"Name": "subnet-id", "Values": [subnet_id]}]
    s = aws.client.describe_subnets(Filters=filters)["Subnets"][0]
    if s["AvailableIpAddressCount"] == 0:
        log.warning("No IP addresses available in subnet")
        return False

    private_ip_obj = ipaddress.ip_address(private_ip)
    if private_ip_obj not in ipaddress.ip_network(s["CidrBlock"]):
        log.warning("IP address is not in subnet")
        return False

    interfaces = aws.client.describe_network_interfaces(Filters=filters)[
        "NetworkInterfaces"
    ]
    for interface in interfaces:
        if interface["NetworkInterfaceId"] == ignore_id:
            continue
        for ip in interface["PrivateIpAddresses"]:
            if private_ip == ip["PrivateIpAddress"]:
                log.warning(
                    f"IP: {ip} is in use by interface: {interface['NetworkInterfaceId']}"
                )
                return False

        if "Ipv4Prefixes" in interface:
            for prefix in interface["Ipv4Prefixes"]:
                if private_ip_obj in ipaddress.ip_network(prefix["Ipv4Prefix"]):
                    log.warning(
                        f"IP: {private_ip} is enclosed by prefix for: {interface['NetworkInterfaceId']}"
                    )
                    return False

    return True


def ip_prefix_available(subnet_id, prefix, ignore_id, aws):
    """
    Checks if a given IP prefix is available in a subnet.

    Returns False if either:
        Prefix is not found in the subnet
        Prefix is already in use
        IP address contained within prefix is already in use
    """
    log = logging.getLogger(__name__)

    filters = [{"Name": "subnet-id", "Values": [subnet_id]}]
    subnet = aws.client.describe_subnets(Filters=filters)["Subnets"][0]
    if subnet["AvailableIpAddressCount"] == 0:
        log.warning("No IP addresses available in subnet")
        return False
    subnet = ipaddress.ip_network(subnet["CidrBlock"])

    prefix = ipaddress.ip_network(prefix)
    if not prefix.subnet_of(subnet):
        log.warning("Prefix is not in subnet")
        return False

    interfaces = aws.client.describe_network_interfaces(Filters=filters)[
        "NetworkInterfaces"
    ]
    for interface in interfaces:
        if interface["NetworkInterfaceId"] == ignore_id:
            continue
        for ip in interface["PrivateIpAddresses"]:
            ip = ipaddress.ip_address(ip["PrivateIpAddress"])
            if ip in prefix:
                log.warning(f"Existing IP: {ip} is contained within prefix: {prefix}")
                return False

        if "Ipv4Prefixes" in interface:
            for other_prefix in interface["Ipv4Prefixes"]:
                other_prefix = ipaddress.ip_network(other_prefix["Ipv4Prefix"])
                if prefix.overlaps(other_prefix):
                    log.warning(
                        f"Existing prefix: {other_prefix} is overlaps with: {prefix}"
                    )
                    return False

    return True


def generate_different_ip(ip, subnet_id, aws):
    log = logging.getLogger(__name__)
    subnet = aws.client.describe_subnets(SubnetIds=[subnet_id])["Subnets"][0]
    subnet = ipaddress.ip_network(subnet["CidrBlock"])

    # First three addresses are reserved by AWS for the VPC
    potential_ips = list(subnet.hosts())[3:]
    random.shuffle(potential_ips)

    for potential_ip in potential_ips:
        if potential_ip == ip:
            continue
        if util.vpc.ip_available(subnet_id, str(potential_ip), "", aws):
            return str(potential_ip)

    log.error("Unable to find a free IP address")
    return False


def generate_different_prefix(prefix, subnet_id, aws):
    log = logging.getLogger(__name__)
    subnet = aws.client.describe_subnets(SubnetIds=[subnet_id])["Subnets"][0]
    subnet = ipaddress.ip_network(subnet["CidrBlock"])

    prefix = ipaddress.ip_network(prefix)

    potential_subnets = list(subnet.subnets(new_prefix=prefix.prefixlen))
    random.shuffle(potential_subnets)

    for potential_subnet in potential_subnets:
        potential_subnet = ipaddress.ip_network(potential_subnet)
        if potential_subnet == prefix:
            continue
        if util.vpc.ip_prefix_available(subnet_id, str(potential_subnet), "", aws):
            return str(potential_subnet)

    log.error("Unable to find a free IP prefix")
    return False
