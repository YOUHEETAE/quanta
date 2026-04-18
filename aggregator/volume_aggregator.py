from aggregator.base_aggregator import BaseAggregator


class VolumeAggregator(BaseAggregator):
    def __init__(self, store):
        super().__init__(store, "volume")
