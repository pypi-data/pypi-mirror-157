"""
.. module:: road_definition

    :platform: Windows
    :synopsis: Example code making a scenario that defines new roads to drive
               on.

.. moduleauthor:: Marc Müller <mmueller@beamng.gmbh>

"""

from beamngpy import BeamNGpy, Scenario, Road, Vehicle, setup_logging


def main():
    beamng = BeamNGpy('localhost', 64256)
    bng = beamng.open(launch=True)

    scenario = Scenario('gridmap_v2', 'road_test')
    road_a = Road('track_editor_C_center', rid='circle_road', looped=True)
    road_a.add_nodes(
        (-25, 300, 0, 5),
        (25, 300, 0, 6),
        (25, 350, 0, 4),
        (-25, 350, 0, 5),
    )
    scenario.add_road(road_a)

    road_b = Road('track_editor_C_center', rid='center_road')
    road_b.add_nodes(
        (0, 325, 0, 5)
        (50, 375, 0, 5)
    )
    scenario.add_road(road_b)

    scenario.make(bng)

    try:
        bng.load_scenario(scenario)
        bng.start_scenario()
        input('Press enter when done...')
    finally:
        bng.close()


if __name__ == '__main__':
    main()
