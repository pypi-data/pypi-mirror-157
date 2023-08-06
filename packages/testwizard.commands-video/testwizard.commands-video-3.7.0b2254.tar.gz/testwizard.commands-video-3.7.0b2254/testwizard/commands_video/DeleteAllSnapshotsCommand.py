import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkResult import OkResult


class DeleteAllSnapshotsCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "DeleteAllSnapShots")

    def execute(self):
        requestObj = []

        result = self.executeCommand(requestObj)

        return OkResult(result, "DeleteAllSnapshotsCommand was successful", "DeleteAllSnapshotsCommand failed")
