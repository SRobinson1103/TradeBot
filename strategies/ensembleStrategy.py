from .baseStrategy import BaseStrategy
from collections import Counter

class EnsembleStrategy(BaseStrategy):
    # strategies: a list of BaseStrategy instances
    def __init__(self, strategies, name="Ensemble_Strategy"):
        super().__init__(name)
        self.strategies = strategies

    def on_bar(self, symbol: str, bar_data: dict) -> str:
        signals = []
        for strat in self.strategies:
            signal = strat.on_bar(symbol, bar_data)
            signals.append(signal)

        # Count frequency of signals
        counter = Counter(signals)
        if(len(counter) == 1):
            return list(counter.keys())[0]

        top_two = counter.most_common(2)
        if top_two[0][1] == top_two[1][1]:
            return "HOLD"
        
        return top_two[0][0]
