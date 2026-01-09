from typing import Any


# TODO falta usar essa estrutura para armazenar as transacoes de maneira mais simples
class NotionProperties:
    BASIC_PROPERTIES = ["number", "relation", "date", "created_time"]

    def __init__(self, key: str, property: dict[str, Any]) -> None:
        self.key = key
        self.property = property
        self.property_type: str = property["type"]
        self.value = self.get_value()

    def get_value(self) -> Any:
        if self.property_type in self.BASIC_PROPERTIES:
            return self.__basic_type()

        method_name = f"_{self.__class__.__name__}__{self.property_type}"
        return getattr(self, method_name)()

    def __basic_type(self) -> Any:
        return self.property[self.property_type]

    def __select(self) -> Any:
        if self.property["select"] is not None:
            return self.property["select"]["name"]
        return None

    def __title(self) -> Any:
        return ([item["plain_text"] for item in self.property["title"]])[0]

    def __formula(self) -> Any:
        type_value = self.property["formula"]["type"]
        return self.property[self.property_type][type_value]

    def __created_by(self) -> Any:
        created_by = self.property.get("created_by")
        if created_by is None:
            return None
        return created_by.get("name") or created_by.get("id")

    def __status(self) -> Any:
        status = self.property.get("status")
        if status is None:
            return None
        return status.get("name")

    def __last_edited_by(self) -> Any:
        last_edited_by = self.property.get("last_edited_by")
        if last_edited_by is None:
            return None
        return last_edited_by.get("name") or last_edited_by.get("id")

    def __updatedBy(self) -> Any:
        updated_by = self.property.get("updatedBy")
        if updated_by is None:
            return None
        return updated_by.get("name") or updated_by.get("id")

    def __rich_text(self) -> Any:
        rich_text = self.property.get("rich_text", [])
        if not rich_text:
            return ""
        return "".join([item.get("plain_text", "") for item in rich_text])

    def __multi_select(self) -> Any:
        multi_select = self.property.get("multi_select", [])
        if not multi_select:
            return []
        return [item.get("name") for item in multi_select]

    def __people(self) -> Any:
        people = self.property.get("people", [])
        if not people:
            return []
        return [person.get("name") or person.get("id") for person in people]

    def __files(self) -> Any:
        files = self.property.get("files", [])
        if not files:
            return []
        result = []
        for file in files:
            if file["type"] == "external":
                url = file["external"]["url"]
            elif file["type"] == "file":
                url = file["file"]["url"]
            else:
                url = None
            result.append({"name": file.get("name"), "url": url})
        return result

    def __checkbox(self) -> Any:
        return self.property.get("checkbox", False)

    def __url(self) -> Any:
        return self.property.get("url")

    def __email(self) -> Any:
        return self.property.get("email")

    def __phone_number(self) -> Any:
        return self.property.get("phone_number")

    def __rollup(self) -> Any:
        rollup = self.property.get("rollup")
        if not rollup:
            return None
        rollup_type = rollup.get("type")
        return rollup.get(rollup_type)

    def __last_edited_time(self) -> Any:
        return self.property.get("last_edited_time")

    def __unique_id(self) -> Any:
        unique_id = self.property.get("unique_id")
        if not unique_id:
            return None
        return {"number": unique_id.get("number"), "prefix": unique_id.get("prefix")}

    def __verification(self) -> Any:
        verification = self.property.get("verification")
        if not verification:
            return None
        result = {"state": verification.get("state")}
        verified_by = verification.get("verified_by")
        if verified_by:
            result["verified_by"] = verified_by.get("name") or verified_by.get("id")
        result["date"] = verification.get("date")
        return result
