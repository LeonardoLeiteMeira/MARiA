from enum import Enum


class ToolType(str, Enum):
    HUMAN_INTERRUPT = "human_interrupt"
    AGENT_REDIRECT = "agent_redirect"
    EXECUTION = "execution"
