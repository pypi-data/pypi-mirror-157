
import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult


class LaunchAppCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "Mobile.LaunchApp")

    def execute(self):
        requestObj = []

        result = self.executeCommand(requestObj)

        return SimpleResult(result, "LaunchApp was successful", "LaunchApp failed")
