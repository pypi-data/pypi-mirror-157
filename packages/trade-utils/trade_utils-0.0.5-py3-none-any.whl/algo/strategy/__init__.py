from typing import Dict, List, Tuple

from .common import StrategyDescriptor
from .moving_averages import MAStrategyParams
from .moving_averages import act as MovingAverageStrategy

# all strategies put together:
# (yes it can be dynamic, I just like it this way)
moving_average_sample: StrategyDescriptor = StrategyDescriptor(
    'sample-moving-average',
    MovingAverageStrategy,
    MAStrategyParams,
    'Simple moving averages'
)

# STRATEGIES_REGISTER: Final[Tuple[StrategyDescriptor]] = ( # Final will get on board at python3.8
STRATEGIES_REGISTER: Tuple[StrategyDescriptor] = (
    moving_average_sample,
)
