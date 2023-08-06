from logging import Logger

from buz.event import EventBus
from buz.event.kombu import EventNotPublishedException
from buz.event.transactional_outbox import OutboxRepository, OutboxCriteria, OutboxRecordToEventTranslator
from buz.event.transactional_outbox.outbox_criteria import OutboxSortingCriteria
from buz.locator import MessageFqnNotFoundException


class TransactionalOutboxWorker:
    def __init__(
        self,
        outbox_repository: OutboxRepository,
        outbox_record_to_event_translator: OutboxRecordToEventTranslator,
        event_bus: EventBus,
        logger: Logger,
    ):
        self.__outbox_repository = outbox_repository
        self.__outbox_record_to_event_translator = outbox_record_to_event_translator
        self.__event_bus = event_bus
        self.__logger = logger

    def start(self) -> None:
        criteria = OutboxCriteria(delivered_at=None, order_by=OutboxSortingCriteria.CREATED_AT)
        for outbox_record in self.__outbox_repository.find(criteria):
            try:
                event = self.__outbox_record_to_event_translator.translate(outbox_record)

                self.__event_bus.publish(event)
                outbox_record.mark_as_delivered()

            except (EventNotPublishedException, MessageFqnNotFoundException, Exception) as e:
                self.__logger.exception(e)
                outbox_record.mark_delivery_error()

            self.__outbox_repository.save(outbox_record)
