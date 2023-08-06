import ec2_clone as ec

from . import ami, eip, instance, vpc


def confirm(prompt="Continue? (y/n): ", skip=False):
    if ec.YES:
        return True
    if skip:
        return True

    answer = input(prompt)
    if answer.lower() == "y":
        return True
    return False


def get_tag_specifications(tag_list, resource_types):
    if type(resource_types) is not list:
        resource_types = [resource_types]

    tag_specifications = []
    for resource_type in resource_types:
        tag_specifications.append(
            {"ResourceType": resource_type, "Tags": remove_aws_tags(tag_list)}
        )

    return tag_specifications


def get_tag_dict(tag_list):
    if not tag_list:
        return {}
    return {tag["Key"]: tag["Value"] for tag in remove_aws_tags(tag_list)}


def remove_aws_tags(tag_list):
    if not tag_list:
        return []
    return [tag for tag in tag_list if "aws:" not in tag["Key"]]
