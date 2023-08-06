# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Output/OutElec.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Output/OutElec
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.copy import copy
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from ._frozen import FrozenClass

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
try:
    from ..Methods.Output.OutElec.get_Nr import get_Nr
except ImportError as error:
    get_Nr = error

try:
    from ..Methods.Output.OutElec.get_Is import get_Is
except ImportError as error:
    get_Is = error

try:
    from ..Methods.Output.OutElec.get_Us import get_Us
except ImportError as error:
    get_Us = error

try:
    from ..Methods.Output.OutElec.store import store
except ImportError as error:
    store = error

try:
    from ..Methods.Output.OutElec.get_electrical import get_electrical
except ImportError as error:
    get_electrical = error


from ._check import InitUnKnowClassError
from .OutInternal import OutInternal
from .OP import OP
from .ImportGenPWM import ImportGenPWM


class OutElec(FrozenClass):
    """Gather the electric module outputs"""

    VERSION = 1

    # Check ImportError to remove unnecessary dependencies in unused method
    # cf Methods.Output.OutElec.get_Nr
    if isinstance(get_Nr, ImportError):
        get_Nr = property(
            fget=lambda x: raise_(
                ImportError("Can't use OutElec method get_Nr: " + str(get_Nr))
            )
        )
    else:
        get_Nr = get_Nr
    # cf Methods.Output.OutElec.get_Is
    if isinstance(get_Is, ImportError):
        get_Is = property(
            fget=lambda x: raise_(
                ImportError("Can't use OutElec method get_Is: " + str(get_Is))
            )
        )
    else:
        get_Is = get_Is
    # cf Methods.Output.OutElec.get_Us
    if isinstance(get_Us, ImportError):
        get_Us = property(
            fget=lambda x: raise_(
                ImportError("Can't use OutElec method get_Us: " + str(get_Us))
            )
        )
    else:
        get_Us = get_Us
    # cf Methods.Output.OutElec.store
    if isinstance(store, ImportError):
        store = property(
            fget=lambda x: raise_(
                ImportError("Can't use OutElec method store: " + str(store))
            )
        )
    else:
        store = store
    # cf Methods.Output.OutElec.get_electrical
    if isinstance(get_electrical, ImportError):
        get_electrical = property(
            fget=lambda x: raise_(
                ImportError(
                    "Can't use OutElec method get_electrical: " + str(get_electrical)
                )
            )
        )
    else:
        get_electrical = get_electrical
    # save and copy methods are available in all object
    save = save
    copy = copy
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        axes_dict=None,
        Is=None,
        Ir=None,
        logger_name="pyleecan.Electrical",
        Pj_losses=None,
        Us=None,
        internal=None,
        OP=None,
        Pem_av_ref=None,
        Tem_av_ref=None,
        phase_dir=None,
        current_dir=None,
        PWM=None,
        eec_param=None,
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
            if "axes_dict" in list(init_dict.keys()):
                axes_dict = init_dict["axes_dict"]
            if "Is" in list(init_dict.keys()):
                Is = init_dict["Is"]
            if "Ir" in list(init_dict.keys()):
                Ir = init_dict["Ir"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
            if "Pj_losses" in list(init_dict.keys()):
                Pj_losses = init_dict["Pj_losses"]
            if "Us" in list(init_dict.keys()):
                Us = init_dict["Us"]
            if "internal" in list(init_dict.keys()):
                internal = init_dict["internal"]
            if "OP" in list(init_dict.keys()):
                OP = init_dict["OP"]
            if "Pem_av_ref" in list(init_dict.keys()):
                Pem_av_ref = init_dict["Pem_av_ref"]
            if "Tem_av_ref" in list(init_dict.keys()):
                Tem_av_ref = init_dict["Tem_av_ref"]
            if "phase_dir" in list(init_dict.keys()):
                phase_dir = init_dict["phase_dir"]
            if "current_dir" in list(init_dict.keys()):
                current_dir = init_dict["current_dir"]
            if "PWM" in list(init_dict.keys()):
                PWM = init_dict["PWM"]
            if "eec_param" in list(init_dict.keys()):
                eec_param = init_dict["eec_param"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.axes_dict = axes_dict
        self.Is = Is
        self.Ir = Ir
        self.logger_name = logger_name
        self.Pj_losses = Pj_losses
        self.Us = Us
        self.internal = internal
        self.OP = OP
        self.Pem_av_ref = Pem_av_ref
        self.Tem_av_ref = Tem_av_ref
        self.phase_dir = phase_dir
        self.current_dir = current_dir
        self.PWM = PWM
        self.eec_param = eec_param

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        OutElec_str = ""
        if self.parent is None:
            OutElec_str += "parent = None " + linesep
        else:
            OutElec_str += "parent = " + str(type(self.parent)) + " object" + linesep
        OutElec_str += "axes_dict = " + str(self.axes_dict) + linesep + linesep
        OutElec_str += "Is = " + str(self.Is) + linesep + linesep
        OutElec_str += "Ir = " + str(self.Ir) + linesep + linesep
        OutElec_str += 'logger_name = "' + str(self.logger_name) + '"' + linesep
        OutElec_str += "Pj_losses = " + str(self.Pj_losses) + linesep
        OutElec_str += "Us = " + str(self.Us) + linesep + linesep
        if self.internal is not None:
            tmp = self.internal.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            OutElec_str += "internal = " + tmp
        else:
            OutElec_str += "internal = None" + linesep + linesep
        if self.OP is not None:
            tmp = self.OP.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            OutElec_str += "OP = " + tmp
        else:
            OutElec_str += "OP = None" + linesep + linesep
        OutElec_str += "Pem_av_ref = " + str(self.Pem_av_ref) + linesep
        OutElec_str += "Tem_av_ref = " + str(self.Tem_av_ref) + linesep
        OutElec_str += "phase_dir = " + str(self.phase_dir) + linesep
        OutElec_str += "current_dir = " + str(self.current_dir) + linesep
        if self.PWM is not None:
            tmp = self.PWM.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            OutElec_str += "PWM = " + tmp
        else:
            OutElec_str += "PWM = None" + linesep + linesep
        OutElec_str += "eec_param = " + str(self.eec_param) + linesep
        return OutElec_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.axes_dict != self.axes_dict:
            return False
        if other.Is != self.Is:
            return False
        if other.Ir != self.Ir:
            return False
        if other.logger_name != self.logger_name:
            return False
        if other.Pj_losses != self.Pj_losses:
            return False
        if other.Us != self.Us:
            return False
        if other.internal != self.internal:
            return False
        if other.OP != self.OP:
            return False
        if other.Pem_av_ref != self.Pem_av_ref:
            return False
        if other.Tem_av_ref != self.Tem_av_ref:
            return False
        if other.phase_dir != self.phase_dir:
            return False
        if other.current_dir != self.current_dir:
            return False
        if other.PWM != self.PWM:
            return False
        if other.eec_param != self.eec_param:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if (other.axes_dict is None and self.axes_dict is not None) or (
            other.axes_dict is not None and self.axes_dict is None
        ):
            diff_list.append(name + ".axes_dict None mismatch")
        elif self.axes_dict is None:
            pass
        elif len(other.axes_dict) != len(self.axes_dict):
            diff_list.append("len(" + name + "axes_dict)")
        else:
            for key in self.axes_dict:
                diff_list.extend(
                    self.axes_dict[key].compare(
                        other.axes_dict[key], name=name + ".axes_dict"
                    )
                )
        if (other.Is is None and self.Is is not None) or (
            other.Is is not None and self.Is is None
        ):
            diff_list.append(name + ".Is None mismatch")
        elif self.Is is not None:
            diff_list.extend(self.Is.compare(other.Is, name=name + ".Is"))
        if (other.Ir is None and self.Ir is not None) or (
            other.Ir is not None and self.Ir is None
        ):
            diff_list.append(name + ".Ir None mismatch")
        elif self.Ir is not None:
            diff_list.extend(self.Ir.compare(other.Ir, name=name + ".Ir"))
        if other._logger_name != self._logger_name:
            diff_list.append(name + ".logger_name")
        if other._Pj_losses != self._Pj_losses:
            diff_list.append(name + ".Pj_losses")
        if (other.Us is None and self.Us is not None) or (
            other.Us is not None and self.Us is None
        ):
            diff_list.append(name + ".Us None mismatch")
        elif self.Us is not None:
            diff_list.extend(self.Us.compare(other.Us, name=name + ".Us"))
        if (other.internal is None and self.internal is not None) or (
            other.internal is not None and self.internal is None
        ):
            diff_list.append(name + ".internal None mismatch")
        elif self.internal is not None:
            diff_list.extend(
                self.internal.compare(other.internal, name=name + ".internal")
            )
        if (other.OP is None and self.OP is not None) or (
            other.OP is not None and self.OP is None
        ):
            diff_list.append(name + ".OP None mismatch")
        elif self.OP is not None:
            diff_list.extend(self.OP.compare(other.OP, name=name + ".OP"))
        if other._Pem_av_ref != self._Pem_av_ref:
            diff_list.append(name + ".Pem_av_ref")
        if other._Tem_av_ref != self._Tem_av_ref:
            diff_list.append(name + ".Tem_av_ref")
        if other._phase_dir != self._phase_dir:
            diff_list.append(name + ".phase_dir")
        if other._current_dir != self._current_dir:
            diff_list.append(name + ".current_dir")
        if (other.PWM is None and self.PWM is not None) or (
            other.PWM is not None and self.PWM is None
        ):
            diff_list.append(name + ".PWM None mismatch")
        elif self.PWM is not None:
            diff_list.extend(self.PWM.compare(other.PWM, name=name + ".PWM"))
        if other._eec_param != self._eec_param:
            diff_list.append(name + ".eec_param")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        if self.axes_dict is not None:
            for key, value in self.axes_dict.items():
                S += getsizeof(value) + getsizeof(key)
        S += getsizeof(self.Is)
        S += getsizeof(self.Ir)
        S += getsizeof(self.logger_name)
        S += getsizeof(self.Pj_losses)
        S += getsizeof(self.Us)
        S += getsizeof(self.internal)
        S += getsizeof(self.OP)
        S += getsizeof(self.Pem_av_ref)
        S += getsizeof(self.Tem_av_ref)
        S += getsizeof(self.phase_dir)
        S += getsizeof(self.current_dir)
        S += getsizeof(self.PWM)
        if self.eec_param is not None:
            for key, value in self.eec_param.items():
                S += getsizeof(value) + getsizeof(key)
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

        OutElec_dict = dict()
        if self.axes_dict is None:
            OutElec_dict["axes_dict"] = None
        else:
            OutElec_dict["axes_dict"] = dict()
            for key, obj in self.axes_dict.items():
                if obj is not None:
                    OutElec_dict["axes_dict"][key] = obj.as_dict(
                        type_handle_ndarray=type_handle_ndarray,
                        keep_function=keep_function,
                        **kwargs
                    )
                else:
                    OutElec_dict["axes_dict"][key] = None
        if self.Is is None:
            OutElec_dict["Is"] = None
        else:
            OutElec_dict["Is"] = self.Is.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.Ir is None:
            OutElec_dict["Ir"] = None
        else:
            OutElec_dict["Ir"] = self.Ir.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        OutElec_dict["logger_name"] = self.logger_name
        OutElec_dict["Pj_losses"] = self.Pj_losses
        if self.Us is None:
            OutElec_dict["Us"] = None
        else:
            OutElec_dict["Us"] = self.Us.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.internal is None:
            OutElec_dict["internal"] = None
        else:
            OutElec_dict["internal"] = self.internal.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.OP is None:
            OutElec_dict["OP"] = None
        else:
            OutElec_dict["OP"] = self.OP.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        OutElec_dict["Pem_av_ref"] = self.Pem_av_ref
        OutElec_dict["Tem_av_ref"] = self.Tem_av_ref
        OutElec_dict["phase_dir"] = self.phase_dir
        OutElec_dict["current_dir"] = self.current_dir
        if self.PWM is None:
            OutElec_dict["PWM"] = None
        else:
            OutElec_dict["PWM"] = self.PWM.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        OutElec_dict["eec_param"] = (
            self.eec_param.copy() if self.eec_param is not None else None
        )
        # The class name is added to the dict for deserialisation purpose
        OutElec_dict["__class__"] = "OutElec"
        return OutElec_dict

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.axes_dict = None
        self.Is = None
        self.Ir = None
        self.logger_name = None
        self.Pj_losses = None
        self.Us = None
        if self.internal is not None:
            self.internal._set_None()
        if self.OP is not None:
            self.OP._set_None()
        self.Pem_av_ref = None
        self.Tem_av_ref = None
        self.phase_dir = None
        self.current_dir = None
        if self.PWM is not None:
            self.PWM._set_None()
        self.eec_param = None

    def _get_axes_dict(self):
        """getter of axes_dict"""
        if self._axes_dict is not None:
            for key, obj in self._axes_dict.items():
                if obj is not None:
                    obj.parent = self
        return self._axes_dict

    def _set_axes_dict(self, value):
        """setter of axes_dict"""
        if type(value) is dict:
            for key, obj in value.items():
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[key] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "SciDataTool.Classes", obj.get("__class__"), "axes_dict"
                    )
                    value[key] = class_obj(init_dict=obj)
        if type(value) is int and value == -1:
            value = dict()
        check_var("axes_dict", value, "{Data}")
        self._axes_dict = value

    axes_dict = property(
        fget=_get_axes_dict,
        fset=_set_axes_dict,
        doc=u"""Dict containing axes data used for Electrical

        :Type: {SciDataTool.Classes.DataND.Data}
        """,
    )

    def _get_Is(self):
        """getter of Is"""
        return self._Is

    def _set_Is(self, value):
        """setter of Is"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "SciDataTool.Classes", value.get("__class__"), "Is"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            value = DataND()
        check_var("Is", value, "DataND")
        self._Is = value

    Is = property(
        fget=_get_Is,
        fset=_set_Is,
        doc=u"""Stator currents DataTime object

        :Type: SciDataTool.Classes.DataND.DataND
        """,
    )

    def _get_Ir(self):
        """getter of Ir"""
        return self._Ir

    def _set_Ir(self, value):
        """setter of Ir"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "SciDataTool.Classes", value.get("__class__"), "Ir"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            value = DataND()
        check_var("Ir", value, "DataND")
        self._Ir = value

    Ir = property(
        fget=_get_Ir,
        fset=_set_Ir,
        doc=u"""Rotor currents as a function of time (each column correspond to one phase)

        :Type: SciDataTool.Classes.DataND.DataND
        """,
    )

    def _get_logger_name(self):
        """getter of logger_name"""
        return self._logger_name

    def _set_logger_name(self, value):
        """setter of logger_name"""
        check_var("logger_name", value, "str")
        self._logger_name = value

    logger_name = property(
        fget=_get_logger_name,
        fset=_set_logger_name,
        doc=u"""Name of the logger to use

        :Type: str
        """,
    )

    def _get_Pj_losses(self):
        """getter of Pj_losses"""
        return self._Pj_losses

    def _set_Pj_losses(self, value):
        """setter of Pj_losses"""
        check_var("Pj_losses", value, "float")
        self._Pj_losses = value

    Pj_losses = property(
        fget=_get_Pj_losses,
        fset=_set_Pj_losses,
        doc=u"""Electrical Joule losses

        :Type: float
        """,
    )

    def _get_Us(self):
        """getter of Us"""
        return self._Us

    def _set_Us(self, value):
        """setter of Us"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "SciDataTool.Classes", value.get("__class__"), "Us"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            value = DataND()
        check_var("Us", value, "DataND")
        self._Us = value

    Us = property(
        fget=_get_Us,
        fset=_set_Us,
        doc=u"""Stator voltage as a function of time (each column correspond to one phase)

        :Type: SciDataTool.Classes.DataND.DataND
        """,
    )

    def _get_internal(self):
        """getter of internal"""
        return self._internal

    def _set_internal(self, value):
        """setter of internal"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "internal"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            value = OutInternal()
        check_var("internal", value, "OutInternal")
        self._internal = value

        if self._internal is not None:
            self._internal.parent = self

    internal = property(
        fget=_get_internal,
        fset=_set_internal,
        doc=u"""OutInternal object containg outputs related to a specific model

        :Type: OutInternal
        """,
    )

    def _get_OP(self):
        """getter of OP"""
        return self._OP

    def _set_OP(self, value):
        """setter of OP"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "OP")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            value = OP()
        check_var("OP", value, "OP")
        self._OP = value

        if self._OP is not None:
            self._OP.parent = self

    OP = property(
        fget=_get_OP,
        fset=_set_OP,
        doc=u"""Operating Point

        :Type: OP
        """,
    )

    def _get_Pem_av_ref(self):
        """getter of Pem_av_ref"""
        return self._Pem_av_ref

    def _set_Pem_av_ref(self, value):
        """setter of Pem_av_ref"""
        check_var("Pem_av_ref", value, "float")
        self._Pem_av_ref = value

    Pem_av_ref = property(
        fget=_get_Pem_av_ref,
        fset=_set_Pem_av_ref,
        doc=u"""Theoretical Average Electromagnetic Power

        :Type: float
        """,
    )

    def _get_Tem_av_ref(self):
        """getter of Tem_av_ref"""
        return self._Tem_av_ref

    def _set_Tem_av_ref(self, value):
        """setter of Tem_av_ref"""
        check_var("Tem_av_ref", value, "float")
        self._Tem_av_ref = value

    Tem_av_ref = property(
        fget=_get_Tem_av_ref,
        fset=_set_Tem_av_ref,
        doc=u"""Theoretical Average Electromagnetic torque

        :Type: float
        """,
    )

    def _get_phase_dir(self):
        """getter of phase_dir"""
        return self._phase_dir

    def _set_phase_dir(self, value):
        """setter of phase_dir"""
        check_var("phase_dir", value, "int", Vmin=-1, Vmax=1)
        self._phase_dir = value

    phase_dir = property(
        fget=_get_phase_dir,
        fset=_set_phase_dir,
        doc=u"""Rotation direction of the stator phases (phase_dir*(n-1)*pi/qs, default value given by PHASE_DIR_REF)

        :Type: int
        :min: -1
        :max: 1
        """,
    )

    def _get_current_dir(self):
        """getter of current_dir"""
        return self._current_dir

    def _set_current_dir(self, value):
        """setter of current_dir"""
        check_var("current_dir", value, "int", Vmin=-1, Vmax=1)
        self._current_dir = value

    current_dir = property(
        fget=_get_current_dir,
        fset=_set_current_dir,
        doc=u"""Rotation direction of the stator currents (current_dir*2*pi*felec*time, default value given by CURRENT_DIR_REF)

        :Type: int
        :min: -1
        :max: 1
        """,
    )

    def _get_PWM(self):
        """getter of PWM"""
        return self._PWM

    def _set_PWM(self, value):
        """setter of PWM"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "PWM")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            value = ImportGenPWM()
        check_var("PWM", value, "ImportGenPWM")
        self._PWM = value

        if self._PWM is not None:
            self._PWM.parent = self

    PWM = property(
        fget=_get_PWM,
        fset=_set_PWM,
        doc=u"""Object to generate PWM signal

        :Type: ImportGenPWM
        """,
    )

    def _get_eec_param(self):
        """getter of eec_param"""
        return self._eec_param

    def _set_eec_param(self, value):
        """setter of eec_param"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("eec_param", value, "dict")
        self._eec_param = value

    eec_param = property(
        fget=_get_eec_param,
        fset=_set_eec_param,
        doc=u"""Dict containing parameters used in Electric Equivalent Circuit

        :Type: dict
        """,
    )
