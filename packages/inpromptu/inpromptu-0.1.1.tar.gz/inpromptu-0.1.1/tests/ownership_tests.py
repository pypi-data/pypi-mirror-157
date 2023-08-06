#!/usr/bin/env/python3
import pytest
from inpromptu import Inpromp2
from .test_classes import MyTopClass

# Ownership looks like this:
# MyTopClass
# |
#  -- self.my_class_a = MyClassA()
#     |
#      -- self.my_class_b = MyClassB()



# for tests that need to receive user input and inspect output printed to the
# shell, use this fn as a template.
def test_user_input_hookup(monkeypatch, capsys):
    """ Check nested call tree."""

    def user_input_response(prompt_input):
        """Send a when provided with an input string from the prompt.
           This fn acts as a user replying to the prompt_input."""
        return "my_func_0\r\n" # The equivalent of pressing <ENTER>

    # Hookup our custom response to act as user input.
    monkeypatch.setattr('builtins.input', user_input_response)

    my_prompt = Inpromp2(ClassA())

    # This will produce an input. Monkeypatched input fn should reply with
    my_prompt.cmdloop(loop=False)

    # Reply for help should print the docstring for the help function.
    assert capsys.readouterr().out.rstrip() == "" # Should not produce any output
