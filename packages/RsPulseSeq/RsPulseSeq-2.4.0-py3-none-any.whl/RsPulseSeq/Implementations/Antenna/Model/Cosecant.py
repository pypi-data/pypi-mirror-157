from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Cosecant:
	"""Cosecant commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cosecant", core, parent)

	def get_hp_bw(self) -> float:
		"""SCPI: ANTenna:MODel:COSecant:HPBW \n
		Snippet: value: float = driver.antenna.model.cosecant.get_hp_bw() \n
		Sets the Half-Power Beam Width Cosecant Squared antenna. \n
			:return: hp_bw: float Range: 0.01 to 30
		"""
		response = self._core.io.query_str('ANTenna:MODel:COSecant:HPBW?')
		return Conversions.str_to_float(response)

	def set_hp_bw(self, hp_bw: float) -> None:
		"""SCPI: ANTenna:MODel:COSecant:HPBW \n
		Snippet: driver.antenna.model.cosecant.set_hp_bw(hp_bw = 1.0) \n
		Sets the Half-Power Beam Width Cosecant Squared antenna. \n
			:param hp_bw: float Range: 0.01 to 30
		"""
		param = Conversions.decimal_value_to_str(hp_bw)
		self._core.io.write(f'ANTenna:MODel:COSecant:HPBW {param}')

	def get_t_1(self) -> float:
		"""SCPI: ANTenna:MODel:COSecant:T1 \n
		Snippet: value: float = driver.antenna.model.cosecant.get_t_1() \n
		Sets the Theta parameters. \n
			:return: t_1: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:COSecant:T1?')
		return Conversions.str_to_float(response)

	def set_t_1(self, t_1: float) -> None:
		"""SCPI: ANTenna:MODel:COSecant:T1 \n
		Snippet: driver.antenna.model.cosecant.set_t_1(t_1 = 1.0) \n
		Sets the Theta parameters. \n
			:param t_1: float Range: 1 to 90
		"""
		param = Conversions.decimal_value_to_str(t_1)
		self._core.io.write(f'ANTenna:MODel:COSecant:T1 {param}')

	def get_t_2(self) -> float:
		"""SCPI: ANTenna:MODel:COSecant:T2 \n
		Snippet: value: float = driver.antenna.model.cosecant.get_t_2() \n
		Sets the Theta parameters. \n
			:return: t_2: float Range: 1 to 90
		"""
		response = self._core.io.query_str('ANTenna:MODel:COSecant:T2?')
		return Conversions.str_to_float(response)

	def set_t_2(self, t_2: float) -> None:
		"""SCPI: ANTenna:MODel:COSecant:T2 \n
		Snippet: driver.antenna.model.cosecant.set_t_2(t_2 = 1.0) \n
		Sets the Theta parameters. \n
			:param t_2: float Range: 1 to 90
		"""
		param = Conversions.decimal_value_to_str(t_2)
		self._core.io.write(f'ANTenna:MODel:COSecant:T2 {param}')
