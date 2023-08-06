from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Interleaving:
	"""Interleaving commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("interleaving", core, parent)

	def get_freq_agility(self) -> bool:
		"""SCPI: SCENario:CEMit:INTerleaving:FREQagility \n
		Snippet: value: bool = driver.scenario.cemit.interleaving.get_freq_agility() \n
		Enables frequency agility in interleaving. Requires R&S SMW with firmware version 5.xx.xxx and higher. To query the
		installed firmware version of the selected instrument, use the command method RsPulseSeq.Instrument.firmware. \n
			:return: freq_agility: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:CEMit:INTerleaving:FREQagility?')
		return Conversions.str_to_bool(response)

	def set_freq_agility(self, freq_agility: bool) -> None:
		"""SCPI: SCENario:CEMit:INTerleaving:FREQagility \n
		Snippet: driver.scenario.cemit.interleaving.set_freq_agility(freq_agility = False) \n
		Enables frequency agility in interleaving. Requires R&S SMW with firmware version 5.xx.xxx and higher. To query the
		installed firmware version of the selected instrument, use the command method RsPulseSeq.Instrument.firmware. \n
			:param freq_agility: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(freq_agility)
		self._core.io.write(f'SCENario:CEMit:INTerleaving:FREQagility {param}')

	def get_value(self) -> bool:
		"""SCPI: SCENario:CEMit:INTerleaving \n
		Snippet: value: bool = driver.scenario.cemit.interleaving.get_value() \n
		If enabled, multiple PDW lists are interleaved into a single output file using a priority-based dropping algorithm. Set
		the priority with the command method RsPulseSeq.Scenario.Cpdw.priority. \n
			:return: interleaving: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:CEMit:INTerleaving?')
		return Conversions.str_to_bool(response)

	def set_value(self, interleaving: bool) -> None:
		"""SCPI: SCENario:CEMit:INTerleaving \n
		Snippet: driver.scenario.cemit.interleaving.set_value(interleaving = False) \n
		If enabled, multiple PDW lists are interleaved into a single output file using a priority-based dropping algorithm. Set
		the priority with the command method RsPulseSeq.Scenario.Cpdw.priority. \n
			:param interleaving: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(interleaving)
		self._core.io.write(f'SCENario:CEMit:INTerleaving {param}')
