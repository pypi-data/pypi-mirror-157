from enum import Enum


class FlowModuleValueType(str, Enum):
    SCRIPT = "script"
    FLOW = "flow"
    RAWSCRIPT = "rawscript"

    def __str__(self) -> str:
        return str(self.value)
