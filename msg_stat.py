import re


class Conversation:
    patterns = {

    }

    def __init__(self, chat_id, chat_name):
        self.chat_id = chat_id
        self.chat_name = chat_namename

    def register(self, msg):
        pass


class ConversationMember(Conversation):
    def __init__(self, chat_id, chat_name, member_id, member_name):
        super().__init__(self, chat_id, chat_name)
        self.member_id = member_id
        self.member_name = member_name

    def count_msg(self):
        pass

# ConversationMember(1, 'helsso', 123, 'rashid')
# print(ConversationMember.chat_id)

try:
    1/0
except Exception as e:
    print(e)
