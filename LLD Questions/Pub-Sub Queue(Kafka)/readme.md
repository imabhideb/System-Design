# Pub-Sub Message Queue System (Kafka-like) — LLD

An in-memory, Kafka-inspired publish-subscribe message queue built to practice
Low-Level Design. Supports multiple topics, partitioned logs, multiple
producers, and consumer groups with independent offset tracking.

## Scope / Assumptions

- In-memory only — no disk persistence
- Multiple topics, each split into multiple partitions
- Multiple producers and consumers
- Consumer groups: every group receives every message; within a group, each
  partition is owned by at most one consumer at a time
- At-least-once delivery
- Ordering is guaranteed only **within a partition**, not across the whole topic
- Pull-based consumption (`consumer.poll()`), not push/callback-based

## Components and How They Link Together

```
MessageBroker
 ├── topics: { topic_name -> Topic }
 └── consumer_groups: { topic_name -> { group_id -> ConsumerGroup } }

Topic
 └── partitions: [ Partition, Partition, ... ]

Partition
 └── log: [ Message, Message, ... ]   (append-only)

ConsumerGroup
 ├── offsets: { partition_id -> last_read_offset }
 ├── members: [ Consumer, Consumer, ... ]
 └── assignment: { consumer_id -> [ Partition, Partition ] }

Producer  --publishes to-->  Partition (via Topic)
Consumer  --polls from  -->  Partition (via ConsumerGroup's assignment)
```

### 1. `Message`
The unit of data. Holds a `key`, a `value`, a generated `id`, a `timestamp`,
and an `offset` — the offset is not set until the message is actually
appended to a partition (the partition assigns it).

### 2. `Partition`
An append-only log — just a Python list under a lock. This is the actual
source of truth for message order. Each partition is independently locked,
so writes to different partitions never block each other.

- `append(message)` — adds a message, assigns it the next offset (its index
  in the list), returns that offset.
- `read(from_offset, max_messages)` — slices the log starting at
  `from_offset`, returns up to `max_messages` messages.

### 3. `Topic`
A named collection of partitions. This is where partitioning strategy lives:

- `get_partition_for_key(key)` — hashes the key and mods by partition count
  to pick a partition deterministically. Same key always routes to the same
  partition, which is what guarantees ordering *for that key*.

### 4. `Producer`
Holds a reference to the `MessageBroker` (passed in at construction) so it
can look up topics by name. `publish(topic_name, key, value)`:
1. Looks up the `Topic` via the broker
2. Asks the topic which `Partition` this key belongs to
3. Creates a `Message` and appends it to that partition

### 5. `ConsumerGroup`
The coordination layer for a group of consumers reading the same topic.
Tracks two things per group:

- **Offsets** — how far each partition has been read *by this group*
  (`Dict[partition_id, offset]`). Different groups on the same topic have
  completely independent offsets — that's how one group can be "ahead" of
  another.
- **Assignment** — which consumer owns which partitions
  (`Dict[consumer_id, List[Partition]]`), decided by `rebalance()` using
  simple round-robin. Rebalance runs automatically whenever a consumer
  joins or leaves the group.

Within a group, each partition is assigned to exactly one consumer at a
time — this is what prevents two consumers in the same group from
processing the same message twice.

### 6. `Consumer`
Represents one reader. On construction, it immediately calls
`group.join(self)`, which registers it as a member and triggers a
rebalance. `poll()`:
1. Asks its group which partitions it currently owns
2. For each owned partition, reads new messages since the group's last
   committed offset for that partition
3. Commits the new offset back to the group so the next `poll()` doesn't
   re-read the same messages

### 7. `MessageBroker`
The facade tying everything together — the single entry point a client
interacts with.

- `create_topic(name, num_partitions)` — creates and stores a `Topic`
- `get_topic(name)` — looks up an existing topic
- `get_producer()` — hands back a `Producer` wired to this broker
- `get_consumer(topic_name, group_id, consumer_id)` — finds or creates the
  `ConsumerGroup` for that `(topic, group_id)` pair, then constructs and
  returns a `Consumer` already joined to it

## End-to-End Flow (Publish → Consume)

1. `broker.create_topic("orders", 3)` — creates a topic with 3 empty
   partitions.
2. `producer.publish("orders", key="user-0", value="order-0")` — the
   producer asks the broker for the topic, the topic hashes `"user-0"` to
   pick a partition, and the message is appended there with an assigned
   offset.
3. `broker.get_consumer("orders", "analytics", "c1")` — creates (or reuses)
   the `"analytics"` consumer group for topic `"orders"`, creates a
   `Consumer` named `"c1"`, and joins it to the group — triggering a
   rebalance that assigns it some subset of the topic's partitions.
4. `c1.poll()` — for each partition `c1` owns, read new messages since the
   group's last committed offset, return them, and advance the offset.
5. A second consumer, `c2`, in the **same** group splits the partitions with
   `c1` — together they process the full topic with no overlap.
6. A consumer `c3` in a **different** group (`"audit"`) gets its own
   independent offset tracking and sees *all* messages on the topic,
   regardless of what `"analytics"` has already consumed — this is the
   pub-sub property: every group gets a full copy of the stream.

## Known Limitations (worth stating out loud in an interview)

- **Rebalance timing** — because rebalance runs on every `join()`
  individually, a consumer that joins first can temporarily own more
  partitions than a "fair" split would give it, depending on when later
  consumers join.
- **Hash instability** — Python's `hash()` on strings is randomized per
  process run (`PYTHONHASHSEED`), so partition routing for a given key can
  differ between runs. A production system would use a stable hash (e.g.
  `hashlib.md5`) instead.
- **No persistence** — everything is lost when the process exits. A real
  system would use a write-ahead log or segment files on disk.
- **No replication / fault tolerance** — a single partition living in one
  process's memory has no redundancy.