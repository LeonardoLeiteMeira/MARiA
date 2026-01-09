from __future__ import annotations

from typing import Any

from external.notion.enum import UserDataTypes

from MARiA.graph.state import State


STATE_KEY_BY_TYPE: dict[UserDataTypes, str] = {
    UserDataTypes.CARDS_AND_ACCOUNTS: "cards",
    UserDataTypes.CATEGORIES: "categories",
    UserDataTypes.MACRO_CATEGORIES: "macroCategories",
    UserDataTypes.MONTHS: "months",
}


def _get_state_section(state: State, key: str | None) -> dict[str, Any] | None:
    if not key:
        return None
    section = state.get(key)
    if isinstance(section, dict):
        return section
    return None


def get_state_records(state: State, key: str | None) -> list[dict[str, Any]]:
    section = _get_state_section(state, key)
    if not section:
        return []
    data = section.get("data")
    if isinstance(data, list):
        return data
    return []


def get_state_records_by_type(state: State, data_type: UserDataTypes) -> list[dict[str, Any]]:
    return get_state_records(state, STATE_KEY_BY_TYPE.get(data_type))


def get_data_id_from_state(state: State, data_type: UserDataTypes, register_name: str | None) -> str | None:
    if not register_name:
        return None
    for record in get_state_records_by_type(state, data_type):
        if record.get("Name") == register_name:
            return record.get("id")
    return None


def get_state_section_by_type(state: State, data_type: UserDataTypes) -> dict[str, Any] | None:
    return _get_state_section(state, STATE_KEY_BY_TYPE.get(data_type))
