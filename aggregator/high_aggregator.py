from aggregator.base_aggregator import BaseAggregator


class HighAggregator(BaseAggregator):
    def __init__(self, store):
        super().__init__(store, "high")
