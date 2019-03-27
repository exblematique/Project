# Installation
Make sure you have pip installed. Run `pip2 install -r requirements.txt` from the root of the project to install the modules that are required by Python. The requirements.txt file contains all the modules that the software needs.

To run the application just execute `sudo python2 smart_grid_app.py` from the root of the project. Sudo is needed to access `/dev/ttyMySensorsGateway`, and should probably be fixed in the future.

# REST API
The application contains a REST API so it can be controlled by external applications. It's documented in the file [API.md](API.md).

# Grid
The way the flows are generated is by using a grid. This is a total rewrite of the old system of the smart grid table. Basic keywords are graph theory, vertice, nodes and A-Star pathfinding.

## Basic theory
A node is a point on the table which is represented by a X-coordinate and Y-coordinate, in that order. Starting from the top left, represented by `(0, 0)`, node `(4, 3)` is a point on the table which is 4 to the right and 3 down from the top left.
In Python a node is represented as the object 'tuple', which can be compared to an array with 2 elements in it, the only difference is that a tuple is immutable. 


## Table sections
### Layout
| Symbol      | Meaning
| ----------- | -------
| `x`         | A node where a module can be placed
| `—` and `|` | A single flow segment
| `=`         | Two flow segments that represent the same flow

#### Table section 1
```
      |
   x — — x
   |     |
x —       — x
   |     |
   x — — x
      |
```

#### Table section 2
```
x —
   |
   |
x — = = x
   |
   |
x —
```

### Modules
| Position ID | Point
| ----------- | ----------
| 0           | `[0, 2]`
| 1           | `[1, 1]`
| 2           | `[3, 1]`
| 3           | `[4, 2]`
| 4           | `[3, 3]`
| 5           | `[1, 3]`

#### Table section 1
```
             |
   [1,1]> x — — x <[3,1]
          |     |
[0,2]> x —       — x <[4,2]
          |     |
   [1,3]> x — — x <[3,3]
             |
```


## How to register flow segments to the grid?
Lets say you want to have a new table section which looks like the following:

Each flow segment internally has an id. If there are 10 LED-strips registered on the Arduino, then the ids are 0 through 9. These flow segments should be registered in order.

A normal flow segment should be registered with an instance of `FlowSegment`. A flow segment that is connected to another flow segment that is NOT on the same table section should be registered with `NeighborFlowSegment`. This differentiation is because the Python-code checks the instance type to know if a flow segment is attached to a flow segment of another table section.

The flow segments should be registered in the file table_section.py. Here is an example of table type 1:

```python
if table_type == 1:
    self.flows = [
        FlowSegment((0, 2), (1, 2)),
        FlowSegment((1, 2), (1, 1)),
        FlowSegment((1, 1), (2, 1)),
        NeighborFlowSegment((2, 1), (2, 0)),
        FlowSegment((2, 1), (3, 1)),
        FlowSegment((3, 1), (3, 2)),
        FlowSegment((3, 2), (4, 2)),
        FlowSegment((3, 2), (3, 3)),
        FlowSegment((3, 3), (2, 3)),
        NeighborFlowSegment((2, 3), (2, 4)),
        FlowSegment((2, 3), (1, 3)),
        FlowSegment((1, 3), (1, 2))
    ]
```

The locations of where a module is placed on the grid should be set in [settings.py](settings.py), in the variable `TABLE_PART`. Please notice that these positions SHOULD NOT take the position of the table section into account. Read paragraph [How to change the position of a table section?](#how-to-change-the-position-of-a-table-section) to see how to change the starting position of a table section.

## how to improve neighbouring tables
Currently the neighboring tables endpoint gets the neighbouring tables from the tableConfig file where it is hardcoded. This can be improved by creating a function that dynamically gives back the neighbours.

## How to change the pathfinding algorithm?
There are two branches for two different pathfinding algorithms. These three are:
- grid-master
- grid-match

To switch to an other branch, use the following command in terminal:
```shell
git checkout [BRANCH]
```

For example:
```shell
git checkout grid-match
```

The grid master makes consuming modules search for the nearest producing modules. The other one is grid-match, which will traverse modules to see if the nearest relevant module of the nearest relevant module of that module is equal to that module. In simpler words, lets take the following example:

- Module A
- Module B
- Module C

The distance between A-B is 2, the distance between A-C is 3 and the distance between B-C is 1. The matching asks module A: what is the closest module that is relevant to you? It will answer with B, as 2 (A-B) < 3 (A-C). Then it will ask the same question to B, however B answers with C, as 1 (B-C) < 2 (A-B). This will make the traversion continue, as it will ask C what the closest relevant module is. It will answer with B, because 1 (B-C) < 3 (A-C). As B answers that the closest module is C, and C answers that the closest module is B, they have matched together and will have energy flowing. This loop will continue until there are no matches to be made anymore, as there is no power to deliver anymore, or the modules that are left have no way to reach other modules.

## How to change the position of a table section?
To change the position of a table section, you have to go to the [config/tableConfig.json](config/tableConfig.json) file. Each table section is added to this configuration file. To change the position, you have to set the `startingPosition` of the table section you want to change. This will make the starting point of the table section different which will also adjust the position of the flow segments. For example, lets say you have a diagonal flow segment going from `(1, 1)` to `(2, 2)`. If your table section starts at `(0, 0)`, then the flow segment will start at `(1, 1)`. When you change the table section to start at `(5, 5)`, the flow segment will start at `(6, 6)` and go to `(7, 7)`.

# The software on the Raspberry Pi
Currently this software is being ran on a Raspberry Pi. The Raspberry Pi which this software is installed runs on Raspbian and contains the Git repository under folder `~/smartgrid/Python`. The Raspberry Pi is using the shell `fish`, which means that whenever you go to the project directory in the terminal, you will see, next to the current directory, a branch icon. If you are on the master branch, you would only see a branch icon, otherwise you would also see the name of the branch. If the local repository is equal to the remote repository, the background where the branch is shown is green. For more information, read ['The Prompt' of theme 'bobthefish'](https://github.com/oh-my-fish/theme-bobthefish/blob/master/README.md#the-prompt).

# Future
To improve performance in the future, there are a few different options, listed below:

## Use multiprocessing to use all processing power
Currently a very small bit of multiprocessing is implemented but this could be inproved.
The current script does not use threads for the main pathfinding, as the pathfinding can not easily be done in multiple threads. It can not easily be done in multiple threads for the following reason:
- The pathfinding is dependant on the direction of the flow segments.
- The reduction and increment of power of modules is harder with multiple threads as you have to take account which thread gets priority.

## Move the Python-software from the Raspberry Pi to a more powerful device
Calculating the grid currently uses 100 percent of a single processor of the Raspberry Pi, meaning the processor is using its full strength. Other hardware could be more capable of running the Python-software.

### How can this be done?
The Python-software is MOSTLY cross-platform. The only thing that is not cross-platform is the reading of the serial connection. The library that is being used for that is [MySensors](https://www.mysensors.org/). The Python-software is reading the serial connection through psuedo-terminal `/dev/ttyMySensorsGateway`. To move the Python-software to a different device, one should probably do the following:
- Check if there is compability between the device you want to run the Python-software on and the MySensors library.
- Potentially rewrite the receiving of data as `/dev/ttyMySensorsGateway` might be something of the deprecated [MySensors Raspberry Port](https://github.com/mysensors/Raspberry).

Another solution is to write a small Python-script that is being run on the Raspberry Pi that reads `/dev/ttyMySensorsGateway`, and sends that data over to another device that do all other things. That other device should then send over the serial information to the Raspberry Pi, which then uses MySensors to send it over to the Arduino.

