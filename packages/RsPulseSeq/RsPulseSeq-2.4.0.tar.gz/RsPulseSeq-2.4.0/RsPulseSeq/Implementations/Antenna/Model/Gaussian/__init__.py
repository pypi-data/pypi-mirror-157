from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Gaussian:
	"""Gaussian commands group definition. 2 total commands, 1 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gaussian", core, parent)

	@property
	def hpBw(self):
		"""hpBw commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_hpBw'):
			from .HpBw import HpBw
			self._hpBw = HpBw(self._core, self._cmd_group)
		return self._hpBw

	def clone(self) -> 'Gaussian':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Gaussian(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
