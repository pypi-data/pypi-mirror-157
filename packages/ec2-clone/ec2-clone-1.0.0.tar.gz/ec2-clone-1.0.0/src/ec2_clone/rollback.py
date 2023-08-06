import logging

import ec2_clone.util as util


class Rollback:
    def __init__(self, instance, aws):
        self.instance = instance
        self.aws = aws
        self.eip = None
        self.name = None
        self.ami = None
        self.is_running = None
        self.secondary_nics = []
        self.instance.stop_protection = False

    def roll(self):
        """
        Revert changes made to instance/Ami
        """
        log = logging.getLogger(__name__)
        if not (
            self.eip
            or self.name
            or self.ami
            or self.is_running
            or self.secondary_nics
            or self.instance.stop_protection
        ):
            log.debug("No changes to rollback")
            return

        log.warning("Rolling back changes")

        if self.eip:  # EIP should be associated before reassociating NICS
            util.eip.associate(self.eip, self.instance)

        if self.name:
            util.instance.rename(self.instance, self.name)

        if self.ami:
            util.ami.delete(self.ami, self.aws)

        if self.is_running:
            util.instance.start(self.instance)

        for nic in self.secondary_nics:
            util.instance.attach_nic(self.instance, nic, self.aws)

        if self.instance.stop_protection:
            util.instance.enable_stop_protection(self.instance)
