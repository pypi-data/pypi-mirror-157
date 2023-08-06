#: L23 Port TSN Extension Commands

from dataclasses import dataclass
import typing
import functools

from ..protocol.command_builders import (
    build_get_request,
    build_set_request
)
from .. import interfaces
from ..transporter.token import Token
from ..protocol.fields.data_types import *
from ..protocol.fields.field import XmpField
from ..registry import register_command
from .enums import *

@register_command
@dataclass
class XP_TSNINIT:
    """
    Initialize shadow configuration to defaults. Any non-applied changes are lost.
    """

    code: typing.ClassVar[int] = 4000
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class SetDataAttr:
        pass

    def set(self) -> "Token":
        """Initialize shadow configuration to defaults.
        """
        return Token(
            self._connection,
            build_set_request(
                self,
                module=self._module,
                port=self._port,
            ),
        )


@register_command
@dataclass
class XP_TSNAPPLY:
    """
    Apply configuration from shadow configuration onto working configuration.
    """

    code: typing.ClassVar[int] = 4001
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class SetDataAttr:
        pass

    def set(self) -> "Token":
        """Apply configuration from shadow configuration onto working configuration.
        """
        return Token(
            self._connection,
            build_set_request(
                self,
                module=self._module,
                port=self._port,
            ),
        )


