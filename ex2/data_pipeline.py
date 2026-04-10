from abc import ABC, abstractmethod
from typing import Any, Protocol
import typing


class DataProcessor(ABC):
    def __init__(self) -> None:
        self.storage: list[str] = []
        self.counter: int = 0
        self.total: int = 0

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
            self.total += 1
        elif isinstance(data, list):
            for x in data:
                self.storage.append(str(x))
                self.total += 1


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
            self.total += 1

        elif isinstance(data, list):
            for x in data:
                self.storage.append(x)
                self.total += 1


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
            self.total += 1

        elif isinstance(data, list):
            for x in data:
                self.storage.append(x['log_level'] + ": " + x['log_message'])
                self.total += 1


class ExportPlugin(Protocol):
    def process_output(self, data: list[tuple[int, str]]) -> None:
        pass


class CSVExporter:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        values: list = []
        for element in data:
            rank, value = element
            values.append(value)
        values_union = ",".join(values)
        print("CSV Output:")
        print(f"{values_union}")


class JSONExporter:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        items: list[str] = []
        for item in data:
            rank, value = item
            items.append(f'"item_{rank}": "{value}"')
        json_string = "{" + ", ".join(items) + "}"
        print("JSON Output:")
        print(f"{json_string}")


class DataStream():
    def __init__(self) -> None:
        self.processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        self.processors.append(proc)

    def process_stream(self, stream: list[typing.Any]) -> None:
        for element in stream:
            processed = False
            for proc in self.processors:
                if proc.validate(element):
                    proc.ingest(element)
                    processed = True
            if not processed:
                print(f"DataStream error - "
                      f"Can't process element in stream: {element}")

    def print_processors_stats(self) -> None:
        print("== DataStream statistics ==")
        if not self.processors:
            print("No processor found, no data")
        else:
            for proc in self.processors:
                name = type(proc).__name__.replace("Processor", " Processor")
                total = proc.total
                remaining = len(proc.storage)
                print(f"{name}: total {total} items processed, "
                      f"remaining {remaining} on processor")

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        for proc in self.processors:
            results: list = []
            for x in range(nb):
                if proc.storage:
                    element = proc.output()
                    results.append(element)
            plugin.process_output(results)


def main() -> None:
    print("=== Code Nexus - Data Pipeline ===\n")

    print("Initialize Data Stream...\n")

    stream = DataStream()
    stream.print_processors_stats()

    print("\nRegistering Processors\n")

    numeric = NumericProcessor()
    text = TextProcessor()
    log = LogProcessor()
    stream.register_processor(numeric)
    stream.register_processor(text)
    stream.register_processor(log)

    batch = [
        'Hello world',
        [3.14, -1, 2.71],
        [
            {
                'log_level': 'WARNING',
                'log_message': 'Telnet access! Use ssh instead'
            },
            {
                'log_level': 'INFO',
                'log_message': 'User wil is connected'
            }
        ],
        42,
        ['Hi', 'five']
    ]
    print(f"Send first batch of data on stream: {batch}\n")
    stream.process_stream(batch)

    stream.print_processors_stats()

    print("\nSend 3 processed data from each processor to a CSV plugin:")
    csv = CSVExporter()
    stream.output_pipeline(3, csv)
    print("")

    stream.print_processors_stats()

    new_batch = [
        21,
        ['I love AI', 'LLMs are wonderful', 'Stay healthy'],
        [
            {
                'log_level': 'ERROR',
                'log_message': '500 server crash'
            },
            {
                'log_level': 'NOTICE',
                'log_message': 'Certificate expires in 10 days'
            }
        ],
        [32, 42, 64, 84, 128, 168],
        'World hello'
    ]

    print(f"\nSend another batch of data: {new_batch}\n")
    stream.process_stream(new_batch)

    stream.print_processors_stats()

    print("\nSend 5 processed data from each processor to a JSON plugin:")
    json = JSONExporter()
    stream.output_pipeline(5, json)
    print("")

    stream.print_processors_stats()


if __name__ == "__main__":
    main()
