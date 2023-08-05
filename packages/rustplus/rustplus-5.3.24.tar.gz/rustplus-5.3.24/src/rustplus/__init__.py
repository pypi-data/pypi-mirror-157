r"""
RustPlus, An API wrapper for interfacing with the Rust+ App API
"""

from .V5_3_24.api import RustSocket
from .V5_3_24.api.structures import EntityEvent, TeamEvent, ChatEvent
from .V5_3_24.api.remote.fcm_listener import FCMListener
from .V5_3_24.commands import CommandOptions, Command
from .V5_3_24.exceptions import *
from .V5_3_24.conversation import ConversationFactory, Conversation, ConversationPrompt
from .V5_3_24.utils import *

__name__ = "rustplus"
__author__ = "olijeffers0n"
__version__ = "5.3.24"
__support__ = "Discord: https://discord.gg/nQqJe8qvP8"