@register_command
@dataclass
class XP_TSNISSHADOWDIRTY:
    """
    To determine if the shadow configuration matches the working configuration for a
    port, or not.
    """

    code: typing.ClassVar[int] = 4002
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        shadow_matches_working: XmpField[XmpByte] = XmpField(XmpByte, choices=YesNo)  # coded byte, whether shadow config matches the working config.

    def get(self) -> "Token[GetDataAttr]":
        """Get whether the shadow configuration matches the working configuration or not.

        :return: whether the shadow configuration matches the working configuration or not.
        :rtype: XP_TSNISSHADOWDIRTY.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNLOADMODE:
    """
    Enable/disable TSN configuration load mode.
    """

    code: typing.ClassVar[int] = 4005
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class SetDataAttr:
        mode: XmpField[XmpByte] = XmpField(
            XmpByte, choices=OnOff
        )  # coded byte, allow 'set' commands to address working (sw_sel = 1), but actually apply to shadow (sw_sel = 0).

    @dataclass(frozen=True)
    class GetDataAttr:
        mode: XmpField[XmpByte] = XmpField(
            XmpByte, choices=OnOff
        )  # coded byte, allow 'set' commands to address working (sw_sel = 1), but actually apply to shadow (sw_sel = 0).

    def get(self) -> "Token[GetDataAttr]":
        """Get TSN configuration load mode.

        :return: TSN configuration load mode
        :rtype: XP_TSNLOADMODE.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))

    def set(self, mode: OnOff) -> "Token":
        """Set TSN configuration load mode.

        :param mode: TSN configuration load mode
        :type mode: OnOff
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, mode=mode))

    set_off = functools.partialmethod(set, OnOff.OFF)
    """Disable TSN configuration load."""
    set_on = functools.partialmethod(set, OnOff.ON)
    """Enable TSN configuration load."""


@register_command
@dataclass
class XP_TSNPROFILE:
    """
    Select PTP configuration profile.

    * ``AUTOMOTIVE`` = select defaults suitable for automotive testing.
    
    * ``IEEE1588V2`` = select defaults suitable for PTP testing.

    .. note::
    
        ``IEEE1588V2`` is not supported yet.
    
    .. note::
    
        Selecting profile configures a number of internal as well as user-settable parameters to default values, so this command should be the first in a configuration after :class:`~xoa_driver.internals.core.commands.xp_commands.XP_TSNINIT`.

    """

    code: typing.ClassVar[int] = 4006
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        profile: XmpField[XmpByte] = XmpField(
            XmpByte, choices=TSNConfigProfile
        )  # coded byte, AUTOMOTIVE = select defaults suitable for automotive testing, IEEE1588V2 = select defaults suitable for PTP testing. Note: Selecting profile configures a number of internal as well as user-settable parameters to default values, so this command should be the first in a configuration after XP_TSNINIT. Note: IEEE1588V2 is not supported yet.

    @dataclass(frozen=True)
    class GetDataAttr:
        profile: XmpField[XmpByte] = XmpField(
            XmpByte, choices=TSNConfigProfile
        )  # coded byte, AUTOMOTIVE = select defaults suitable for automotive testing, IEEE1588V2 = select defaults suitable for PTP testing. Note: Selecting profile configures a number of internal as well as user-settable parameters to default values, so this command should be the first in a configuration after XP_TSNINIT. Note: IEEE1588V2 is not supported yet.

    def get(self) -> "Token[GetDataAttr]":
        """Get PTP configuration profile.

        :return: PTP configuration profile
        :rtype: XP_TSNPROFILE.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, profile: TSNConfigProfile) -> "Token":
        """Set PTP configuration profile.

        :param profile: PTP configuration profile
        :type profile: TSNConfigProfile
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex], profile=profile))

    set_automotive = functools.partialmethod(set, profile=TSNConfigProfile.AUTOMOTIVE)
    """Select defaults suitable for automotive testing."""
    set_ieee1588v2 = functools.partialmethod(set, profile=TSNConfigProfile.IEEE1588V2)
    """Select defaults suitable for PTP testing."""


@register_command
@dataclass
class XP_TSNROLE:
    """
    The TSN port role.

    * ``GRANDMASTER`` = select Grandmaster role
    
    * ``SLAVE`` = select Slave role
    """

    code: typing.ClassVar[int] = 4007
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        role: XmpField[XmpByte] = XmpField(XmpByte, choices=TSNPortRole)  # coded byte, GRANDMASTER = select Grandmaster role, SLAVE = select Slave role

    @dataclass(frozen=True)
    class GetDataAttr:
        role: XmpField[XmpByte] = XmpField(XmpByte, choices=TSNPortRole)  # coded byte, GRANDMASTER = select Grandmaster role, SLAVE = select Slave role

    def get(self) -> "Token[GetDataAttr]":
        """Get the TSN port role.

        :return: the TSN port role
        :rtype: XP_TSNROLE.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, role: TSNPortRole) -> "Token":
        """Set the TSN port role.

        :param role: the TSN port role
        :type role: TSNPortRole
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex], role=role))

    set_grandmaster = functools.partialmethod(set, role=TSNPortRole.GRANDMASTER)
    """Select Grandmaster role"""
    set_slave = functools.partialmethod(set, role=TSNPortRole.SLAVE)
    """Select Slave role"""


@register_command
@dataclass
class XP_TSNSYNCINTERVAL:
    """
    Interval between SYNC packets.
    """

    code: typing.ClassVar[int] = 4009
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        value: XmpField[XmpByte] = XmpField(XmpByte)  # byte, 2^exponent seconds between SYNC packets. Valid range: -7 (1/128 second) to 5 (32 seconds).

    @dataclass(frozen=True)
    class GetDataAttr:
        exponent: XmpField[XmpByte] = XmpField(XmpByte)  # byte, 2^exponent seconds between SYNC packets. Valid range: -7 (1/128 second) to 5 (32 seconds).

    def get(self) -> "Token[GetDataAttr]":
        """Get the interval between SYNC packets.

        :return: interval between SYNC packets.
        :rtype: XP_TSNSYNCINTERVAL.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, exponent: int) -> "Token":
        """Set the interval between SYNC packets.

        :param exponent: 2^exponent seconds between SYNC packets. Valid range: -7 (1/128 second) to 5 (32 seconds).
        :type exponent: int
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex], exponent=exponent))


@register_command
@dataclass
class XP_TSNPDELAYINTERVAL:
    """
    Interval between PDelay packets.
    """

    code: typing.ClassVar[int] = 4010
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        exponent: XmpField[XmpByte] = XmpField(XmpByte)  # byte, 2^exponent seconds between SYNC packets. Valid range: -7 (1/128 second) to 5 (32 seconds).

    @dataclass(frozen=True)
    class GetDataAttr:
        exponent: XmpField[XmpByte] = XmpField(XmpByte)  # byte, 2^exponent seconds between SYNC packets. Valid range: -7 (1/128 second) to 5 (32 seconds).

    def get(self) -> "Token[GetDataAttr]":
        """Get the interval between PDelay packets.

        :return: the interval between PDelay packets.
        :rtype: XP_TSNPDELAYINTERVAL.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, exponent: int) -> "Token":
        """Set the interval between PDelay packets.

        :param exponent: 2^exponent seconds between SYNC packets. Valid range: -7 (1/128 second) to 5 (32 seconds).
        :type exponent: int
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex], exponent=exponent))


@register_command
@dataclass
class XP_TSNDEVIATION:
    """
    Systematic Grandmaster clock deviation setup.
    """

    code: typing.ClassVar[int] = 4012
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        mode: XmpField[XmpByte] = XmpField(
            XmpByte, choices=TSNDeviationMode
        )  # coded byte, deviation mode. FIXED = fixed-interval, fixed-value deviations. (Future versions may support more modes.)
        first_clock_offset_dev: XmpField[XmpInt] = XmpField(XmpInt)  # signed integer, first clock offset deviation, ppm (microseconds)
        second_clock_offset_dev: XmpField[XmpInt] = XmpField(XmpInt)  # signed integer, second clock offset deviation, ppm (microseconds)
        interval: XmpField[XmpInt] = XmpField(XmpInt)  # unsigned integer, interval between change of deviation, ms (millisecond)

    @dataclass(frozen=True)
    class GetDataAttr:
        mode: XmpField[XmpByte] = XmpField(
            XmpByte, choices=TSNDeviationMode
        )  # coded byte, deviation mode. FIXED = fixed-interval, fixed-value deviations. (Future versions may support more modes.)
        first_clock_offset_dev: XmpField[XmpInt] = XmpField(XmpInt)  # signed integer, first clock offset deviation, ppm (microseconds)
        second_clock_offset_dev: XmpField[XmpInt] = XmpField(XmpInt)  # signed integer, second clock offset deviation, ppm (microseconds)
        interval: XmpField[XmpInt] = XmpField(XmpInt)  # unsigned integer, interval between change of deviation, ms (millisecond)

    def get(self) -> "Token[GetDataAttr]":
        """Get the systematic Grandmaster clock deviation setup.

        :return: systematic Grandmaster clock deviation setup
        :rtype: class XP_TSNDEVIATION.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, mode: TSNDeviationMode, first_clock_offset_dev: int, second_clock_offset_dev: int, interval: int) -> "Token":
        """Set the systematic Grandmaster clock deviation setup.

        :param mode: deviation mode. ``FIXED`` = fixed-interval, fixed-value deviations. (Future versions may support more modes.)
        :type mode: TSNDeviationMode
        :param first_clock_offset_dev: first clock offset deviation, ppm (microseconds)
        :type first_clock_offset_dev: int
        :param second_clock_offset_dev: second clock offset deviation, ppm (microseconds)
        :type second_clock_offset_dev: int
        :param interval: interval between change of deviation, ms (millisecond)
        :type interval: int
        """
        return Token(
            self._connection,
            build_set_request(
                self,
                module=self._module,
                port=self._port,
                indices=[self._sw_config_xindex],
                mode=mode,
                first_clock_offset_dev=first_clock_offset_dev,
                second_clock_offset_dev=second_clock_offset_dev,
                interval=interval,
            ),
        )

    set_fixed = functools.partialmethod(set, mode=TSNDeviationMode.FIXED)
    """Fixed-interval, fixed-value deviations"""


