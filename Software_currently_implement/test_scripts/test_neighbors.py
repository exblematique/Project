import sys

from grid import Grid
from table_section import TableSection

sys.path.append("../")

# Create grid for testing
grid = Grid(None)
tablesection = TableSection(0, 1, (0, 0))
flows = tablesection.get_flows()

for flow in flows:
    grid.add_flow_segment(flow)


def test_generate_colliding_path():
    """
    Test if second_path does not go through first_path, as direction of the flow segment of first_path are set forwards.
    """
    grid.reset()
    first_path = grid.generate_path((2, 2), (4, 3))
    print(first_path)
    assert first_path[0] == (2, 2)
    assert first_path[-1] == (4, 3)

    second_path = grid.generate_path((1, 3), (4, 3))
    print(second_path)
    assert second_path[0] == (1, 3)
    assert second_path[-1] == (4, 3)

    third_path = grid.generate_path((3, 2), (2, 2))
    print(third_path)
    assert third_path[0] == (3, 2)
    assert third_path[-1] == (2, 2)
    assert (4, 3) in third_path
