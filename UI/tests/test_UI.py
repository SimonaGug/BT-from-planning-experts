#!/usr/bin/env python3
"""
Test routines for the UI
"""

import UI.draw_world as ui
import matplotlib.pyplot as plt

def test_object():
    """
    Test the object class
    """
    oracle_origin = (100, 100)
    oracle_length = 10
    oracle_height = 20
    oracle_line = 'line_color'
    oracle_fill = 'fill_color'

    test = ui.Object(100, 100, 10, 20, line='line_color', fill='fill_color')

    assert test.origin == oracle_origin
    assert test.length == oracle_length
    assert test.height == oracle_height
    assert test.line == oracle_line
    assert test.fill == oracle_fill

    oracle_origin = (5, 5)
    test.set_origin(5, 5)

    assert test.origin == oracle_origin

def test_reset():
    """
    Test the reset world function.
    The feedback is visual, very few assertions.
    """
    world = ui.WorldUI()
    world.reset_world()
    world.print_world('empty_world')
    plt.close()

def test_robot():
    """
    Test the add robot function.
    The feedback is visual, very few assertions.
    - robot test poses:
    robotCharge1 = (2,7.5)
    robotCharge2 = (23,12)
    robotConvH = (12,12)
    robotConvL = (12,3)
    robotDel = (21,7.5)
    """
    world = ui.WorldUI()
    world.reset_world()
    world.add_robot((2,7.5))
    world.print_world('robot')
    world.reset_world()
    world.print_world('empty_again')
    plt.close()

def test_items():
    """
    Test the add items function.
    The feedback is visual, very few assertions.
    """
    world = ui.WorldUI()
    world.reset_world()
    world.add_items(2, 3)
    world.print_world('items')
    world.reset_world()
    world.print_world('empty_again')
    plt.close()

def test_output():
    """
    Test if a figure can be output.
    """
    plt.cla()
    plt.clf()
    world = ui.WorldUI()
    world.reset_world()
    fig, ax = world.get_figure()
    ax.plot()
    plt.show()