@register_command
@dataclass
class XP_TSNPORTINFO:
    """
    Local TSN port information.
    """

    code: typing.ClassVar[int] = 4013
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        clock_indentity: XmpField[XmpHex8] = XmpField(XmpHex8)  # 8 hex bytes, local clock identity.
        port_number: XmpField[XmpInt] = XmpField(XmpInt)  # integer, local port number.

    def get(self) -> "Token[GetDataAttr]":
        """Get local TSN port information.

        :return: local TSN port information.
        :rtype: XP_TSNPORTINFO.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNPRIORITY:
    """
    Local clock priority attributes.
    """

    code: typing.ClassVar[int] = 4014
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        prio_1: XmpField[XmpByte] = XmpField(XmpByte)  # byte, first priority attribute.
        prio_2: XmpField[XmpByte] = XmpField(XmpByte)  # byte, second priority attribute.

    @dataclass(frozen=True)
    class GetDataAttr:
        prio_1: XmpField[XmpByte] = XmpField(XmpByte)  # byte, first priority attribute.
        prio_2: XmpField[XmpByte] = XmpField(XmpByte)  # byte, second priority attribute.

    def get(self) -> "Token[GetDataAttr]":
        """Get local clock priority attributes.

        :return: local clock priority attributes.
        :rtype: XP_TSNPRIORITY.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, prio_1: int, prio_2: int) -> "Token":
        """Set local clock priority attributes.

        :param prio_1: first priority attribute
        :type prio_1: int
        :param prio_2: second priority attribute
        :type prio_2: int
        """
        return Token(
            self._connection, build_set_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex], prio_1=prio_1, prio_2=prio_2)
        )


