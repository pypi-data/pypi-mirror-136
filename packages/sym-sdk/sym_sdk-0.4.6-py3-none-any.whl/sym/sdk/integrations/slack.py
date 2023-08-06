"""Helpers for interacting with a Slack workspace."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Sequence, Union

from sym.sdk.errors import SymIntegrationErrorEnum
from sym.sdk.user import User


class SlackError(SymIntegrationErrorEnum):
    """Raised when there is an error connecting to Slack's API."""

    UNKNOWN = (
        "An unexpected error occurred while trying to connect to Slack.",
        "Sym Support has been notified of this issue and should be reaching out shortly.",
    )
    TIMEOUT = ("Sym timed out while trying to connect to Slack.", "Try again in a few seconds.")


class SlackLookupType(str, Enum):
    USER = "user"
    USER_ID = "user_id"
    USERNAME = "username"
    CHANNEL = "channel"
    GROUP = "group"
    EMAIL = "email"


@dataclass
class SlackChannel:
    lookup_type: SlackLookupType
    lookup_keys: List[Union[str, User]]
    allow_self: bool = True
    fallback_channel: Optional[str] = None


def user(identifier: Union[str, User]) -> SlackChannel:
    """A reference to a Slack user.

    Users can be specified with a Slack user ID, email,
    or Sym :class:`~sym.sdk.user.User` instance.
    """


def channel(
    name: str, allow_self: bool = False, fallback_channel: Optional[str] = None
) -> SlackChannel:
    """
    A reference to a Slack channel.

    Args:
        name: The channel name to send the message to.
        allow_self: Whether to allow the current user to approve their own request.
        fallback_channel: If the channel cannot be found, send the message to this channel instead.
    """


def group(users: Sequence[Union[str, User]], allow_self: bool = False) -> SlackChannel:
    """
    A reference to a Slack group.

    Args:
        users (Sequence[Union[str, User]]): A list of either Sym :class:`~sym.sdk.user.User` objects or emails.
    """
