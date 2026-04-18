from aggregator.base_aggregator import BaseAggregator


class OpenAggregator(BaseAggregator):
    def __init__(self, store):
        super().__init__(store, "open")
