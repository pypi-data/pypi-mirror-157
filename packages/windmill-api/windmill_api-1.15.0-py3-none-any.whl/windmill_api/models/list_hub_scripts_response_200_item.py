from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="ListHubScriptsResponse200Item")


@attr.s(auto_attribs=True)
class ListHubScriptsResponse200Item:
    """ """

    id: float
    summary: str
    app: str
    approved: bool
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        summary = self.summary
        app = self.app
        approved = self.approved

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "summary": summary,
                "app": app,
                "approved": approved,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        summary = d.pop("summary")

        app = d.pop("app")

        approved = d.pop("approved")

        list_hub_scripts_response_200_item = cls(
            id=id,
            summary=summary,
            app=app,
            approved=approved,
        )

        list_hub_scripts_response_200_item.additional_properties = d
        return list_hub_scripts_response_200_item

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
