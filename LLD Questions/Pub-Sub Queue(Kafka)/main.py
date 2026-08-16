"""
Pub-Sub Message Queue System (Kafka-like) - LLD Skeleton
    ----------------------------------------------------------
    Scope for this version (state these assumptions out loud in an interview):
    - In-memory only (no persistence to disk)
    - Multiple topics, each with multiple partitions
    - Multiple producers/consumers
    - Consumer groups: each group gets every message; within a group,
    each partition is owned by at most one consumer (simple round-robin assignment)
    - At-least-once delivery, ordering guaranteed only within a partition
    - Pull-based consumption (consumer calls poll())
"""

import threading
import time
import uuid
from collections import defaultdict
from typing import List, Dict, Optional

# ---------------------------------------------------------------------------
# 1. Core data class
# ---------------------------------------------------------------------------

class Message:
    def __init__(self, key: str, val: str):
        self.id = str(uuid.uuid4())
        self.key = key
        self.val = val
        self.timestamp = time.time()
        self.offset: Optional[int] = None       # Assigned by the partition on append

# ---------------------------------------------------------------------------
# 2. Partition - append-only log, thread-safe
# ---------------------------------------------------------------------------

class Partition:
    def __init__(self, partition_id: int):
        self.partition_id = partition_id
        self.log: List[Message] = []
        self.lock = threading.Lock()

    def append(self, msg: Message) -> int:
        with self.lock:
            msg.offset = len(self.log)
            self.log.append(msg)
            return msg.offset

    def read(self, from_offset: int, max_msgs: int = 10) -> List[Message]:      
        # from_offset means start from this (eg: arr[2:x]) and max_msgs mean from 2 till what?(ex: x so arr[2:2+x])
        # Use lock so that no one publishses when we read (avoids reading a half-updated list)
        with self.lock:
            return self.log[from_offset: from_offset+max_msgs]

    def size(self) -> int:
        with self.lock:
            return len(self.log)

# ---------------------------------------------------------------------------
# 3. Topic - collection of partitions
# ---------------------------------------------------------------------------
 
class Topic:
    def __init__(self, name: str, partitions: int = 3):
        self.name = name
        self.partitions: List[Partition] = [Partition(i) for i in range(partitions)]

    def get_partition_for_key(self, key: int) -> Partition:
        # Simple hash-based routing -> guarantees ordering per key
        # hash converts the str into int and % keeps it within bound
        ind = hash(key) % len(self.partitions)
        return self.partitions[ind]

    def total_partitions(self) -> int:
        return len(self.partitions)

# ---------------------------------------------------------------------------
# 4. Producer
# ---------------------------------------------------------------------------

class Producer:
    def __init__(self, broker: "Kafka"):
        self.broker = broker

    def publish(self, topic_name: str, key: str, val: str) -> Message:
        topic = self.broker.get_topic(topic_name)
        partition = topic.get_partition_for_key(key)
        msg = Message(key, val)
        partition.append(msg)
        return msg

# ---------------------------------------------------------------------------
# 5. Consumer Group - tracks per-partition offsets, assigns partitions to consumers
# ---------------------------------------------------------------------------

class ConsumerGroup:
    def __init__(self, group_id: int, topic: Topic):
        self.group_id = group_id
        self.topic = topic
        # key = partition_id, value = the offset up to which this consumer group has read that partition
        self.offsets: Dict[int, int] = {p.partition_id: 0 for p in topic.partitions}
        self.offset_lock = threading.Lock()
        self.members: List["Consumer"] = []
        self.assignment: Dict[str, List[Partition]] = {}    # It states which consumer will look whih partition (Helpful for rebalancing)

    def join(self, consumer: "Consumer"):
        self.members.append(consumer)
        self.rebalance_consumer()

    def leave(self, consumer: "Consumer"):
        self.members = [c for c in self.members if c.consumer_id != consumer.consumer_id]
        self.rebalance()

    def rebalance_consumer(self):
        # Simple round-robin partition assignment across current members
        self.assignment = {c.consumer_id: [] for c in self.members}
        if not self.members:
            return 
        for i, partition in enumerate(self.topic.partitions):
            owner = self.members[i%len(self.members)]
            self.assignment[owner.consumer_id].append(partition)

    def get_assigned_partitions(self, consumer_id: str) -> List[Partition]:
        return self.assignment.get(consumer_id, [])

    def get_offset(self, partition_id) -> int:
        with self.offset_lock:
            return self.offsets[partition_id]

    def commit_offset(self, partition_id: int, offset: int):
        with self.offset_lock:
            self.offsets[partition_id] = offset

# ---------------------------------------------------------------------------
# 6. Consumer
# ---------------------------------------------------------------------------

class Consumer:
    def __init__(self, consumer_id: str, group: ConsumerGroup):
        self.consumer_id = consumer_id
        self.group = group
        self.group.join(self)

    def poll(self, max_msgs: int = 10) -> List[Message]:
        results = []
        for partition in self.group.get_assigned_partitions(self.consumer_id):
            offset = self.group.get_offset(partition.partition_id)
            msgs = partition.read(offset, max_msgs)
            if msgs:
                results.extend(msgs)
                new_offset = msgs[-1].offset + 1
                self.group.commit_offset(partition.partition_id, new_offset)
        return results

# ---------------------------------------------------------------------------
# 7. Broker - facade tying everything together
# ---------------------------------------------------------------------------

class MessageBroker:    # (eg: Kafka, SQS)
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.consumer_groups: Dict[str, Dict[str, ConsumerGroup]] = defaultdict(dict)
        self.lock = threading.Lock()

    def create_topic(self, name: str, num_of_partitions: int) -> Topic:
        with self.lock:
            if name not in self.topics:
                self.topics[name] = Topic(name, num_of_partitions)
            return self.topics[name]

    def get_topic(self, name: str) -> Topic:
        if name not in self.topics:
            raise ValueError(f"Topic '{name}' does not exist")
        return self.topics[name]

    def get_producer(self) -> Producer:
        return Producer(self)

    def get_consumer(self, topic_name: str, group_id: str, consumer_id: str) -> Consumer:
        topic = self.get_topic(topic_name)
        if group_id not in self.consumer_groups[topic_name]:
            self.consumer_groups[topic_name][group_id] = ConsumerGroup(group_id, topic)
        group = self.consumer_groups[topic_name][group_id]
        return Consumer(consumer_id, group)

# ---------------------------------------------------------------------------
# 8. Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    broker = MessageBroker()
    broker.create_topic("orders", 3)

    producer = broker.get_producer()
    for i in range(6):      # Publishing 6 msgs
        producer.publish("orders", key=f"user-{i % 3}", val=f"order-{i}")

    c1 = broker.get_consumer("orders", "analytics", "c1")
    c2 = broker.get_consumer("orders", "analytics", "c2")

    c3 = broker.get_consumer("orders", "audit", "c3")

    print("Consumer c1 (analytics group):", c1.poll())
    print("Consumer c2 (analytics group):", c2.poll())
    print("Consumer c3 (audit group):", c3.poll())