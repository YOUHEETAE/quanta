from aggregator.base_aggregator import BaseAggregator


class LowAggregator(BaseAggregator):
    def __init__(self, store):
        super().__init__(store, "low")
