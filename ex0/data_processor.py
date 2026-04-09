from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    def __init__(self) -> None:
        self.storage: list[str] = []
        self.counter: int = 0

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        if not self.storage:
            return (self.counter, "No data available")
        data = self.storage.pop(0)
        rank = self.counter
        self.counter += 1
        return (rank, data)


class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, (int, float)):
            return True
        elif isinstance(data, list):
            return all(isinstance(x, (int, float)) for x in data)
        else:
            return False

    def ingest(self, data: int | float | list[int | float]) -> None:
        if not self.validate(data):
            raise ValueError("Improper numeric data")
        elif isinstance(data, (int, float)):
            self.storage.append(str(data))
        elif isinstance(data, list):
            for x in data:
                self.storage.append(str(x))


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True
        elif isinstance(data, list):
            return all(isinstance(x, str) for x in data)
        else:
            return False

    def ingest(self, data: str | list[str]) -> None:
        if not self.validate(data):
            raise ValueError("Improper text data")
        elif isinstance(data, str):
            self.storage.append(data)
        elif isinstance(data, list):
            for x in data:
                self.storage.append(x)


class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, dict):
            return True
        elif isinstance(data, list):
            return all(isinstance(x, dict) for x in data)
        else:
            return False

    def ingest(self, data: dict | list[dict]) -> None:
        if not self.validate(data):
            raise ValueError("Improper log data")
        elif isinstance(data, dict):
            self.storage.append(data['log_level'] + ": " + data['log_message'])
        elif isinstance(data, list):
            for x in data:
                self.storage.append(x['log_level'] + ": " + x['log_message'])


def main() -> None:
    print("=== Code Nexus - Data Processor ===")

    print("\nTesting Numeric Processor...")
    numeric = NumericProcessor()
    print(f" Trying to validate input '42': {numeric.validate(42)}")
    print(f" Trying to validate input 'Hello': {numeric.validate('Hello')}")
    print(" Test invalid ingestion of string 'foo' without prior validation:")
    try:
        numeric.ingest("foo")
    except ValueError as e:
        print(f" Got exception: {e}")
    numeric_value: list[int | float] = [1, 2, 3, 4, 5]
    numeric.ingest(numeric_value)
    print(f" Processing data: {numeric_value}")
    print(" Extracting 3 values...")
    for x in range(3):
        rank, value = numeric.output()
        print(f" Numeric value {rank}: {value}")

    print("\nTesting Text Processor...")
    text = TextProcessor()
    print(f" Trying to validate input 'Hello': {text.validate('Hello')}")
    print(f" Trying to validate input '42': {text.validate(42)}")
    print(" Test invalid ingestion of int '123' without prior validation:")
    try:
        text.ingest(123)
    except ValueError as e:
        print(f" Got exception: {e}")
    text_value = ["Hello", "Nexus", "World"]
    text.ingest(text_value)
    print(f" Processing data: {text_value}")
    print(" Extracting 1 value...")
    for x in range(1):
        rank, value = text.output()
        print(f" Text value {rank}: {value}")

    print("\nTesting Log Processor...")
    log = LogProcessor()
    example_log = {'log_level': 'INFO', 'log_message': 'System Clear'}
    print(f" Trying to validate input 'dict': {log.validate(example_log)}")
    print(f" Trying to validate input 'Hello': {log.validate("Hello")}")
    print(" Test invalid ingestion of list of ints without prior validation:")
    try:
        log.ingest([1, 2, 3])
    except ValueError as e:
        print(f" Got exception: {e}")
    log_value = [
        {'log_level': 'NOTICE', 'log_message': 'Connection to server'},
        {'log_level': 'ERROR', 'log_message': 'Unauthorized access!!'}
    ]
    log.ingest(log_value)
    print(f" Processing data: {log_value}")
    print(" Extracting 2 values...")
    for x in range(2):
        rank, value = log.output()
        print(f" Log entry {rank}: {value}")


if __name__ == "__main__":
    main()