@register_command
@dataclass
class XP_TSNCLOCKCLASS:
    """
    Local clock class attribute.
    """

    code: typing.ClassVar[int] = 4015
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        value: XmpField[XmpByte] = XmpField(XmpByte)  # byte, clock class attribute.

    @dataclass(frozen=True)
    class GetDataAttr:
        value: XmpField[XmpByte] = XmpField(XmpByte)  # byte, clock class attribute.

    def get(self) -> "Token[GetDataAttr]":
        """Get local clock class attribute.

        :return: local clock class attribute.
        :rtype: XP_TSNCLOCKCLASS.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, value: int) -> "Token":
        """Set local clock class attribute.

        :param value: clock class attribute.
        :type value: int
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex], value=value))


@register_command
@dataclass
class XP_TSNCLOCKACCURACY:
    """
    Local clock accuracy attribute.
    """

    code: typing.ClassVar[int] = 4016
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        value: XmpField[XmpByte] = XmpField(XmpByte)  # byte, clock accuracy attribute.

    @dataclass(frozen=True)
    class GetDataAttr:
        value: XmpField[XmpByte] = XmpField(XmpByte)  # byte, clock accuracy attribute.

    def get(self) -> "Token[GetDataAttr]":
        """Get local clock accuracy attribute.

        :return: local clock accuracy attribute.
        :rtype: XP_TSNCLOCKACCURACY.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, value: int) -> "Token":
        """Set local clock accuracy attribute.

        :param value: clock accuracy attribute
        :type value: int
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex], value=value))


