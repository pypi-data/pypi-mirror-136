import unittest

from ubotadapter.manager import *
from ubotadapter.test.test_tools import *


class DublicateReplyInboundProcessor(InboundProcessor):
    @staticmethod
    def process(context: BotContext, inbound: InboundMessage):
        text = 'test_duplicate'
        for i in range(5):
            context.replies.add_text(text)


class TestBotsReplies(unittest.TestCase):
    def test_dtf_bot(self):
        for bot_test in BOTS_LIBRARY:
            if bot_test.channel != ChannelType.DTF:
                continue
            bot = bot_test.bot
            with self.subTest(bot=bot.channel.name):
                bot.set_inbound_processor(DublicateReplyInboundProcessor)
                for message_getter in bot_test.all_message_getters:
                    result = bot.handle(message_getter.get_message())
                    self.assertTrue(result.is_ok, msg=result.report())
                    self.assertFalse(result.no_replies)
