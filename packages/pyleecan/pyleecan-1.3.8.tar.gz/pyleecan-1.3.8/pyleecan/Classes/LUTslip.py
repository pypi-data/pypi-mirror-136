# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Simulation/LUTslip.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/LUTslip
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import set_array, check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.copy import copy
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from .LUT import LUT

from numpy import array, array_equal
from ._check import InitUnKnowClassError


class LUTslip(LUT):
    """Look Up Table class for u0/slip OP matrix"""

    VERSION = 1

    # save and copy methods are available in all object
    save = save
    copy = copy
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Phi_m=None,
        I_m=None,
        T2_ref=20,
        R2=None,
        L2=None,
        R1=None,
        L1=None,
        T1_ref=20,
        OP_matrix=None,
        phase_dir=None,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "Phi_m" in list(init_dict.keys()):
                Phi_m = init_dict["Phi_m"]
            if "I_m" in list(init_dict.keys()):
                I_m = init_dict["I_m"]
            if "T2_ref" in list(init_dict.keys()):
                T2_ref = init_dict["T2_ref"]
            if "R2" in list(init_dict.keys()):
                R2 = init_dict["R2"]
            if "L2" in list(init_dict.keys()):
                L2 = init_dict["L2"]
            if "R1" in list(init_dict.keys()):
                R1 = init_dict["R1"]
            if "L1" in list(init_dict.keys()):
                L1 = init_dict["L1"]
            if "T1_ref" in list(init_dict.keys()):
                T1_ref = init_dict["T1_ref"]
            if "OP_matrix" in list(init_dict.keys()):
                OP_matrix = init_dict["OP_matrix"]
            if "phase_dir" in list(init_dict.keys()):
                phase_dir = init_dict["phase_dir"]
        # Set the properties (value check and convertion are done in setter)
        self.Phi_m = Phi_m
        self.I_m = I_m
        self.T2_ref = T2_ref
        self.R2 = R2
        self.L2 = L2
        # Call LUT init
        super(LUTslip, self).__init__(
            R1=R1, L1=L1, T1_ref=T1_ref, OP_matrix=OP_matrix, phase_dir=phase_dir
        )
        # The class is frozen (in LUT init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LUTslip_str = ""
        # Get the properties inherited from LUT
        LUTslip_str += super(LUTslip, self).__str__()
        LUTslip_str += (
            "Phi_m = "
            + linesep
            + str(self.Phi_m).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        LUTslip_str += (
            "I_m = "
            + linesep
            + str(self.I_m).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        LUTslip_str += "T2_ref = " + str(self.T2_ref) + linesep
        LUTslip_str += "R2 = " + str(self.R2) + linesep
        LUTslip_str += "L2 = " + str(self.L2) + linesep
        return LUTslip_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LUT
        if not super(LUTslip, self).__eq__(other):
            return False
        if not array_equal(other.Phi_m, self.Phi_m):
            return False
        if not array_equal(other.I_m, self.I_m):
            return False
        if other.T2_ref != self.T2_ref:
            return False
        if other.R2 != self.R2:
            return False
        if other.L2 != self.L2:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from LUT
        diff_list.extend(super(LUTslip, self).compare(other, name=name))
        if not array_equal(other.Phi_m, self.Phi_m):
            diff_list.append(name + ".Phi_m")
        if not array_equal(other.I_m, self.I_m):
            diff_list.append(name + ".I_m")
        if other._T2_ref != self._T2_ref:
            diff_list.append(name + ".T2_ref")
        if other._R2 != self._R2:
            diff_list.append(name + ".R2")
        if other._L2 != self._L2:
            diff_list.append(name + ".L2")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from LUT
        S += super(LUTslip, self).__sizeof__()
        S += getsizeof(self.Phi_m)
        S += getsizeof(self.I_m)
        S += getsizeof(self.T2_ref)
        S += getsizeof(self.R2)
        S += getsizeof(self.L2)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from LUT
        LUTslip_dict = super(LUTslip, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.Phi_m is None:
            LUTslip_dict["Phi_m"] = None
        else:
            if type_handle_ndarray == 0:
                LUTslip_dict["Phi_m"] = self.Phi_m.tolist()
            elif type_handle_ndarray == 1:
                LUTslip_dict["Phi_m"] = self.Phi_m.copy()
            elif type_handle_ndarray == 2:
                LUTslip_dict["Phi_m"] = self.Phi_m
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        if self.I_m is None:
            LUTslip_dict["I_m"] = None
        else:
            if type_handle_ndarray == 0:
                LUTslip_dict["I_m"] = self.I_m.tolist()
            elif type_handle_ndarray == 1:
                LUTslip_dict["I_m"] = self.I_m.copy()
            elif type_handle_ndarray == 2:
                LUTslip_dict["I_m"] = self.I_m
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        LUTslip_dict["T2_ref"] = self.T2_ref
        LUTslip_dict["R2"] = self.R2
        LUTslip_dict["L2"] = self.L2
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LUTslip_dict["__class__"] = "LUTslip"
        return LUTslip_dict

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Phi_m = None
        self.I_m = None
        self.T2_ref = None
        self.R2 = None
        self.L2 = None
        # Set to None the properties inherited from LUT
        super(LUTslip, self)._set_None()

    def _get_Phi_m(self):
        """getter of Phi_m"""
        return self._Phi_m

    def _set_Phi_m(self, value):
        """setter of Phi_m"""
        if type(value) is int and value == -1:
            value = array([])
        elif type(value) is list:
            try:
                value = array(value)
            except:
                pass
        check_var("Phi_m", value, "ndarray")
        self._Phi_m = value

    Phi_m = property(
        fget=_get_Phi_m,
        fset=_set_Phi_m,
        doc=u"""Magnetizing flux for a given magnetizing current I_m

        :Type: ndarray
        """,
    )

    def _get_I_m(self):
        """getter of I_m"""
        return self._I_m

    def _set_I_m(self, value):
        """setter of I_m"""
        if type(value) is int and value == -1:
            value = array([])
        elif type(value) is list:
            try:
                value = array(value)
            except:
                pass
        check_var("I_m", value, "ndarray")
        self._I_m = value

    I_m = property(
        fget=_get_I_m,
        fset=_set_I_m,
        doc=u"""Stator magnetizing current

        :Type: ndarray
        """,
    )

    def _get_T2_ref(self):
        """getter of T2_ref"""
        return self._T2_ref

    def _set_T2_ref(self, value):
        """setter of T2_ref"""
        check_var("T2_ref", value, "float")
        self._T2_ref = value

    T2_ref = property(
        fget=_get_T2_ref,
        fset=_set_T2_ref,
        doc=u"""Rotor bar average temperature at which Phi_m is given

        :Type: float
        """,
    )

    def _get_R2(self):
        """getter of R2"""
        return self._R2

    def _set_R2(self, value):
        """setter of R2"""
        check_var("R2", value, "float")
        self._R2 = value

    R2 = property(
        fget=_get_R2,
        fset=_set_R2,
        doc=u"""DC rotor winding resistance at T2_ref already expressed per phase in stator frame 

        :Type: float
        """,
    )

    def _get_L2(self):
        """getter of L2"""
        return self._L2

    def _set_L2(self, value):
        """setter of L2"""
        check_var("L2", value, "float")
        self._L2 = value

    L2 = property(
        fget=_get_L2,
        fset=_set_L2,
        doc=u"""Rotor winding leakage inductance

        :Type: float
        """,
    )
