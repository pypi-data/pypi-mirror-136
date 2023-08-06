from dataclasses import dataclass
from typing import Type, List, Dict

from ubotadapter import ChannelType
from ubotadapter.bots import *


@dataclass
class ChannelData:
    channel_type: ChannelType
    alias: str
    bot_cls: Type[UBotAdapter]


class Channel:
    def __init__(self, channel_data: ChannelData):
        self._channel_data = channel_data

    @property
    def channel_data(self) -> ChannelData:
        return self._channel_data


class Channels:
    _channels = [
        Channel(ChannelData(
            channel_type=ChannelType.NoChannel,
            alias='NONE',
            bot_cls=UBotAdapter
        )),
        Channel(ChannelData(
            channel_type=ChannelType.Telegram,
            alias='tg',
            bot_cls=Telegram
        )),
        Channel(ChannelData(
            channel_type=ChannelType.VK,
            alias='vk',
            bot_cls=VK
        )),
        Channel(ChannelData(
            channel_type=ChannelType.DTF,
            alias='dtf',
            bot_cls=DTF
        )),
    ]

    def __init__(self):
        self._alias_map = {ch.channel_data.channel_type: ch for ch in self.get_channels()}

    @staticmethod
    def get_channels() -> List[Channel]:
        return Channels._channels

    @property
    def alias_map(self) -> Dict[ChannelType, Channel]:
        return self._alias_map

    def __getitem__(self, channel_type: ChannelType) -> Channel:
        try:
            return self.alias_map[channel_type]
        except KeyError:
            raise KeyError(f'No channel {channel_type} in ChannelTypeAlias data')

    def get_alias_by_channel_type(self, channel_type: ChannelType) -> str:
        return self[channel_type].channel_data.alias


CHANNELS = Channels()

if __name__ == '__main__':
    CHANNELS.get_alias_by_channel_type(ChannelType.DTF)
