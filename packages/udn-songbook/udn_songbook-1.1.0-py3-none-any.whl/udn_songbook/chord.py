#!/usr/bin/env python3
# vim: set ts=4 sts=4 sw=4 et ci nu ft=python:

import pychord

class Chord(pychord.Chord):
    """
    wrapper around chords in a song

    Effectively combines the pychord.Chord data (which allows transposition
    and contained notes etc) and position in markup
    """

    def __init__(self, start: int, end: int, chord: str):
        """
        just calls the parent initialiser and adds a couple of 
        extra properties
        """
        super().__init__(chord)
        # These are actually the opening and closing parentheses in markup
        self.start = start
        self.end = end

    def __repr__(self):
        return f"<Chord: {self.chord}, start: {self.start}, end: {self.end}>"
