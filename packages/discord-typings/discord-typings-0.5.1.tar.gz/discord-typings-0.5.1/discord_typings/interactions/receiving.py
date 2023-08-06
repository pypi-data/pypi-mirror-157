from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Union

from typing_extensions import Literal, NotRequired, TypedDict, final

if TYPE_CHECKING:
    from ..reference import Snowflake
    from ..resources import (
        AllowedMentionsData, AttachmentData, EmbedData, GuildMemberData,
        MessageData, PartialChannelData, RoleData, UserData
    )
    from .commands import (
        ApplicationCommandOptionInteractionData, AutocompleteOptionData,
        Locales, SubcommandGroupOptionInteractionData,
        SubcommandOptionInteractionData
    )
    from .components import (
        ComponentData, SelectMenuComponentData, SelectMenuOptionData,
        TextInputComponentData
    )

__all__ = (
    'InteractionData', 'InteractionType', 'ResolvedInteractionDataData',
    'MessageInteractionData', 'InteractionResponseData', 'InteractionCallbackTypes',
    'InteractionCallbackData', 'ApplicationCommandInteractionData',
    'ComponentInteractionData', 'AutocompleteInteractionData', 'InteractionData',
    'InteractionMessageCallbackData', 'InteractionAutocompleteCallbackData',
    'InteractionModalCallbackData', 'InteractionMessageResponseData',
    'InteractionAutocompleteResponseData', 'InteractionModalResponseData',
    'InteractionNodataResponseData', 'ModalInteractionData'
)


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-structure


class GuildInteractionData(TypedDict):
    id: Snowflake
    application_id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake
    member: GuildMemberData
    token: str
    version: int
    locale: Locales
    guild_locale: Locales


@final
class ApplicationCommandGuildInteractionData(GuildInteractionData):
    type: Literal[2]
    data: ApplicationCommandInteractionDataData
    app_permissions: str


@final
class ComponentGuildInteractionData(GuildInteractionData):
    type: Literal[3]
    data: ComponentInteractionDataData
    message: MessageData
    app_permissions: str


@final
class ModalGuildInteractionData(GuildInteractionData):
    type: Literal[5]
    data: ModalComponentInteractionDataData
    message: MessageData
    app_permissions: str


@final
class AutocompleteGuildInteractionData(GuildInteractionData):
    type: Literal[4]
    data: ApplicationCommandInteractionDataData


class ChannelInteractionData(TypedDict):
    id: Snowflake
    application_id: Snowflake
    channel_id: Snowflake
    user: UserData
    token: str
    version: int
    locale: Locales


@final
class ApplicationCommandChannelInteractionData(ChannelInteractionData):
    type: Literal[2]
    data: ApplicationCommandInteractionDataData
    app_permissions: str


@final
class ComponentChannelInteractionData(ChannelInteractionData):
    type: Literal[3]
    data: ComponentInteractionDataData
    message: MessageData
    app_permissions: str


@final
class ModalChannelInteractionData(ChannelInteractionData):
    type: Literal[5]
    data: ModalComponentInteractionDataData
    message: MessageData
    app_permissions: str


@final
class AutocompleteChannelInteractionData(ChannelInteractionData):
    type: Literal[4]
    data: ApplicationCommandInteractionDataData


class UserCommandInteractionBase(TypedDict):
    id: Snowflake
    application_id: Snowflake
    type: Literal[2]
    data: ContextMenuInteractionDataData
    token: str
    version: int
    locale: Locales
    app_permissions: str


@final
class GuildUserCommandInteractionData(UserCommandInteractionBase):
    member: GuildMemberData
    guild_locale: Locales


@final
class ChannelUserCommandInteractionData(UserCommandInteractionBase):
    user: UserData


ApplicationCommandInteractionData = Union[
    ApplicationCommandGuildInteractionData, ApplicationCommandChannelInteractionData,
    GuildUserCommandInteractionData, ChannelUserCommandInteractionData
]


ComponentInteractionData = Union[
    ComponentGuildInteractionData, ComponentChannelInteractionData
]


ModalInteractionData = Union[
    ModalGuildInteractionData, ModalChannelInteractionData
]

