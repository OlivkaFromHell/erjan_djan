import re


class Conversation:
    patterns = {

    }

    def __init__(self, chat_id, chat_name):
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.amount_msg = 0


class ConversationMember(Conversation):
    def __init__(self, chat_id, chat_name, member_id, member_name):
        super().__init__(chat_id, chat_name)
        self.member_id = member_id
        self.member_name = member_name
        self.member_amount_msg = {
            'total': 0,
            'audio_msg': 0,
            'audio': 0,
            'video': 0,
            'explicit': 0
        }

    def count_msg(self):
        # some message handling
        self.amount_msg += 1
        self.member_amount_msg += 1


a = ConversationMember(1, 'helsso', 123, 'rashid')
print(a.__dict__)

if __name__ == '__main__':
    print('hello')
