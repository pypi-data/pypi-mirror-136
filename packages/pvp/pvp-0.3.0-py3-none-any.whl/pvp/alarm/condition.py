import operator
import types
import importlib
import copy


from pvp.alarm import AlarmType, AlarmSeverity
from pvp.common.message import SensorValues
from pvp.common.values import ValueName

def get_alarm_manager():
    try:
        return Alarm_Manager()
    except:
        manager_module = importlib.import_module('pvp.alarm.alarm_manager')
        globals()['Alarm_Manager'] = getattr(manager_module, 'Alarm_Manager')
        return Alarm_Manager()


class Condition(object):
    """
    Base class for specifying alarm test conditions

    Subclasses must define :meth:`.Condition.check` and :meth:`.Conditino.reset`

    Condition objects can be added together to create compound conditions.

    Attributes:
        _child (:class:`Condition`): if another condition is added to this one, store a reference to it
        """

    def __init__(self, depends: dict = None, *args, **kwargs):
        """

        Args:
            depends (list, dict): a list of, or a single dict::

                {'value_name':ValueName,
                'value_attr': attr in ControlMessage,
                 'condition_attr',
                 optional: transformation: callable)
                that declare what values are needed to update
            *args:
            **kwargs:
        """

        self._manager = None
        self._child = None
        self._check = None
        self.depends = depends

    @property
    def manager(self):
        """
        The active alarm manager, used to get status of alarms

        Returns:
            :class:`pvp.alarm.alarm_manager.Alarm_Manager`
        """
        if self._manager is None:
            self._manager = get_alarm_manager()
        return self._manager

    def check(self, sensor_values) -> bool:
        """
        Every Condition subclass needs to define this method that accepts :class:`.SensorValues` and returns a boolean

        Args:
            sensor_values ( :class:`.SensorValues` ): SensorValues used to compute alarm status

        Returns:
            bool
        """
        raise NotImplementedError("Every condition needs to override check!!")

    def reset(self):
        """
        If a condition is stateful, need to provide some method of resetting the state
        """
        raise NotImplementedError("every condition needs to override reset!")

    def __add__(self, other: 'Condition'):
        """
        Add another :class:`Condition` object to check in series.

        Conditions are evaluated left-to-right, and return if any along the sequence is False

        Args:
            other (:class:`Condition`)
        """
        # can't just add any ole apples n oranges
        assert(issubclass(type(other), Condition))

        _self = copy.deepcopy(self)

        if _self._child is None:
            # if something hasn't been added to us yet...
            # claim our child
            _self._child = other

            # override our check method so we check recursively
            # make a quick backup first tho yno
            _self._check = _self.check
            _self._reset = _self.reset

            def new_check(self, sensor_values):
                if not self._check(sensor_values):
                    # if our stashed condition check is false,
                    # return immediately
                    return False
                else:
                    # otherwise call check (potentially recursively)
                    return self._child.check(sensor_values)

            # use python types to programmatically reassign method
            _self.check = types.MethodType(new_check, _self)

            def new_reset(self):
                self._reset()
                self._child.reset()

            _self.reset = types.MethodType(new_reset, _self)

        else:
            # if we have already had something added to us,
            # add it to our child instead, (also potentially recursively)
            _self._child = _self._child + other

        return _self


