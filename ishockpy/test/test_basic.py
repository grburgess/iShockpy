import numpy as np

from ishockpy import *


def test_basic(finished_jet):

    assert finished_jet._status == False


def test_file_write(finished_jet):

    finished_jet.write_to("jet_save.h5")


def test_file_read():

    collisions, shells = Jet.from_file("jet_save.h5")
    

    

    
    
