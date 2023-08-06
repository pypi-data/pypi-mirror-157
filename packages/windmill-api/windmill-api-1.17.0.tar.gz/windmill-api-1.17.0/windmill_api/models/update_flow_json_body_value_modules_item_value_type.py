from enum import Enum


class UpdateFlowJsonBodyValueModulesItemValueType(str, Enum):
    SCRIPT = "script"
    FLOW = "flow"
    RAWSCRIPT = "rawscript"

    def __str__(self) -> str:
        return str(self.value)
