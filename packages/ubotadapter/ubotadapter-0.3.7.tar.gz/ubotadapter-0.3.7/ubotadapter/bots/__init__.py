from ubotadapter import UBotAdapter
from ubotadapter.bots.dtf.dtf import DTF
from ubotadapter.bots.telegram.tg import Telegram
from ubotadapter.bots.vk.vk import VK
from .channel import CHANNELS

_BOTS_CLASSES = UBotAdapter.__subclasses__()