@register_command
@dataclass
class XP_TSNTIMESOURCE:
    """
    Local clock Time Source attribute.
    """

    code: typing.ClassVar[int] = 4017
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        source: XmpField[XmpByte] = XmpField(XmpByte, choices=TSNTimeSource)  # coded byte, a time source value, as specified in the PTP standard.

    @dataclass(frozen=True)
    class GetDataAttr:
        source: XmpField[XmpByte] = XmpField(XmpByte, choices=TSNTimeSource)  # coded byte, a time source value, as specified in the PTP standard.

    def get(self) -> "Token[GetDataAttr]":
        """Get local clock Time Source attribute.

        :return: local clock Time Source attribute
        :rtype: XP_TSNTIMESOURCE.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, source: TSNTimeSource) -> "Token":
        """Set local clock Time Source attribute.

        :param source:  a time source value, as specified in the PTP standard
        :type source: TSNTimeSource
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex], source=source))

    set_atomic = functools.partialmethod(set, source=TSNTimeSource.ATOMIC)
    """Set local clock time source to Atomic."""
    set_gps = functools.partialmethod(set, source=TSNTimeSource.GPS)
    """Set local clock time source to GPS."""
    set_terrestrial = functools.partialmethod(set, source=TSNTimeSource.TERRESTRIAL)
    """Set local clock time source to Terrestrial."""
    set_ptp = functools.partialmethod(set, source=TSNTimeSource.PTP)
    """Set local clock time source to PTP."""
    set_ntp = functools.partialmethod(set, source=TSNTimeSource.NTP)
    """Set local clock time source to NTP."""
    set_hand_set = functools.partialmethod(set, source=TSNTimeSource.HAND_SET)
    """Set local clock time source to Handset."""
    set_other = functools.partialmethod(set, source=TSNTimeSource.OTHER)
    """Set local clock time source to Other."""
    set_internal_osc = functools.partialmethod(set, source=TSNTimeSource.INTERNAL_OSC)
    """Set local clock time source to Internal Oscillator."""


@register_command
@dataclass
class XP_TSNENABLE:
    """
    Whether to enable (start) or disable (stop) TSN when :class:`~xoa_driver.internals.core.commands.xp_commands.XP_TSNAPPLY` is called.
    """

    code: typing.ClassVar[int] = 4018
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int
    _sw_config_xindex: int

    @dataclass(frozen=True)
    class SetDataAttr:
        on_off: XmpField[XmpByte] = XmpField(
            XmpByte, choices=OnOff
        )  # coded byte, OFF = disable TSN when XP_TSNAPPLY is called, ON = enable TSN when XP_TSNAPPLY is called

    @dataclass(frozen=True)
    class GetDataAttr:
        on_off: XmpField[XmpByte] = XmpField(
            XmpByte, choices=OnOff
        )  # coded byte, OFF = disable TSN when XP_TSNAPPLY is called, ON = enable TSN when XP_TSNAPPLY is called

    def get(self) -> "Token[GetDataAttr]":
        """Get whether to enable (start) or disable (stop) TSN.

        :return: whether to enable (start) or disable (stop) TSN
        :rtype: XP_TSNENABLE.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex]))

    def set(self, on_off: OnOff) -> "Token":
        """Set whether to enable (start) or disable (stop) TSN.

        :param on_off: whether to enable (start) or disable (stop) TSN
        :type on_off: OnOff
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, indices=[self._sw_config_xindex], on_off=on_off))

    set_off = functools.partialmethod(set, on_off=OnOff.OFF)
    """Disable TSN when XP_TSNAPPLY is called."""
    set_on = functools.partialmethod(set, on_off=OnOff.ON)
    """Enable TSN when XP_TSNAPPLY is called."""


