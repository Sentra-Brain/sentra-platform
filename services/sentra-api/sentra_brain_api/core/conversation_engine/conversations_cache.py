# sentra_brain_api/core/conversation_engine/conversations_cache.py
from collections import defaultdict, OrderedDict
from threading import Lock
from sentra_brain_api.core.constants import USER_CONVERSATION_CACHE_SIZE

class ConversationsCache:
    def __init__(self, capacity=USER_CONVERSATION_CACHE_SIZE, on_evict=None):
        """
        :param capacity: Max number of conversations per user
        :param on_evict: Optional callback called with (user_id, conversation_id, value) when evicted
        """
        self.capacity = capacity
        self.on_evict = on_evict
        self.user_conversations = defaultdict(OrderedDict)
        self._lock = Lock()

    def get(self, user_id, conversation_id):
        with self._lock:
            conversations = self.user_conversations[user_id]
            if conversation_id not in conversations:
                return None
            conversations.move_to_end(conversation_id)
            return conversations[conversation_id]

    def put(self, user_id, conversation_id, value):
        with self._lock:
            conversations = self.user_conversations[user_id]
            if conversation_id in conversations:
                conversations.move_to_end(conversation_id)
            conversations[conversation_id] = value

            if len(conversations) > self.capacity:
                evicted_id, evicted_value = conversations.popitem(last=False)
                if self.on_evict:
                    self.on_evict(user_id, evicted_id, evicted_value)
