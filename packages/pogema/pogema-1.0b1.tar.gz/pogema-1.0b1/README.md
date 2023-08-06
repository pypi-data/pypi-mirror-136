# Pogema environment

## Installation

Just install from PyPI:

```pip install pogema```

## Using Example


```python
import gym
from pogema.grid_config import GridConfig
from pogema.wrappers.multi_time_limit import MultiTimeLimit
from pogema.animation import AnimationMonitor

env = gym.make('Pogema-v0', config=GridConfig(num_agents=2, size=8))
env = MultiTimeLimit(env, max_episode_steps=64)
env = AnimationMonitor(env)

obs = env.reset()

done = [False, ...]
while not all(done):
    obs, reward, done, info = env.step([env.action_space.sample() for _ in range(env.config.num_agents)])
```