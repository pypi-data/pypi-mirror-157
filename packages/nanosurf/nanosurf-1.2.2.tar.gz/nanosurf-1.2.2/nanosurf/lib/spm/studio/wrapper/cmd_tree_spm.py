# studio_wrapper.py

from enum import Enum
from typing import Any
import nanosurf.lib.spm.studio.wrapper as wrap

g_cmd_tree_hash = '72e0b3d6a65d202b583b46d9a738843b'
g_compiler_version = '1.0'

class RootTestTabel(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.test.tabel'


class RootTest(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.test'
        self.tabel = RootTestTabel(self._context)

    @property
    def num_f(self) -> float:
        return float(self._context.get('root.test.num_f'))

    @num_f.setter
    def num_f(self, new_val:float):
        self._context.set('root.test.num_f', float(new_val))

    def func(self, *args) -> Any:
        return self._context.call('root.test.func', *args)

    @property
    def str(self) -> str:
        return str(self._context.get('root.test.str'))

    @str.setter
    def str(self, new_val:str):
        self._context.set('root.test.str', str(new_val))

    @property
    def num_i(self) -> int:
        return int(self._context.get('root.test.num_i'))

    @num_i.setter
    def num_i(self, new_val:int):
        self._context.set('root.test.num_i', int(new_val))


class RootWorkflowMeasurement_setup(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.measurement_setup'


class RootWorkflowPreset_loader(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.preset_loader'


class RootWorkflowSystem_startup(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.system_startup'


class RootWorkflowParameters(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.parameters'


class RootWorkflowThermal_tune(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.thermal_tune'


class RootWorkflowXy_closed_loop(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.xy_closed_loop'


class RootWorkflowSpm_resource_requester(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.spm_resource_requester'


class RootWorkflowZ_controller(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.z_controller'


class RootWorkflowManager(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.manager'

    @property
    def session_name(self) -> str:
        return str(self._context.get('root.workflow.manager.session_name'))

    @session_name.setter
    def session_name(self, new_val:str):
        self._context.set('root.workflow.manager.session_name', str(new_val))


class RootWorkflowImagingSignalProcedure_info(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal.procedure_info'

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.procedure_info.connect', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.procedure_info.connect_extended', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.procedure_info.empty', *args)

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.procedure_info.call', *args)


class RootWorkflowImagingSignalRemaining_scan_time_changed(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal.remaining_scan_time_changed'

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.remaining_scan_time_changed.connect', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.remaining_scan_time_changed.connect_extended', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.remaining_scan_time_changed.empty', *args)

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.remaining_scan_time_changed.call', *args)


class RootWorkflowImagingSignalScanning_started(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal.scanning_started'

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_started.connect', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_started.connect_extended', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_started.empty', *args)

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_started.call', *args)


class RootWorkflowImagingSignalScanning_finished(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal.scanning_finished'

    def connect(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_finished.connect', *args)

    def connect_extended(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_finished.connect_extended', *args)

    def empty(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_finished.empty', *args)

    def call(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.signal.scanning_finished.call', *args)


class RootWorkflowImagingSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.signal'
        self.scanning_finished = RootWorkflowImagingSignalScanning_finished(self._context)
        self.scanning_started = RootWorkflowImagingSignalScanning_started(self._context)
        self.remaining_scan_time_changed = RootWorkflowImagingSignalRemaining_scan_time_changed(self._context)
        self.procedure_info = RootWorkflowImagingSignalProcedure_info(self._context)


class RootWorkflowImagingVarScript_test_var_array(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.var.script_test_var_array'


class RootWorkflowImagingVar(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.var'
        self.script_test_var_array = RootWorkflowImagingVarScript_test_var_array(self._context)

    @property
    def script_test_var_double(self) -> float:
        return float(self._context.get('root.workflow.imaging.var.script_test_var_double'))

    @script_test_var_double.setter
    def script_test_var_double(self, new_val:float):
        self._context.set('root.workflow.imaging.var.script_test_var_double', float(new_val))

    @property
    def script_test_var_string(self) -> str:
        return str(self._context.get('root.workflow.imaging.var.script_test_var_string'))

    @script_test_var_string.setter
    def script_test_var_string(self, new_val:str):
        self._context.set('root.workflow.imaging.var.script_test_var_string', str(new_val))

    @property
    def script_test_var_int(self) -> int:
        return int(self._context.get('root.workflow.imaging.var.script_test_var_int'))

    @script_test_var_int.setter
    def script_test_var_int(self, new_val:int):
        self._context.set('root.workflow.imaging.var.script_test_var_int', int(new_val))


class RootWorkflowImagingPropertyLines_per_frame(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.lines_per_frame'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.lines_per_frame.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.lines_per_frame.value', int(new_val))


class RootWorkflowImagingPropertyScan_range_slow_axis(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.scan_range_slow_axis'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.scan_range_slow_axis.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.scan_range_slow_axis.value', float(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.scan_range_slow_axis.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.scan_range_slow_axis.unit', str(new_val))


class RootWorkflowImagingPropertyImage_offset_y(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.image_offset_y'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.image_offset_y.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.image_offset_y.value', int(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.image_offset_y.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.image_offset_y.unit', str(new_val))


class RootWorkflowImagingPropertySlope_y(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.slope_y'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.slope_y.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.slope_y.value', int(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.slope_y.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.slope_y.unit', str(new_val))


class RootWorkflowImagingPropertyImage_offset_x(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.image_offset_x'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.image_offset_x.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.image_offset_x.value', int(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.image_offset_x.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.image_offset_x.unit', str(new_val))


class RootWorkflowImagingPropertyScan_range_fast_axis(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.scan_range_fast_axis'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.scan_range_fast_axis.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.scan_range_fast_axis.value', float(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.scan_range_fast_axis.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.scan_range_fast_axis.unit', str(new_val))


class RootWorkflowImagingPropertySlope_x(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.slope_x'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.slope_x.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.slope_x.value', int(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.slope_x.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.slope_x.unit', str(new_val))


class RootWorkflowImagingPropertySlow_axis_scan_direction(wrap.CmdTreeProp):

    class EnumType(Enum):
        Downward = 'Downward'
        Upward = 'Upward'
        Bounce = 'Bounce'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.slow_axis_scan_direction'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def value(self) -> EnumType:
        return RootWorkflowImagingPropertySlow_axis_scan_direction.EnumType(self._context.get('root.workflow.imaging.property.slow_axis_scan_direction.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.imaging.property.slow_axis_scan_direction.value', new_val.value)

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.imaging.property.slow_axis_scan_direction.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.imaging.property.slow_axis_scan_direction.enum', list(new_val))


class RootWorkflowImagingPropertyTime_per_line(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.time_per_line'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.time_per_line.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.time_per_line.value', float(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.time_per_line.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.time_per_line.unit', str(new_val))


class RootWorkflowImagingPropertyScan_mode(wrap.CmdTreeProp):

    class EnumType(Enum):
        Continuous = 'Continuous'
        Single_Frame = 'Single Frame'

    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.scan_mode'
        self._lua_value_type = wrap.LuaType('str')

    @property
    def value(self) -> EnumType:
        return RootWorkflowImagingPropertyScan_mode.EnumType(self._context.get('root.workflow.imaging.property.scan_mode.value'))

    @value.setter
    def value(self, new_val:EnumType):
        self._context.set('root.workflow.imaging.property.scan_mode.value', new_val.value)

    @property
    def enum(self) -> list:
        return list(self._context.get('root.workflow.imaging.property.scan_mode.enum'))

    @enum.setter
    def enum(self, new_val:list):
        self._context.set('root.workflow.imaging.property.scan_mode.enum', list(new_val))


class RootWorkflowImagingPropertyLine_rate(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.line_rate'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.line_rate.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.line_rate.value', int(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.line_rate.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.line_rate.unit', str(new_val))


class RootWorkflowImagingPropertyRotation(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.rotation'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.rotation.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.rotation.value', int(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.rotation.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.rotation.unit', str(new_val))


class RootWorkflowImagingPropertyPoints_per_line(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.points_per_line'
        self._lua_value_type = wrap.LuaType('int')

    @property
    def value(self) -> int:
        return int(self._context.get('root.workflow.imaging.property.points_per_line.value'))

    @value.setter
    def value(self, new_val:int):
        self._context.set('root.workflow.imaging.property.points_per_line.value', int(new_val))


class RootWorkflowImagingPropertyTip_velocity(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.tip_velocity'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.tip_velocity.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.tip_velocity.value', float(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.tip_velocity.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.tip_velocity.unit', str(new_val))


class RootWorkflowImagingPropertyMove_speed_xy(wrap.CmdTreeProp):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property.move_speed_xy'
        self._lua_value_type = wrap.LuaType('float')

    @property
    def value(self) -> float:
        return float(self._context.get('root.workflow.imaging.property.move_speed_xy.value'))

    @value.setter
    def value(self, new_val:float):
        self._context.set('root.workflow.imaging.property.move_speed_xy.value', float(new_val))

    @property
    def unit(self) -> str:
        return str(self._context.get('root.workflow.imaging.property.move_speed_xy.unit'))

    @unit.setter
    def unit(self, new_val:str):
        self._context.set('root.workflow.imaging.property.move_speed_xy.unit', str(new_val))


class RootWorkflowImagingProperty(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging.property'
        self.move_speed_xy = RootWorkflowImagingPropertyMove_speed_xy(self._context)
        self.tip_velocity = RootWorkflowImagingPropertyTip_velocity(self._context)
        self.points_per_line = RootWorkflowImagingPropertyPoints_per_line(self._context)
        self.rotation = RootWorkflowImagingPropertyRotation(self._context)
        self.line_rate = RootWorkflowImagingPropertyLine_rate(self._context)
        self.scan_mode = RootWorkflowImagingPropertyScan_mode(self._context)
        self.time_per_line = RootWorkflowImagingPropertyTime_per_line(self._context)
        self.slow_axis_scan_direction = RootWorkflowImagingPropertySlow_axis_scan_direction(self._context)
        self.slope_x = RootWorkflowImagingPropertySlope_x(self._context)
        self.scan_range_fast_axis = RootWorkflowImagingPropertyScan_range_fast_axis(self._context)
        self.image_offset_x = RootWorkflowImagingPropertyImage_offset_x(self._context)
        self.slope_y = RootWorkflowImagingPropertySlope_y(self._context)
        self.image_offset_y = RootWorkflowImagingPropertyImage_offset_y(self._context)
        self.scan_range_slow_axis = RootWorkflowImagingPropertyScan_range_slow_axis(self._context)
        self.lines_per_frame = RootWorkflowImagingPropertyLines_per_frame(self._context)


class RootWorkflowImaging(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.imaging'
        self.property = RootWorkflowImagingProperty(self._context)
        self.var = RootWorkflowImagingVar(self._context)
        self.signal = RootWorkflowImagingSignal(self._context)

    def is_scanning(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.is_scanning', *args)

    def start_imaging(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.start_imaging', *args)

    def stop_imaging(self, *args) -> Any:
        return self._context.call('root.workflow.imaging.stop_imaging', *args)


class RootWorkflowApproach(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach'


class RootWorkflowWorkspace(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.workspace'


class RootWorkflowCantilever(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.cantilever'


class RootWorkflowOrt(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.ort'


class RootWorkflowCamera_properties(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.camera_properties'


class RootWorkflowLaser_align(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.laser_align'


class RootWorkflowApproach_motors(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.approach_motors'


class RootWorkflowStorage(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.storage'


class RootWorkflow(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow'
        self.storage = RootWorkflowStorage(self._context)
        self.approach_motors = RootWorkflowApproach_motors(self._context)
        self.laser_align = RootWorkflowLaser_align(self._context)
        self.camera_properties = RootWorkflowCamera_properties(self._context)
        self.ort = RootWorkflowOrt(self._context)
        self.cantilever = RootWorkflowCantilever(self._context)
        self.workspace = RootWorkflowWorkspace(self._context)
        self.approach = RootWorkflowApproach(self._context)
        self.imaging = RootWorkflowImaging(self._context)
        self.manager = RootWorkflowManager(self._context)
        self.z_controller = RootWorkflowZ_controller(self._context)
        self.spm_resource_requester = RootWorkflowSpm_resource_requester(self._context)
        self.xy_closed_loop = RootWorkflowXy_closed_loop(self._context)
        self.thermal_tune = RootWorkflowThermal_tune(self._context)
        self.parameters = RootWorkflowParameters(self._context)
        self.system_startup = RootWorkflowSystem_startup(self._context)
        self.preset_loader = RootWorkflowPreset_loader(self._context)
        self.measurement_setup = RootWorkflowMeasurement_setup(self._context)


class RootSession(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.session'

    def select_main(self, *args) -> Any:
        return self._context.call('root.session.select_main', *args)

    def list(self, *args) -> Any:
        return self._context.call('root.session.list', *args)

    @property
    def current_connection(self) -> str:
        return str(self._context.get('root.session.current_connection'))

    @current_connection.setter
    def current_connection(self, new_val:str):
        self._context.set('root.session.current_connection', str(new_val))

    @property
    def name(self) -> str:
        return str(self._context.get('root.session.name'))

    @name.setter
    def name(self, new_val:str):
        self._context.set('root.session.name', str(new_val))

    def select(self, *args) -> Any:
        return self._context.call('root.session.select', *args)


class RootCoreCore_cantilever(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.core_cantilever'


class RootCoreApproach_motors_drive(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach_motors_drive'


class RootCoreDirect_motor_control(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.direct_motor_control'


class RootCorePosition_control(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.position_control'


class RootCoreSignal_store(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.signal_store'


class RootCoreLaser_align_drive_impl(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.laser_align_drive_impl'


class RootCoreZ_controller(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.z_controller'


class RootCoreScan_head_calibration(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.scan_head_calibration'


class RootCoreCore_environment(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.core_environment'


class RootCoreOscilloscope(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.oscilloscope'


class RootCoreImaging(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.imaging'


class RootCoreApproach(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.approach'


class RootCoreAcquisition(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.acquisition'


class RootCoreCore_monitoring(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.core_monitoring'


class RootCoreConverter_channel_correction(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.converter_channel_correction'


class RootCoreOrt(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.ort'


class RootCoreThermal_tune(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.thermal_tune'


class RootCoreHv_amp_control(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.hv_amp_control'


class RootCoreCore_options(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.core_options'


class RootCore(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core'
        self.core_options = RootCoreCore_options(self._context)
        self.hv_amp_control = RootCoreHv_amp_control(self._context)
        self.thermal_tune = RootCoreThermal_tune(self._context)
        self.ort = RootCoreOrt(self._context)
        self.converter_channel_correction = RootCoreConverter_channel_correction(self._context)
        self.core_monitoring = RootCoreCore_monitoring(self._context)
        self.acquisition = RootCoreAcquisition(self._context)
        self.approach = RootCoreApproach(self._context)
        self.imaging = RootCoreImaging(self._context)
        self.oscilloscope = RootCoreOscilloscope(self._context)
        self.core_environment = RootCoreCore_environment(self._context)
        self.scan_head_calibration = RootCoreScan_head_calibration(self._context)
        self.z_controller = RootCoreZ_controller(self._context)
        self.laser_align_drive_impl = RootCoreLaser_align_drive_impl(self._context)
        self.signal_store = RootCoreSignal_store(self._context)
        self.position_control = RootCorePosition_control(self._context)
        self.direct_motor_control = RootCoreDirect_motor_control(self._context)
        self.approach_motors_drive = RootCoreApproach_motors_drive(self._context)
        self.core_cantilever = RootCoreCore_cantilever(self._context)


class RootUtil(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.util'

    def list_table_elements(self, *args) -> Any:
        return self._context.call('root.util.list_table_elements', *args)

    def deep_copy(self, *args) -> Any:
        return self._context.call('root.util.deep_copy', *args)

    def array_concat(self, *args) -> Any:
        return self._context.call('root.util.array_concat', *args)

    def make_property(self, *args) -> Any:
        return self._context.call('root.util.make_property', *args)

    def to_string(self, *args) -> Any:
        return self._context.call('root.util.to_string', *args)

    def table_append(self, *args) -> Any:
        return self._context.call('root.util.table_append', *args)

    def list_table_vars(self, *args) -> Any:
        return self._context.call('root.util.list_table_vars', *args)

    def list_table_tables(self, *args) -> Any:
        return self._context.call('root.util.list_table_tables', *args)

    def list_table_functions(self, *args) -> Any:
        return self._context.call('root.util.list_table_functions', *args)

    def list_table_all(self, *args) -> Any:
        return self._context.call('root.util.list_table_all', *args)

    def filter_string_array_begin(self, *args) -> Any:
        return self._context.call('root.util.filter_string_array_begin', *args)


class RootLu(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.lu'


class Root(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root'
        self.lu = RootLu(self._context)
        self.util = RootUtil(self._context)
        self.core = RootCore(self._context)
        self.session = RootSession(self._context)
        self.workflow = RootWorkflow(self._context)
        self.test = RootTest(self._context)

    def log_info(self, *args) -> Any:
        return self._context.call('root.log_info', *args)

    def log_debug(self, *args) -> Any:
        return self._context.call('root.log_debug', *args)

    def log_error(self, *args) -> Any:
        return self._context.call('root.log_error', *args)

    def log_warn(self, *args) -> Any:
        return self._context.call('root.log_warn', *args)

    def log_fatal(self, *args) -> Any:
        return self._context.call('root.log_fatal', *args)