AutocompleteInteractionData = Union[
    AutocompleteGuildInteractionData, AutocompleteChannelInteractionData
]


InteractionData = Union[
    ApplicationCommandInteractionData, ComponentInteractionData, AutocompleteInteractionData,
    ModalInteractionData,
]


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-type


InteractionType = Literal[1, 2, 3, 4, 5]


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-data-structure


class ApplicationCommandInteractionDataBase(TypedDict):
    id: Snowflake
    name: str
    type: Literal[1, 2, 3]
    resolved: NotRequired[ResolvedInteractionDataData]
    options: NotRequired[
        List[Union[
            SubcommandOptionInteractionData,
            SubcommandGroupOptionInteractionData,
            ApplicationCommandOptionInteractionData
        ]]
    ]


@final
class ApplicationCommandInteractionDataData(ApplicationCommandInteractionDataBase):
    pass


@final
class ButtonComponentInteractionDataData(TypedDict):
    custom_id: str
    component_type: Literal[2]


@final
class SelectComponentInteractionDataData(TypedDict):
    custom_id: str
    component_type: Literal[3]
    values: List[SelectMenuOptionData]


@final
class ModalComponentInteractionDataData(TypedDict):
    custom_id: str
    component_type: Literal[4]
    components: List[Union[TextInputComponentData, SelectMenuComponentData]]


ComponentInteractionDataData = Union[
    ButtonComponentInteractionDataData, SelectComponentInteractionDataData,
    ModalComponentInteractionDataData
]


@final
class ContextMenuInteractionDataData(ApplicationCommandInteractionDataBase):
    target_id: Snowflake


InteractionDataData = Union[
    ApplicationCommandInteractionDataData, ButtonComponentInteractionDataData,
    SelectComponentInteractionDataData, ContextMenuInteractionDataData
]


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-resolved-data-structure


@final
class ResolvedInteractionDataData(TypedDict):
    users: NotRequired[Dict[Snowflake, UserData]]
    members: NotRequired[Dict[Snowflake, GuildMemberData]]
    roles: NotRequired[Dict[Snowflake, RoleData]]
    channels: NotRequired[Dict[Snowflake, PartialChannelData]]
    messages: NotRequired[Dict[Snowflake, MessageData]]


# https://discord.com/developers/docs/interactions/receiving-and-responding#message-interaction-object-message-interaction-structure


@final
class MessageInteractionData(TypedDict):
    id: Snowflake
    type: Literal[2, 3, 4]
    name: str
    user: UserData


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-interaction-response-structure


@final
class InteractionMessageResponseData(TypedDict):
    type: Literal[4, 7]
    data: InteractionMessageCallbackData


@final
class InteractionAutocompleteResponseData(TypedDict):
    type: Literal[8]
    data: InteractionAutocompleteCallbackData


@final
class InteractionModalResponseData(TypedDict):
    type: Literal[9]
    data: InteractionModalCallbackData


@final
class InteractionNodataResponseData(TypedDict):
    type: Literal[1, 5, 6]


InteractionResponseData = Union[
    InteractionMessageResponseData, InteractionAutocompleteResponseData,
    InteractionModalResponseData, InteractionNodataResponseData
]


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-interaction-callback-type


InteractionCallbackTypes = Literal[1, 4, 5, 6, 7, 8, 9]


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-interaction-callback-data-structure


@final
class InteractionMessageCallbackData(TypedDict):
    tts: NotRequired[bool]
    content: NotRequired[str]
    embeds: NotRequired[List[EmbedData]]
    allowed_mentions: NotRequired[AllowedMentionsData]
    flags: NotRequired[int]
    components: NotRequired[List[ComponentData]]
    attachments: NotRequired[List[AttachmentData]]


@final
class InteractionAutocompleteCallbackData(TypedDict):
    choices: List[AutocompleteOptionData]


@final
class InteractionModalCallbackData(TypedDict):
    custom_id: str
    title: str
    components: List[ComponentData]


InteractionCallbackData = Union[
    InteractionMessageCallbackData, InteractionAutocompleteCallbackData,
    InteractionModalCallbackData
]
