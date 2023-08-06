import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkResult import OkResult


class DeleteAllRecordingsCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "DeleteAllRecordings")

    def execute(self):
        requestObj = []

        result = self.executeCommand(requestObj)

        return OkResult(result, "DeleteAllRecordings was successful", "DeleteAllRecordings failed")
