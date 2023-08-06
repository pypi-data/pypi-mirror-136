from enum import Enum, IntEnum, auto

class AlarmType(Enum):
    LOW_PRESSURE  = auto()  # low airway pressure alarm
    HIGH_PRESSURE = auto()  # high airway pressure alarm
    LOW_VTE       = auto()  # low VTE
    HIGH_VTE      = auto()
    LOW_PEEP      = auto()
    HIGH_PEEP     = auto()
    LOW_O2        = auto()
    HIGH_O2       = auto()
    OBSTRUCTION   = auto()
    LEAK          = auto()
    SENSORS_STUCK = auto()
    BAD_SENSOR_READINGS = auto()
    MISSED_HEARTBEAT = auto()

    @property
    def human_name(self) -> str:
        """Replace ``.name`` underscores with spaces"""
        return self.name.replace('_', ' ')


class AlarmSeverity(IntEnum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    OFF = 0
    TECHNICAL = -1

from pvp.alarm import condition
from pvp.alarm import AlarmType, AlarmSeverity
from pvp.alarm.rule import Alarm_Rule
from pvp.alarm.alarm import Alarm
from pvp.alarm.alarm_manager import Alarm_Manager
from pvp.common.values import ValueName, VALUES
from collections import OrderedDict as odict


ALARM_RULES = odict({
    AlarmType.LOW_PRESSURE: Alarm_Rule(
        name = AlarmType.LOW_PRESSURE,
        latch = False,
        conditions = (
            (
            AlarmSeverity.LOW,
                condition.ValueCondition(
                    value_name=ValueName.PIP,
                    limit=VALUES[ValueName.PIP]['safe_range'][0],
                    mode='min',
                    depends={
                        'value_name': ValueName.PIP,
                        'value_attr': 'value',
                        'condition_attr': 'limit',
                        'transform': lambda x : x-(x*0.10)
                    }
                )
            ),
            (
            AlarmSeverity.MEDIUM,
                condition.ValueCondition(
                    value_name=ValueName.PIP,
                    limit=VALUES[ValueName.PIP]['safe_range'][0]- \
                          VALUES[ValueName.PIP]['safe_range'][0]*0.15,
                    depends={
                        'value_name': ValueName.PIP,
                        'value_attr': 'value',
                        'condition_attr': 'limit',
                        'transform': lambda x: x - (x * 0.15)
                    },
                    mode='min'
                ) + \
                condition.CycleAlarmSeverityCondition(
                    alarm_type = AlarmType.LOW_PRESSURE,
                    severity   = AlarmSeverity.LOW,
                    n_cycles = 2
                )
            )
        )
    ),
    AlarmType.HIGH_PRESSURE: Alarm_Rule(
        name = AlarmType.HIGH_PRESSURE,
        latch = True,
        conditions = (
            (
            AlarmSeverity.HIGH,
                condition.ValueCondition(
                    value_name=ValueName.PRESSURE,
                    limit=VALUES[ValueName.PIP]['safe_range'][1],
                    mode='max',
                    depends={
                        'value_name': ValueName.PIP,
                        'value_attr': 'value',
                        'condition_attr': 'limit',
                        'transform': lambda x : x+(x*0.15)
                    }
                )
            ),
        )
    ),
    AlarmType.LOW_VTE: Alarm_Rule(
        name = AlarmType.LOW_VTE,
        latch = False,
        conditions = (
            (
            AlarmSeverity.LOW,
                condition.ValueCondition(
                    value_name=ValueName.VTE,
                    limit=VALUES[ValueName.VTE]['safe_range'][0],
                    mode='min',
                    depends={
                        'value_name': ValueName.VTE,
                        'value_attr': 'value',
                        'condition_attr': 'limit',
                        'transform': lambda x : x-(x*0.15)
                    }
                )
            ),
            (
            AlarmSeverity.MEDIUM,
                condition.ValueCondition(
                    value_name=ValueName.VTE,
                    limit=VALUES[ValueName.VTE]['safe_range'][0]- \
                          VALUES[ValueName.VTE]['safe_range'][0]*0.15,
                    mode='min',
                    depends={
                        'value_name': ValueName.VTE,
                        'value_attr': 'value',
                        'condition_attr': 'limit',
                        'transform': lambda x : x-(x*0.25)
                    }
                ) + \
                condition.CycleAlarmSeverityCondition(
                    alarm_type = AlarmType.LOW_VTE,
                    severity   = AlarmSeverity.LOW,
                    n_cycles = 2
                )
            )
        )
    ),
    AlarmType.HIGH_VTE: Alarm_Rule(
        name = AlarmType.HIGH_VTE,
        latch = False,
        conditions = (
            (
            AlarmSeverity.LOW,
                condition.ValueCondition(
                    value_name=ValueName.VTE,
                    limit=VALUES[ValueName.VTE]['safe_range'][1],
                    mode='max',
                    depends={
                        'value_name': ValueName.VTE,
                        'value_attr': 'value',
                        'condition_attr': 'limit',
                        'transform': lambda x : x+(x*0.15)
                    }
                )
            ),
            (
            AlarmSeverity.MEDIUM,
                condition.ValueCondition(
                    value_name=ValueName.VTE,
                    limit=VALUES[ValueName.VTE]['safe_range'][1]+ \
                          VALUES[ValueName.VTE]['safe_range'][1]*0.15,
                    mode='max',
                    depends={
                        'value_name': ValueName.VTE,
                        'value_attr': 'value',
                        'condition_attr': 'limit',
                        'transform': lambda x : x+(x*0.25)
                    }
                ) + \
                condition.CycleAlarmSeverityCondition(
                    alarm_type = AlarmType.HIGH_VTE,
                    severity   = AlarmSeverity.LOW,
                    n_cycles = 2
                )
            )
        )
    ),
    AlarmType.LOW_PEEP: Alarm_Rule(
        name = AlarmType.LOW_PEEP,
        latch = False,
        conditions = (
            (
            AlarmSeverity.MEDIUM,
                condition.ValueCondition(
                    value_name=ValueName.PEEP,
                    limit=VALUES[ValueName.PEEP]['safe_range'][0],
                    mode='min',
                    depends= {
                        'value_name': ValueName.PEEP,
                        'value_attr': 'value',
                        'condition_attr': 'limit',
                        'transform': lambda x : x-(x*0.15)
                    }
                )
            ),
        )
    ),
    AlarmType.HIGH_PEEP: Alarm_Rule(
        name = AlarmType.HIGH_PEEP,
        latch = False,
        conditions = (
            (
            AlarmSeverity.MEDIUM,
                condition.ValueCondition(
                    value_name=ValueName.PEEP,
                    limit=VALUES[ValueName.PEEP]['safe_range'][1],
                    mode='max',
                    depends={
                        'value_name': ValueName.PEEP,
                        'value_attr': 'value',
                        'condition_attr': 'limit',
                        'transform': lambda x: x + (x * 0.15)
                    }
                )
            ),
        )
    ),

    AlarmType.LOW_O2: Alarm_Rule(
        name=AlarmType.LOW_O2,
        latch=False,
        conditions=(
            (
                AlarmSeverity.MEDIUM,
                condition.ValueCondition(
                    value_name=ValueName.FIO2,
                    limit=VALUES[ValueName.FIO2]['safe_range'][0],
                    mode='min'
                )
            ),
        )
    ),
    AlarmType.HIGH_O2: Alarm_Rule(
        name=AlarmType.HIGH_O2,
        latch=False,
        conditions=(
            (
                AlarmSeverity.MEDIUM,
                condition.ValueCondition(
                    value_name=ValueName.FIO2,
                    limit=VALUES[ValueName.FIO2]['safe_range'][1],
                    mode='max'
                )
            ),
        )
    ),
})
"""
Definitions of all :class:`.Alarm_Rule` s used by the :class:`.Alarm_Manager`

See definitions `here <_modules/pvp/alarm.html>`_
"""