class ValueCondition(Condition):
    """
    Value is greater or lesser than some max/min
    """

    def __init__(self,
                 value_name: ValueName,
                 limit: (int, float),
                 mode: str,
                 *args, **kwargs):
        """

        Args:
            value_name (ValueName): Which value to check
            limit (int, float): value to check against
            mode ('min', 'max'): whether the limit is a minimum or maximum
            *args:
            **kwargs:

        Attributes:
            operator (callable): Either the less than or greater than operators, depending on whether mode is ``'min'`` or ``'max'``
        """
        super(ValueCondition, self).__init__(*args, **kwargs)

        # self.arguments = [value_name]
        self.value_name = value_name
        self.limit = limit

        self._mode = None
        self.operator = None
        self.mode = mode

    @property
    def mode(self):
        """
        One of 'min' or 'max', defines how the incoming sensor values are compared to the set value

        Returns:

        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        assert(mode in ('min', 'max'))
        if mode == 'min':
            # if we're a minimum, True (raise alarm) if value is less than limit
            self.operator = operator.lt
        elif mode == 'max':
            self.operator = operator.gt
        else: # pragma: no cover
            raise ValueError('needs to be max or min')
        self._mode = mode

    def check(self, sensor_values):
        """
        Check that the relevant value in SensorValues is either greater or lesser than the limit

        Args:
            sensor_values ( :class:`.SensorValues` ):

        Returns:
            bool
        """
        assert(isinstance(sensor_values, SensorValues))
        return self.operator(sensor_values[self.value_name], self.limit)

    def reset(self): # pragma: no cover
        """
        not stateful, do nothing.
        """
        pass


class CycleValueCondition(ValueCondition):
    """
    Value goes out of range for a specific number of breath cycles

    Args:
        n_cycles (int): number of cycles required

    Attributes:
        _start_cycle (int): The breath cycle where the
        _mid_check (bool): whether a value has left the acceptable range and we are counting consecutive breath cycles
    """

    def __init__(self, n_cycles: int, *args, **kwargs):
        super(CycleValueCondition, self).__init__(*args, **kwargs)
        self._n_cycles = None
        self.n_cycles = n_cycles

        self._start_cycle = 0
        self._mid_check = False

    @property
    def n_cycles(self) -> int:
        """Number of cycles required"""
        return self._n_cycles

    @n_cycles.setter
    def n_cycles(self, n_cycles: int):
        if not isinstance(n_cycles, int): # pragma: no cover
            n_cycles = int(round(n_cycles))
        assert(n_cycles>0)
        self._n_cycles = n_cycles

    def check(self, sensor_values) -> bool:
        """
        Check if outside of range, and then check if number of breath cycles have elapsed

        Args:
            sensor_values ():

        Returns:
            bool
        """
        # first check if we are outside of the range
        if super(CycleValueCondition, self).check(sensor_values):

            breath_cycle = sensor_values.breath_count
            # if we're currently in a consecutive set of out-of-range alarms..
            # note: doing it this way because we *dont* want to alarm if there are
            # in-range values seen in the waiting period, but we *do* want to
            # alarm if we miss a value from a breath cycle but haven't seen any
            # in-range values.
            if self._mid_check:
                # if we have progressed the required number of cycles...
                if breath_cycle >= self._start_cycle + self.n_cycles:
                    return True
                else:
                    return False
            else:
                # otherwise, this is the first time we've gone out of bounds
                self._mid_check = True
                self._start_cycle = breath_cycle
                # don't check yet, n_cycles must > 0
                return False

        else:
            # if we're not outside the range, false.
            # reset the flag that says we're inside a check
            self._mid_check = False
            return False

    def reset(self):
        """
        Reset check status and start cycle
        """
        self._mid_check = False
        self._start_cycle = 0


class TimeValueCondition(ValueCondition): # pragma: no cover
    """
    value goes out of range for specific amount of time

    .. warning::

        Not implemented!
    """

    def __init__(self, time, *args, **kwargs):
        """

        Args:
            time (float): number of seconds value must be out of range
            *args:
            **kwargs:
        """
        super(TimeValueCondition, self).__init__(*args, **kwargs)
        self.time = time

        raise NotImplementedError('Time condition has not been implemented!')

    def check(self, sensor_values):
        pass

    def reset(self):
        pass

class AlarmSeverityCondition(Condition):

    def __init__(self,
                 alarm_type: AlarmType,
                 severity: AlarmSeverity,
                 mode: str = 'min',
                 *args, **kwargs):
        """
        Alarm is above or below a certain severity.

        Get alarm severity status from :meth:`.Alarm_Manager.get_alarm_severity` .

        Args:
            alarm_type ( :class:`.AlarmType` ): Alarm type to check
            severity ( :class:`.AlarmSeverity` ): Alarm severity to check against
            mode (str): one of 'min', 'equals',  or 'max'.
                'min' returns true if the alarm is at least this value
                (note the difference from ValueCondition which returns true if the alarm is less than..)
                and vice versa for 'max'.

                .. note::

                    'min' and 'max' use >= and <= rather than > and <

            *args:
            **kwargs:
        """
        super(AlarmSeverityCondition, self).__init__(*args, **kwargs)


        self.alarm_type = alarm_type
        self.severity = severity

        self._mode = None
        self.operator = None
        self.mode = mode

    @property
    def mode(self) -> str: # pragma: no cover
        """
        'min' returns true if the alarm is at least this value
        (note the difference from ValueCondition which returns true if the alarm is less than..)
        and vice versa for 'max'.

        .. note::

            'min' and 'max' use >= and <= rather than > and <

        Returns:
            str: one of 'min', 'equals',  or 'max'.
        """
        return self._mode

    @mode.setter
    def mode(self, mode: str):
        assert(mode in ('min', 'eq', 'max'))
        if mode == 'min':
            # if we're a minimum, True (raise alarm) if value is less than limit
            self.operator = operator.ge
        elif mode == 'eq':
            self.operator = operator.eq
        elif mode == 'max':
            self.operator = operator.le
        else: # pragma: no cover
            raise ValueError(f'needs to be max or min, got {mode}')
        self._mode = mode

    def check(self, sensor_values=None):
        alarm_severity = self.manager.get_alarm_severity(self.alarm_type)
        return self.operator(alarm_severity, self.severity)

    def reset(self): # pragma: no cover
        pass


class CycleAlarmSeverityCondition(AlarmSeverityCondition):
    """
    alarm goes out of range for a specific number of breath cycles

    .. todo::

        note that this is exactly the same as CycleValueCondition. Need to do the multiple inheritance thing

    Attributes:
        _start_cycle (int): The breath cycle where the
        _mid_check (bool): whether a value has left the acceptable range and we are counting consecutive breath cycles
    """

    def __init__(self, n_cycles, *args, **kwargs):
        super(CycleAlarmSeverityCondition, self).__init__(*args, **kwargs)
        self._n_cycles = None
        self.n_cycles = n_cycles

        self._start_cycle = 0
        self._mid_check = False

    @property
    def n_cycles(self):
        return self._n_cycles

    @n_cycles.setter
    def n_cycles(self, n_cycles):
        if not isinstance(n_cycles, int): # pragma: no cover
            n_cycles = int(round(n_cycles))
        assert(n_cycles>0)
        self._n_cycles = n_cycles

    def check(self, sensor_values):
        # first check if we are outside of the range
        if super(CycleAlarmSeverityCondition, self).check(sensor_values):

            breath_cycle = sensor_values.breath_count
            # if we're currently in a consecutive set of out-of-range alarms..
            # note: doing it this way because we *dont* want to alarm if there are
            # in-range values seen in the waiting period, but we *do* want to
            # alarm if we miss a value from a breath cycle but haven't seen any
            # in-range values.
            if self._mid_check:
                # if we have progressed the required number of cycles...
                if breath_cycle >= self._start_cycle + self.n_cycles:
                    return True
                else:
                    return False
            else:
                # otherwise, this is the first time we've gone out of bounds
                self._mid_check = True
                self._start_cycle = breath_cycle
                # don't check yet, n_cycles must > 0
                return False

        else: # pragma: no cover - usually this comes after a check for this that should return false, so we never reach here.
            # if we're not outside the range, false.
            # reset the flag that says we're inside a check
            self._mid_check = False
            return False

    def reset(self):
        self._mid_check = False
        self._start_cycle = 0