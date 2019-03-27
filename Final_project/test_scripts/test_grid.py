import sys

from flow_segment import FlowSegment
from grid import Grid
from table_section import TableSection

sys.path.append("../")

# Create grid for testing
grid = Grid(None)
tablesection = TableSection(0, 1, (0, 0))
flows = tablesection.get_flows()

for flow in flows:
    grid.add_flow_segment(flow)


def test_distance_between_correct():
    """
    Test if the distance_between method uses the correct formula to calculate distance between two points
    """
    node1 = (1, 1)
    node2 = (2, 3)
    # Distance between 1,1 and 2,3 = square root of 1*1+2*2 (5) according to
    # Pythagoras
    assert grid.distance_between(node1, node2) == 5 ** 0.5


def test_get_neighbour_works():
    """
    Test if correct neighbours are returned for top-left node for table type 1.
    """
    node = (1, 1)
    assert grid.neighbors(node) == [(2, 1), (1, 2)]


def test_get_flow_segment():
    """
    Test if a flow segment is returned when you want to retrieve an existing flow segment by start- and endpoints
    """
    assert isinstance(grid.flow_find_segments((0, 0), (1, 1))[0], FlowSegment)


def test_get_no_flow_segment():
    """
    Test if no flow segment is returned when you use points of a non-existing flow segment
    """
    assert len(grid.flow_find_segments((2402, 141), (5151, 566))) is 0
