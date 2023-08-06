from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.get_completed_job_response_200_raw_flow_modules_item_value_type import (
    GetCompletedJobResponse200RawFlowModulesItemValueType,
)

T = TypeVar("T", bound="GetCompletedJobResponse200RawFlowModulesItemValue")


@attr.s(auto_attribs=True)
class GetCompletedJobResponse200RawFlowModulesItemValue:
    """ """

    path: str
    type: GetCompletedJobResponse200RawFlowModulesItemValueType
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        path = self.path
        type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        path = d.pop("path")

        type = GetCompletedJobResponse200RawFlowModulesItemValueType(d.pop("type"))

        get_completed_job_response_200_raw_flow_modules_item_value = cls(
            path=path,
            type=type,
        )

        get_completed_job_response_200_raw_flow_modules_item_value.additional_properties = d
        return get_completed_job_response_200_raw_flow_modules_item_value

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
