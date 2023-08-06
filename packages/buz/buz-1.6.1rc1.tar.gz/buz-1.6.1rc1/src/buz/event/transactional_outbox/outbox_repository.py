from abc import ABC, abstractmethod
from typing import Iterable

from buz.event.transactional_outbox import OutboxRecord
from buz.event.transactional_outbox import OutboxCriteria


class OutboxRepository(ABC):
    @abstractmethod
    def save(self, outbox_record: OutboxRecord) -> None:
        pass

    @abstractmethod
    def find(self, criteria: OutboxCriteria) -> Iterable[OutboxRecord]:
        pass
