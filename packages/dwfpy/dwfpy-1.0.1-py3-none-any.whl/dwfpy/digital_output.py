"""
Digital Output module for Digilent WaveForms devices.
"""

#
# This file is part of dwfpy: https://github.com/mariusgreuel/dwfpy
# Copyright (C) 2019 Marius Greuel
#
# SPDX-License-Identifier: MIT
#

import math
from typing import Tuple
from . import bindings as api
from . import device as fwd
from .constants import (
    DigitalOutputMode, DigitalOutputIdle, DigitalOutputType,
    Status, TriggerSlope, TriggerSource)
from .helpers import Helpers


class DigitalOutput:
    """Digital Output module (Pattern Generator)."""

    class Trigger:
        """Represents the trigger unit of a digital output device."""

        def __init__(self, module):
            self._device = module.device

        @property
        def source(self) -> TriggerSource:
            """Gets or sets the current trigger source setting for the instrument."""
            return TriggerSource(api.dwf_digital_out_trigger_source_get(self._device.handle))

        @source.setter
        def source(self, value: TriggerSource) -> None:
            api.dwf_digital_out_trigger_source_set(self._device.handle, value)

        @property
        def slope(self) -> TriggerSlope:
            """Gets or sets the trigger slope for the instrument."""
            return TriggerSlope(api.dwf_digital_out_trigger_slope_get(self._device.handle))

        @slope.setter
        def slope(self, value: TriggerSlope) -> None:
            api.dwf_digital_out_trigger_slope_set(self._device.handle, value)

        @property
        def repeat(self) -> bool:
            """Gets or sets the repeat trigger option.
            To include the trigger in wait-run repeat cycles, set 'repeat' to True."""
            return bool(api.dwf_digital_out_repeat_trigger_get(self._device.handle))

        @repeat.setter
        def repeat(self, value: bool) -> None:
            api.dwf_digital_out_repeat_trigger_set(self._device.handle, value)

    class Channel:
        """Represents a Digital Output channel."""

        def __init__(self, module, channel):
            self._device = module.device
            self._module = module
            self._channel = channel
            self._label = 'dio' + str(channel)

        @property
        def device(self) -> 'fwd.Device':
            """Gets the device."""
            return self._device

        @property
        def module(self) -> 'DigitalOutput':
            """Gets the Digital Output module."""
            return self._module

        @property
        def index(self) -> int:
            """Gets the channel index."""
            return self._channel

        @property
        def label(self) -> str:
            """Gets or sets the channel label."""
            return self._label

        @label.setter
        def label(self, value: str) -> None:
            self._label = value

        @property
        def enabled(self) -> bool:
            """Enables or disables the channel."""
            return bool(api.dwf_digital_out_enable_get(self._device.handle, self._channel))

        @enabled.setter
        def enabled(self, value: bool) -> None:
            api.dwf_digital_out_enable_set(self._device.handle, self._channel, value)

        @property
        def output_mode_info(self) -> Tuple[DigitalOutputMode, ...]:
            """Gets the supported output modes."""
            return Helpers.map_enum_values(
                DigitalOutputMode, api.dwf_digital_out_output_info(self._device.handle, self._channel))

        @property
        def output_mode(self) -> DigitalOutputMode:
            """Gets or sets the output mode."""
            return DigitalOutputMode(
                api.dwf_digital_out_output_get(self._device.handle, self._channel))

        @output_mode.setter
        def output_mode(self, value: DigitalOutputMode) -> None:
            api.dwf_digital_out_output_set(self._device.handle, self._channel, value)

        @property
        def output_type_info(self) -> Tuple[DigitalOutputType, ...]:
            """Gets the supported output types."""
            return Helpers.map_enum_values(
                DigitalOutputType, api.dwf_digital_out_type_info(self._device.handle, self._channel))

        @property
        def output_type(self) -> DigitalOutputType:
            """Gets or sets the output type."""
            return DigitalOutputType(api.dwf_digital_out_type_get(self._device.handle, self._channel))

        @output_type.setter
        def output_type(self, value: DigitalOutputType) -> None:
            api.dwf_digital_out_type_set(self._device.handle, self._channel, value)

        @property
        def idle_state_info(self) -> Tuple[DigitalOutputIdle, ...]:
            """Gets the supported idle output states."""
            return Helpers.map_enum_values(
                DigitalOutputIdle, api.dwf_digital_out_idle_info(self._device.handle, self._channel))

        @property
        def idle_state(self) -> DigitalOutputIdle:
            """Gets or sets the idle output state."""
            return DigitalOutputIdle(api.dwf_digital_out_idle_get(self._device.handle, self._channel))

        @idle_state.setter
        def idle_state(self, value: DigitalOutputIdle) -> None:
            api.dwf_digital_out_idle_set(self._device.handle, self._channel, value)

        @property
        def divider_min(self) -> int:
            """Gets the minimum supported clock divider value."""
            return api.dwf_digital_out_divider_info(self._device.handle, self._channel)[0]

        @property
        def divider_max(self) -> int:
            """Gets the maximum supported clock divider value."""
            return api.dwf_digital_out_divider_info(self._device.handle, self._channel)[1]

        @property
        def initial_divider(self) -> int:
            """Gets or sets the initial divider value."""
            return api.dwf_digital_out_divider_init_get(self._device.handle, self._channel)

        @initial_divider.setter
        def initial_divider(self, value: int) -> None:
            api.dwf_digital_out_divider_init_set(self._device.handle, self._channel, value)

        @property
        def divider(self) -> int:
            """Gets or sets the divider value."""
            return api.dwf_digital_out_divider_get(self._device.handle, self._channel)

        @divider.setter
        def divider(self, value: int) -> None:
            api.dwf_digital_out_divider_set(self._device.handle, self._channel, value)

        @property
        def counter_min(self) -> int:
            """Gets the minimum supported clock counter value."""
            return api.dwf_digital_out_counter_info(self._device.handle, self._channel)[0]

        @property
        def counter_max(self) -> int:
            """Gets the maximum supported clock counter value."""
            return api.dwf_digital_out_counter_info(self._device.handle, self._channel)[1]

        @property
        def initial_state(self) -> bool:
            """Getsthe initial state."""
            return bool(api.dwf_digital_out_counter_init_get(self._device.handle, self._channel)[0])

        @property
        def initial_counter(self) -> int:
            """Gets the initial counter value."""
            return api.dwf_digital_out_counter_init_get(self._device.handle, self._channel)[1]

        @property
        def low_counter(self) -> int:
            """Gets the low counter value."""
            return api.dwf_digital_out_counter_get(self._device.handle, self._channel)[0]

        @property
        def high_counter(self) -> int:
            """Gets the high counter value."""
            return api.dwf_digital_out_counter_get(self._device.handle, self._channel)[1]

        def set_initial_state_and_counter(self, state: bool, counter: int) -> None:
            """Sets the initial state and the initial counter."""
            api.dwf_digital_out_counter_init_set(self._device.handle, self._channel, state, counter)

        def set_counter(self, low: int, high: int) -> None:
            """Sets the low and high counter values."""
            api.dwf_digital_out_counter_set(self._device.handle, self._channel, low, high)

        def setup(
                self,
                output_type=None,
                output_mode=None,
                idle_state=None,
                initial_state=None,
                divider=None,
                initial_divider=None,
                low_counter=None,
                high_counter=None,
                initial_counter=None,
                enabled=True,
                configure=False,
                start=False) -> None:
            """Sets up the channel.

            Parameters
            ----------
            output_type : str, optional
                The output type.
                Can be 'pulse', 'custom', 'random', 'rom', 'state', or 'play'.
            output_mode : str, optional
                The output mode.
                Can be 'push-pull', 'open-drain', 'open-source', or 'three-state'.
            idle_state : str or DigitalOutputIdle, optional
                The output idle state.
                Can be 'init', 'low', 'high', or 'z'.
            divider : int, optional
                The divider value.
            initial_divider : int, optional
                The initial divider value.
            low_counter : int, optional
                The low counter value.
            high_counter : int, optional
                The high counter value.
            initial_state : str or bool, optional
                The initial state. Can be 'low' or 'high'.
            initial_counter : int, optional
                The initial counter value.
            enabled : bool, optional
                If True, then the channel is enabled (default True).
            configure : bool, optional
                If True, then the instrument is configured (default False).
            start : bool, optional
                If True, then the instrument is started (default False).
            """
            if output_type is not None:
                self.output_type = Helpers.map_digital_output_type(output_type)
            if output_mode is not None:
                self.output_mode = Helpers.map_digital_output_mode(output_mode)
            if idle_state is not None:
                self.idle_state = Helpers.map_digital_output_idle(idle_state)
            if divider is not None:
                self.divider = divider
            if initial_divider is not None:
                self.initial_divider = initial_divider
            if low_counter is not None and high_counter is not None:
                self.set_counter(low_counter, high_counter)
            if initial_state is not None and initial_counter is not None:
                self.set_initial_state_and_counter(Helpers.map_state(initial_state), initial_counter)
            if enabled is not None:
                self.enabled = enabled
            if configure or start:
                self._device.configure(start=start)

        def setup_constant(
                self,
                value,
                output_mode=None,
                idle_state=None,
                enabled=True,
                configure=False,
                start=False) -> None:
            """Sets up the channel as a constant output.

            Parameters
            ----------
            value : str or bool
                The constant output value. Can be 'low' or 'high'.
            output_mode : str, optional
                The output mode.
                Can be 'push-pull', 'open-drain', 'open-source', or 'three-state'.
            idle_state : str, optional
                The output idle state.
                Can be 'init', 'low', 'high', or 'z'.
            enabled : bool, optional
                If True, then the channel is enabled (default True).
            configure : bool, optional
                If True, then the instrument is configured (default False).
            start : bool, optional
                If True, then the instrument is started (default False).
            """
            self.setup(
                output_type=DigitalOutputType.PULSE,
                low_counter=0,
                high_counter=0,
                initial_state=value,
                initial_counter=0,
                output_mode=output_mode,
                idle_state=idle_state,
                enabled=enabled,
                configure=configure,
                start=start)

        def setup_clock(
                self,
                frequency,
                duty_cycle=None,
                phase=None,
                delay=None,
                output_mode=None,
                idle_state=None,
                enabled=True,
                configure=False,
                start=False) -> None:
            """Sets up the channel as a clock output.

            Parameters
            ----------
            frequency : float
                The frequency in Hz.
            duty_cycle : float, optional
                The duty-cycle in percent (default 50).
            phase : float, optional
                The phase in degrees (default 0).
            delay : float, optional
                The delay in seconds (default 0).
            output_mode : str, optional
                The output mode.
                Can be 'push-pull', 'open-drain', 'open-source', or 'three-state'.
            idle_state : str, optional
                The output idle state.
                Can be 'init', 'low', 'high', or 'z'.
            enabled : bool, optional
                If True, then the channel is enabled (default True).
            configure : bool, optional
                If True, then the instrument is configured (default False).
            start : bool, optional
                If True, then the instrument is started (default False).
            """
            divider = math.ceil(self._module.clock_frequency / frequency / self.counter_max)
            clock_frequency = self._module.clock_frequency / divider

            total_counter = round(clock_frequency / frequency)
            high_counter = round(total_counter * duty_cycle / 100)
            low_counter = total_counter - high_counter

            phase_count = round(total_counter * phase / 360) % total_counter
            if phase_count < low_counter:
                initial_state = False
                initial_counter = low_counter - phase_count
            else:
                initial_state = True
                initial_counter = total_counter - phase_count

            initial_divider = round(delay * frequency / divider)

            self.setup(
                output_type=DigitalOutputType.PULSE,
                divider=divider,
                initial_divider=initial_divider,
                low_counter=low_counter,
                high_counter=high_counter,
                initial_counter=initial_counter,
                initial_state=initial_state,
                output_mode=output_mode,
                idle_state=idle_state,
                enabled=enabled,
                configure=configure,
                start=start)

        def setup_pulse(
                self,
                low_duration,
                high_duration,
                delay=None,
                output_mode=None,
                idle_state=None,
                enabled=True,
                configure=False,
                start=False) -> None:
            """Sets up the channel as a pulse output.

            Parameters
            ----------
            low_duration : int, optional
                The duration of the low state in seconds.
            high_duration : int, optional
                The duration of the high state in seconds.
            delay : float, optional
                The delay in seconds (default 0).
            output_mode : str, optional
                The output mode.
                Can be 'push-pull', 'open-drain', 'open-source', or 'three-state'.
            idle_state : str, optional
                The output idle state.
                Can be 'init', 'low', 'high', or 'z'.
            enabled : bool, optional
                If True, then the channel is enabled (default True).
            configure : bool, optional
                If True, then the instrument is configured (default False).
            start : bool, optional
                If True, then the instrument is started (default False).
            """
            total_duration = low_duration + high_duration
            frequency = 1 / total_duration

            divider = math.ceil(self._module.clock_frequency / frequency / self.counter_max)
            clock_frequency = self._module.clock_frequency / divider

            total_counter = round(clock_frequency / frequency)
            high_counter = round(total_counter * high_duration / total_duration)
            low_counter = total_counter - high_counter

            phase_count = round(total_counter * 0 / 360) % total_counter
            if phase_count < low_counter:
                initial_state = False
                initial_counter = low_counter - phase_count
            else:
                initial_state = True
                initial_counter = total_counter - phase_count

            initial_counter = round(delay / clock_frequency)

            self.setup(
                output_type=DigitalOutputType.PULSE,
                divider=divider,
                initial_divider=0,
                low_counter=low_counter,
                high_counter=high_counter,
                initial_counter=initial_counter,
                initial_state=initial_state,
                output_mode=output_mode,
                idle_state=idle_state,
                enabled=enabled,
                configure=configure,
                start=start)

        def setup_random(
                self,
                rate,
                delay=None,
                output_mode=None,
                idle_state=None,
                enabled=True,
                configure=False,
                start=False) -> None:
            """Sets up the channel as a random output.

            Parameters
            ----------
            rate : float
                The bit rate in bits/second.
            delay : float, optional
                The delay in seconds (default 0).
            output_mode : str, optional
                The output mode.
                Can be 'push-pull', 'open-drain', 'open-source', or 'three-state'.
            idle_state : str, optional
                The output idle state.
                Can be 'init', 'low', 'high', or 'z'.
            enabled : bool, optional
                If True, then the channel is enabled (default True).
            configure : bool, optional
                If True, then the instrument is configured (default False).
            start : bool, optional
                If True, then the instrument is started (default False).
            """
            divider = math.ceil(self._module.clock_frequency / rate / self.counter_max)
            clock_frequency = self._module.clock_frequency / divider
            total_counter = round(clock_frequency / rate)
            initial_counter = round(delay / clock_frequency)
            self.setup(
                output_type=DigitalOutputType.RANDOM,
                divider=divider,
                low_counter=total_counter,
                high_counter=total_counter,
                initial_counter=initial_counter,
                output_mode=output_mode,
                idle_state=idle_state,
                enabled=enabled,
                configure=configure,
                start=start)

    def __init__(self, device):
        self._device = device
        self._trigger = self.Trigger(self)
        self._channels = tuple(self.Channel(self, i) for i in range(
            api.dwf_digital_out_count(self._device.handle)))

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback) -> None:
        del _type, _value, _traceback
        self.reset()

    @property
    def device(self) -> 'fwd.Device':
        """Gets the device."""
        return self._device

    @property
    def trigger(self) -> Trigger:
        """Gets the trigger unit."""
        return self._trigger

    @property
    def channels(self) -> Tuple[Channel, ...]:
        """Gets a collection of Digital Output channels."""
        return self._channels

    def __getitem__(self, key) -> Channel:
        if isinstance(key, int):
            return self._channels[key]

        if isinstance(key, str):
            for channel in self._channels:
                if channel.label == key:
                    return channel

        raise IndexError(key)

    @property
    def clock_frequency(self) -> float:
        """Gets the internal clock frequency in Hz."""
        return api.dwf_digital_out_internal_clock_info(self._device.handle)

    @property
    def run_length_min(self) -> float:
        """Gets the minimum run length in seconds."""
        return api.dwf_digital_out_run_info(self._device.handle)[0]

    @property
    def run_length_max(self) -> float:
        """Gets the maximum run length in seconds."""
        return api.dwf_digital_out_run_info(self._device.handle)[1]

    @property
    def run_length(self) -> float:
        """Gets or sets the run length in seconds."""
        return api.dwf_digital_out_run_get(self._device.handle)

    @run_length.setter
    def run_length(self, value: float) -> None:
        api.dwf_digital_out_run_set(self._device.handle, value)

    @property
    def run_length_status(self) -> float:
        """Gets the remaining run length in seconds."""
        return api.dwf_digital_out_run_status(self._device.handle)

    @property
    def wait_length_min(self) -> float:
        """Gets the minimum wait length in seconds."""
        return api.dwf_digital_out_wait_info(self._device.handle)[0]

    @property
    def wait_length_max(self) -> float:
        """Gets the maximum wait length in seconds."""
        return api.dwf_digital_out_wait_info(self._device.handle)[1]

    @property
    def wait_length(self) -> float:
        """Gets or sets the wait length in seconds."""
        return api.dwf_digital_out_wait_get(self._device.handle)

    @wait_length.setter
    def wait_length(self, value: float) -> None:
        api.dwf_digital_out_wait_set(self._device.handle, value)

    @property
    def repeat_count_min(self) -> int:
        """Gets the minimum repeat count."""
        return api.dwf_digital_out_repeat_info(self._device.handle)[0]

    @property
    def repeat_count_max(self) -> int:
        """Gets the maximum repeat count."""
        return api.dwf_digital_out_repeat_info(self._device.handle)[1]

    @property
    def repeat_count(self) -> int:
        """Gets or sets the repeat count."""
        return api.dwf_digital_out_repeat_get(self._device.handle)

    @repeat_count.setter
    def repeat_count(self, value: int) -> None:
        api.dwf_digital_out_repeat_set(self._device.handle, value)

    @property
    def repeat_count_status(self) -> float:
        """Gets the remaining repeat count."""
        return api.dwf_digital_out_repeat_status(self._device.handle)

    def reset(self) -> None:
        """Resets and configures all instrument parameters to default values."""
        api.dwf_digital_out_reset(self._device.handle)

    def configure(self, start=False) -> None:
        """Configures and starts the instrument."""
        api.dwf_digital_out_configure(self._device.handle, start)

    def read_status(self) -> Status:
        """Gets the instrument status."""
        return Status(api.dwf_digital_out_status(self._device.handle))

    def setup(
            self,
            run_length=None,
            wait_length=None,
            repeat_count=None,
            configure=False,
            start=False) -> None:
        """Sets up the pattern generator.

        Parameters
        ----------
        run_length : float, optional
            The run length in seconds.
        wait_length : float, optional
            The wait length in seconds.
        repeat_count : int, optional
            The repeat count.
        configure : bool, optional
            If True, then the instrument is configured (default False).
        start : bool, optional
            If True, then the instrument is started (default False).
        """
        if run_length is not None:
            self.run_length = run_length
        if wait_length is not None:
            self.wait_length = wait_length
        if repeat_count is not None:
            self.repeat_count = repeat_count
        if configure or start:
            self.configure(start=start)
