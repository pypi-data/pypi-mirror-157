import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult


class MultiTouch_PerformCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "Mobile.MultiTouch_Perform")

    def execute(self):
        requestObj = []

        result = self.executeCommand(requestObj)

        return SimpleResult(result, "MultiTouch_Perform was successful", "MultiTouch_Perform failed")
