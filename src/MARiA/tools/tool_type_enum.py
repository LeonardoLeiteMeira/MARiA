from enum import Enum


class ToolType(str, Enum):
    AGENT_REDIRECT = "agent_redirect"
    EXECUTION = "execution"