@register_command
@dataclass
class XP_TSNPEERINDICES:
    """
    Obtain the indices of peers currently known. Details can be retrieved with :class:`~xoa_driver.internals.core.commands.xp_commands.XP_TSNPEERINFO`.
    """

    code: typing.ClassVar[int] = 4019
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        indices: XmpField[XmpIntList] = XmpField(XmpIntList)  # list of integers, indices of a peer record retrievable with XP_TSNPEERINFO

    def get(self) -> "Token[GetDataAttr]":
        """Get the indices of peers currently known.

        :return: the indices of peers currently known
        :rtype: XP_TSNPEERINDICES.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNPEERINFO:
    """
    Information about a peer node.
    
    .. note::
    
        This command is not fully functional due to low-level bug. Only clock_identity and port_number will contain meaningful info.

    """

    code: typing.ClassVar[int] = 4020
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        clock_indentity: XmpField[XmpHex8] = XmpField(XmpHex8)  # 8 hex bytes, peer clock identity
        port_number: XmpField[XmpInt] = XmpField(XmpInt)  # integer, peer port number
        physical_address: XmpField[XmpMacAddress] = XmpField(XmpMacAddress)  # 6 hex bytes, MAC address of peer port
        manufacturer_id: XmpField[XmpHex3] = XmpField(XmpHex3)  # 3 hex bytes, peer manufacturer ID
        profile_id: XmpField[XmpHex6] = XmpField(XmpHex6)  # 6 hex bytes, PTP profile ID
        info_string: XmpField[XmpStr] = XmpField(XmpStr)  # UTF-8 string containing three subvalues separated by ‘;!;’ for readability

    def get(self) -> "Token[GetDataAttr]":
        """Get information about a peer node.

        :return: information about a peer node.
        :rtype: XP_TSNPEERINFO.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNPACKETCOUNT:
    """
    RX and TX counter pairs for PTP message types.
    """

    code: typing.ClassVar[int] = 4021
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        rx_sync: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received Sync packets
        rx_delay_req: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received Delay_Req packets
        rx_pdelay_req: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received PDelay_Req packets
        rx_pdelay_resp: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received PDelay_Resp packets
        rx_follow_up: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received Follow_Up packets
        rx_delay_resp: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received Delay_Resp packets
        rx_pdelay_resp_follow_up: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received Pdelay_Resp_Follow_Up  packets
        rx_announce: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received Announce packets
        rx_signaling: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received Signaling packets
        rx_management: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of received Management packets

        tx_sync: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted Sync packets
        tx_delay_req: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted Delay_Req packets
        tx_pdelay_req: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted PDelay_Req packets
        tx_pdelay_resp: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted PDelay_Resp packets
        tx_follow_up: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted Follow_Up packets
        tx_delay_resp: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted Delay_Resp packets
        tx_pdelay_resp_follow_up: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted Pdelay_Resp_Follow_Up  packets
        tx_announce: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted Announce packets
        tx_signaling: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted Signaling packets
        tx_management: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, number of transmitted Management packets

    def get(self) -> "Token[GetDataAttr]":
        """Get RX and TX counter pairs for PTP message types.

        :return: RX and TX counter pairs for PTP message types.
        :rtype: XP_TSNPACKETCOUNT.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNOFFSET:
    """
    Slave port offset to Grand Master port, pre-servo and post-servo. Slave port only.
    """

    code: typing.ClassVar[int] = 4022
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        ts_1s_s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Timestamp of oldest value used for 1-sec data, seconds
        ts_1s_ns: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Timestamp of oldest value used for 1-data data, ns
        pre_min: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Pre-servo minimum since last clear, ns
        pre_max: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Pre-servo maximum since last clear, ns
        pre_ave: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Pre-servo average since last clear, ns
        pre_min_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Pre-servo minimum over the last second, ns
        pre_max_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Pre-servo maximum over the last second, ns
        pre_ave_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Pre-servo average over the last second, ns
        post_min: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Post-servo minimum since last clear, ns
        post_max: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Post-servo maximum since last clear, ns
        post_ave: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Post-servo average since last clear, ns
        post_min_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Post-servo minimum over the last second, ns
        post_max_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Post-servo maximum over the last second, ns
        post_ave_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Post-servo average over the last second, ns

    def get(self) -> "Token[GetDataAttr]":
        """Get Slave port offset to Grand Master port.

        :return: Slave port offset to Grand Master port
        :rtype: XP_TSNOFFSET.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNRXSYNCRATE:
    """
    RX SYNC rate. Slave port only.
    """

    code: typing.ClassVar[int] = 4024
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        ts_1s_s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Timestamp of oldest value used for 1-sec data, seconds
        ts_1s_ns: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Timestamp of oldest value used for 1-data data, ns

        rate_min: XmpField[XmpInt] = XmpField(XmpInt)  # integer, RX packet rate minimum since last clear, pps
        rate_max: XmpField[XmpInt] = XmpField(XmpInt)  # integer, RX packet rate maximum since last clear, pps
        rate_average: XmpField[XmpInt] = XmpField(XmpInt)  # integer, RX packet rate average since last clear, pps

        arr_min: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, RX interarrival time minimum since last clear, ns
        arr_max: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, RX interarrival time maximum since last clear, ns
        arr_average: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, RX interarrival time average since last clear, ns

        arr_min_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, RX interarrival time minimum over the last second, ns
        arr_max_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, RX interarrival time maximum over the last second, ns
        arr_average_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, RX interarrival time average over the last second, ns

    def get(self) -> "Token[GetDataAttr]":
        """Get RX SYNC rate.

        :return: RX SYNC rate
        :rtype: XP_TSNRXSYNCRATE.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNTXSYNCRATE:
    """
    TX SYNC rate. Grandmaster port only.
    """

    code: typing.ClassVar[int] = 4025
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        rate_min: XmpField[XmpInt] = XmpField(XmpInt)  # integer, TX packet rate minimum since last clear, pps
        rate_max: XmpField[XmpInt] = XmpField(XmpInt)  # integer, TX packet rate maximum since last clear, pps
        rate_average: XmpField[XmpInt] = XmpField(XmpInt)  # integer, TX packet rate average since last clear, pps

    def get(self) -> "Token[GetDataAttr]":
        """Get TX SYNC rate.

        :return: TX SYNC rate
        :rtype: XP_TSNTXSYNCRATE.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNPDELAY:
    """
    PDelay, port-to-port link delay.
    """

    code: typing.ClassVar[int] = 4026
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        ts_1s_s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Timestamp of oldest value used for 1-sec data, seconds
        ts_1s_ns: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Timestamp of oldest value used for 1-data data, ns

        min: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Minimum PDelay value since last clear, ns
        max: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Maximum PDelay value since last clear, ns
        average: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Average PDelay value since last clear, ns

        min_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Minimum PDelay value over the last second, ns
        max_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Maximum PDelay value over the last second, ns
        average_1s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Average PDelay value over the last second, ns

    def get(self) -> "Token[GetDataAttr]":
        """Get PDelay, port-to-port link delay.

        :return: PDelay, port-to-port link delay.
        :rtype: XP_TSNPDELAY.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNNRR:
    """
    Neighbor Rate Ration (NRR).
    
    An NRR value is an integer scaling of the unsigned floating-point Neighbor Rate Ratio: ``nrr_float * 1,000,000,000``.
    
    For example, NRR = 0.999876543 is represented as 999876543. Slave port only.
    """

    code: typing.ClassVar[int] = 4027
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        ts_1s_s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Timestamp of oldest value used for 1-sec data, seconds
        ts_1s_ns: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Timestamp of oldest value used for 1-data data, ns

        min: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Minimum NRR value since last clear
        max: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Maximum NRR value since last clear
        average: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Average NRR value since last clear

        min_1s: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Minimum NRR value over the last second
        max_1s: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Maximum NRR value over the last second
        average_1s: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Average NRR value over the last second

    def get(self) -> "Token[GetDataAttr]":
        """Get Neighbor Rate Ration (NRR)

        :return: Neighbor Rate Ration (NRR)
        :rtype: XP_TSNNRR.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNCLEAR:
    """
    Clear some or all TSN statistics. It is allowed to clear statistics that do not
    match the port role. This is a no-op.
    """

    code: typing.ClassVar[int] = 4028
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class SetDataAttr:
        stats_to_clear: XmpField[XmpByte] = XmpField(XmpByte, choices=TSNStatisticsTypes)  # coded byte, statistics to clear

    def set(self, stats_to_clear: TSNStatisticsTypes) -> "Token":
        """Clear some or all TSN statistics.

        :param stats_to_clear: statistics to clear
        :type stats_to_clear: TSNStatisticsTypes
        """
        return Token(self._connection, build_set_request(self, module=self._module, port=self._port, stats_to_clear=stats_to_clear))

    set_all = functools.partialmethod(set, TSNStatisticsTypes.ALL)
    """Clear all TSN statistics."""
    set_packetcount = functools.partialmethod(set, TSNStatisticsTypes.PACKETCOUNT)
    """Clear only packet count statistics."""
    set_offset = functools.partialmethod(set, TSNStatisticsTypes.OFFSET)
    """Clear only offset statistics."""
    set_pdelay = functools.partialmethod(set, TSNStatisticsTypes.PDELAY)
    """Clear only pdelay statistics."""
    set_syncrate = functools.partialmethod(set, TSNStatisticsTypes.SYNCRATE)
    """Clear only sync rate statistics."""


