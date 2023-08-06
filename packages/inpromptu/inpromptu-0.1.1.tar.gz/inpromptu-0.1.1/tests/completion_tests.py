#!/usr/bin/env/python3
import pytest, autopy
from inpromptu.inpromptu import Inpromptu, cli_method

def test_docstring_display_from_help_method(monkeypatch, capsys):
    """Asking for help for a particular function should display the docstring."""

    def user_input_response(prompt):
        return "help help \r\n"
    monkeypatch.setattr('builtins.input', user_input_response)

    my_interface = Inpromptu()
    my_interface.cmdloop(loop=False)

    # Reply for help should print the docstring for the help function.
    assert capsys.readouterr().out.rstrip() == my_interface.help.__doc__


#def test_empty_completion_of_methods(monkeypatch, capsys):
#    """Test tab completion on empty input. Should return all methods."""
#
#    def user_input_response(prompt):
#        return "help"
#    monkeypatch.setattr('builtins.input', user_input_response)
#
#    my_interface = Inpromptu()
#    my_interface.cmdloop(loop=False)
#    keyboard.press_and_release('tab, tab')
#
#    # Reply for help should print the docstring for the help function.
#    assert capsys.readouterr().out.rstrip() == ">>>"
