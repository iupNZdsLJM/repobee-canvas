from _repobee import plugin

from repobee_canvas import canvas


def test_register():
    """Just test that there is no crash"""
    plugin.register_plugins([canvas])