@register_command
@dataclass
class XP_TSNSYNCEVENTS:
    """
    A sequence of sync records with three values, each record containing:
    
    * ``tsx_s_s``: Timestamp of ``offsetx``, seconds
    
    * ``tsx_s_ns``: Timestamp of ``offsetx``, nanoseconds.
    
    * ``offsetx``: Offset at time given by timestamp.
    
    For a Grandmaster port, this value is always 0. From 0 to 640 records are returned in each ``get``, representing the most recent data available since last ``get``. The buffer is flushed after each ``get``.
    """

    code: typing.ClassVar[int] = 4029
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        tsx_s_s: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Timestamp of offsetx, seconds
        tsx_s_ns: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Timestamp of offsetx, ns
        offsetx: XmpField[XmpLong] = XmpField(XmpLong)  # long integer, Offset at time given by timestamp. For a Grandmaster port, this value is always 0.

    def get(self) -> "Token[GetDataAttr]":
        """Get a sequence of sync records.

        :return: a sequence of sync records
        :rtype: XP_TSNSYNCEVENTS.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNCANCEL:
    """
    Discard all changes to shadow config, i.e. set shadow = working config.
    """

    code: typing.ClassVar[int] = 4039
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class SetDataAttr:
        pass

    def set(self) -> "Token":
        """Discard all changes to shadow config.
        """
        return Token(
            self._connection,
            build_set_request(
                self,
                module=self._module,
                port=self._port,
            ),
        )


@register_command
@dataclass
class XP_TSNCLEARPEERINFO:
    """
    Clear all peer info data.
    """

    code: typing.ClassVar[int] = 4040
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class SetDataAttr:
        pass

    def set(self) -> "Token":
        """Clear all peer info data.
        """
        return Token(
            self._connection,
            build_set_request(
                self,
                module=self._module,
                port=self._port,
            ),
        )


@register_command
@dataclass
class XP_TSNCAPABILITIES:
    """
    Return a list of TSN-related capabilities for a port.
    """

    code: typing.ClassVar[int] = 4042
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class GetDataAttr:
        min_int: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Minimum deviation interval [ms], 0 if deviation is not supported
        max_int: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Maximum deviation interval [ms], 0 if deviation is not supported
        max_dev: XmpField[XmpInt] = XmpField(XmpInt)  # integer, Maximum deviation, +/-, in ppm [µs], 0 if deviation is not supported

    def get(self) -> "Token[GetDataAttr]":
        """Get a list of TSN-related capabilities for a port.

        :return: a list of TSN-related capabilities for a port
        :rtype: XP_TSNCAPABILITIES.GetDataAttr
        """
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))


@register_command
@dataclass
class XP_TSNDEBUG:
    code: typing.ClassVar[int] = 4050
    pushed: typing.ClassVar[bool] = False

    _connection: "interfaces.IConnection"
    _module: int
    _port: int

    @dataclass(frozen=True)
    class SetDataAttr:
        value: XmpField[XmpHex4] = XmpField(XmpHex4)

    @dataclass(frozen=True)
    class GetDataAttr:
        value: XmpField[XmpHex4] = XmpField(XmpHex4)

    def get(self) -> "Token[GetDataAttr]":
        return Token(self._connection, build_get_request(self, module=self._module, port=self._port))

    def set(self) -> "Token":
        return Token(
            self._connection,
            build_set_request(
                self,
                module=self._module,
                port=self._port,
            ),
        )


