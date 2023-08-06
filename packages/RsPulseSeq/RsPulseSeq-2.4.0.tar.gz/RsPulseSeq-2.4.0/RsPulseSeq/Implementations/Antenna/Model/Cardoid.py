from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Cardoid:
	"""Cardoid commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cardoid", core, parent)

	def get_exponent(self) -> float:
		"""SCPI: ANTenna:MODel:CARDoid:EXPonent \n
		Snippet: value: float = driver.antenna.model.cardoid.get_exponent() \n
		Use values greater than 1 to narrow the antenna beam. \n
			:return: exponent: float Range: 1 to 20
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARDoid:EXPonent?')
		return Conversions.str_to_float(response)

	def set_exponent(self, exponent: float) -> None:
		"""SCPI: ANTenna:MODel:CARDoid:EXPonent \n
		Snippet: driver.antenna.model.cardoid.set_exponent(exponent = 1.0) \n
		Use values greater than 1 to narrow the antenna beam. \n
			:param exponent: float Range: 1 to 20
		"""
		param = Conversions.decimal_value_to_str(exponent)
		self._core.io.write(f'ANTenna:MODel:CARDoid:EXPonent {param}')
