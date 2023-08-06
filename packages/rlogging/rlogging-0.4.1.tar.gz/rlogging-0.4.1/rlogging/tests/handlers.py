from rlogging.handlers import Handler
from rlogging.records import Record


class PytestLoggingHandler(Handler):

    records_list: list

    def __init__(self, records_list) -> None:
        self.records_list = records_list
        super().__init__()

    def processing(self, record: Record):
        self.records_list.append(record)
        return record
