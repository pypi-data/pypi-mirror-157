# Gymmick

A library offering simple functionality for the creation of simple visuals-based OpenAI Gym environments.

## Description

The purpose of this library is to create an easier way for users to make custom visual-based environments compatible with OpenAI Gym. Along with the basics of any Gym environment (ENV class and defining functions), the library will contain special functions to make
state handling (for observation creation) easier as well as a predefined visualization tool which can be activated upon request 
(by changing a default argument when creating an environment instance). If the user does not want a visual/physics-based environment, 
they can opt to add their own variables to an optional argument dictionary when instantiating the class and have complete freedom
with the manipulation of the values in said dictionary as the states of the environment change.

This library is not an advanced tool, but provides users freedom to do (almost) whatever they want in their environment. Flexibility for some environment functions is a priority and pending features include:

 - `Functions for Collision Detection`
 - `Gravity for Members of the Environment`
 - `Visibility and "Tangibility" of Environment Members`
 - `Support for Irregular Polygons`
 - `Rotation of Environment Members`

## Installation

To install, simply use the command:
```python
pip install gymmick
```

## Usage

### Import

```python
from gymmick import creategym
from gymmick import members
```

### Create an Environment

To create an environment, you must also have created a ```handler``` function and know the details of the environment (action/observation space, episode length, using a screen, etc.). Here is the ```__init__()``` function's parameters for the ```creategym.FreeSpaceEnv``` class:
```python
def __init__(self, action_space, observation_space, length, _handler, color = (0, 0, 0), scr=False, **kwargs)
```

Note: If you wish to be able to utilize the screen for the above class, then initialize the environment with ```scr=(<screen width>, <screen height>)```.

and here is the ```GridworldEnv.__init__()``` parameters:

```python
def __init__(self, action_space, observation_space, length, _handler, table_dim, color = (0, 0, 0), **kwargs)
```

Note: If you wish to be able to utilize the screen for the above class, then initialize the ```table_dim``` parameter with ```((<number of rows>, <row height>), (<number of columns>, <column width>))```. Both ```<number of rows>``` and ```<number of columns>``` must be at least 1. If ```<row height>``` or ```<column width>``` is 0, then the environment will not be instantiated with a screen, but the grid (and its variables) will still be accessible.

Here are examples of instantiating both environments, with handler functions, and other class parameters already in place:

```python
def first(action):
    prev = agent1.x
    agent1.change_attr(x=agent1.x+(action-1))
    done = False
    if agent1.x == goal1.x:
        reward = 1
        done = True
    elif (abs(agent1.x-goal1.x)<abs(prev-goal1.x)):
        reward = 1
    else:
        reward = -1 
    observation = goal1.x-agent1.x
    return observation, reward, done, {}

def second(action):
    prev = agent2.col
    agent2.change_attr(col = agent2.col+(action-1))
    done = False
    if agent2.col == goal2.col:
        reward = 1
        done = True
    elif abs(agent2.col-goal2.col)<abs(prev-goal2.col):
        reward = 1
    else:
        reward = -1
    observation = goal2.col-agent2.col
    return observation, reward, done, {}

action = spaces.Discrete(3)
observation1 = spaces.Box(low = np.array([-1500]), high = np.array([1500]))
observation2 = spaces.Box(low = np.array([-15]), high = np.array([15]))
env = FreeSpaceEnv(action, observation1, 1500, first, scr = (1000, 1000))
grid = GridworldEnv(action, observation2, 100, second, ((20, 25), (15, 37)))
```

### Adding members to environments

To add members to environments, instantiate them from the ```gymmick.members``` class with appropriate init parameters:

```python
gymmick.members.FreeSpaceRect(<x>, <y>, <width>, <height>, <horizontal  velocity>, <vertical velocity>, <mass>, <RGB color tuple>)
gymmick.members.CellRect(<row>, <column>, <horizontal  velocity>, <vertical velocity>, <mass>, <RGB color tuple>)
gymmick.members.Circle(<x>, <y>, <radius>, <horizontal  velocity>, <vertical velocity>, <mass>, <RGB color tuple>)
```

Note: Currently, the velocity parameter does not have any effect on the environment or object. Therefore, whatever ```vy``` or ```vx``` is instantiated is irrelevant, unless the user is using these variables in their own handler functions. Functionality for velocity is coming soon.

Note: ```FreeSpaceRect``` and ```Circle``` can only be used in the ```FreeSpaceEnv``` environment, while ```CellRect``` can only be used in the ```GridEnv``` environment.

Note: ```CellRect``` can have ```<row>``` and ```<col>``` values outside the bounds of its environment (they will just remain in a seperate array outside of the main table). Depending on how the user manipulates this object, it can switch its presence between ```GridEnv.table``` and ```GridEnv.outside```.

Also, make sure to create a copy of the member variables so that they can be reset at the end of each episode. There will be future updates to the library in which users will not have to continuously re-add these members to the environment:

```python
agent1_copy = FreeSpaceRect(0, 500, 50, 50, 0, 0, 0, (255, 0, 0))
agent2_copy = CellRect(10, 0, 0, 0, 0, (255, 0, 0))
goal1_copy = FreeSpaceRect(427, 500, 50, 50, 0, 0, 0, (0, 255, 0))
goal2_copy = CellRect(10, 11, 0, 0, 0, (0, 255, 0))
```
To add a member to the environt, use the environment's built-in method:

```python
env.add_member(agent1)
env.add_member(goal1)
grid.add_member(agent2)
grid.add_member(goal2)
```

### Run the environment

To run (and view) the ```grid``` environment, run the following code:

```python
for _ in range(<number of episodes>):
    total_reward = 0
    while True:
        action = grid.action_space.sample()
        obs, reward, done, info = grid.step(action)
        total_reward += reward
        grid.render()
        if done == True:
            break
    print(total_reward)
    grid.reset()
    agent2 = agent2_copy
    goal2 = goal2_copy
    grid.add_member(agent2)
    grid.add_member(goal2)
```
Similarly, you can run the ```env``` environment by substituting its name for ```grid``` in the above example.