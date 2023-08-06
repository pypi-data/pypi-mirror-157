from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Carray:
	"""Carray commands group definition. 17 total commands, 5 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("carray", core, parent)

	@property
	def circular(self):
		"""circular commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_circular'):
			from .Circular import Circular
			self._circular = Circular(self._core, self._cmd_group)
		return self._circular

	@property
	def element(self):
		"""element commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_element'):
			from .Element import Element
			self._element = Element(self._core, self._cmd_group)
		return self._element

	@property
	def hexagonal(self):
		"""hexagonal commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_hexagonal'):
			from .Hexagonal import Hexagonal
			self._hexagonal = Hexagonal(self._core, self._cmd_group)
		return self._hexagonal

	@property
	def linear(self):
		"""linear commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_linear'):
			from .Linear import Linear
			self._linear = Linear(self._core, self._cmd_group)
		return self._linear

	@property
	def rectangular(self):
		"""rectangular commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_rectangular'):
			from .Rectangular import Rectangular
			self._rectangular = Rectangular(self._core, self._cmd_group)
		return self._rectangular

	def get_cosn(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:COSN \n
		Snippet: value: float = driver.antenna.model.carray.get_cosn() \n
		Sets Cos^N of the Planar Phased Array antenna. \n
			:return: cosn: float Range: 2 to 10
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:COSN?')
		return Conversions.str_to_float(response)

	def set_cosn(self, cosn: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:COSN \n
		Snippet: driver.antenna.model.carray.set_cosn(cosn = 1.0) \n
		Sets Cos^N of the Planar Phased Array antenna. \n
			:param cosn: float Range: 2 to 10
		"""
		param = Conversions.decimal_value_to_str(cosn)
		self._core.io.write(f'ANTenna:MODel:CARRay:COSN {param}')

	# noinspection PyTypeChecker
	def get_distribution(self) -> enums.AntennaModelArray:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution \n
		Snippet: value: enums.AntennaModelArray = driver.antenna.model.carray.get_distribution() \n
		Sets the aperture distribution of the Planar Phased Array antenna. \n
			:return: distribution: UNIForm| PARabolic| COSine| CSQuared| COSN| TRIangular| HAMMing| HANN
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:DISTribution?')
		return Conversions.str_to_scalar_enum(response, enums.AntennaModelArray)

	def set_distribution(self, distribution: enums.AntennaModelArray) -> None:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution \n
		Snippet: driver.antenna.model.carray.set_distribution(distribution = enums.AntennaModelArray.COSine) \n
		Sets the aperture distribution of the Planar Phased Array antenna. \n
			:param distribution: UNIForm| PARabolic| COSine| CSQuared| COSN| TRIangular| HAMMing| HANN
		"""
		param = Conversions.enum_scalar_to_str(distribution, enums.AntennaModelArray)
		self._core.io.write(f'ANTenna:MODel:CARRay:DISTribution {param}')

	# noinspection PyTypeChecker
	def get_geometry(self) -> enums.Geometry:
		"""SCPI: ANTenna:MODel:CARRay:GEOMetry \n
		Snippet: value: enums.Geometry = driver.antenna.model.carray.get_geometry() \n
		Sets the geometry of the custom phased array antenna. \n
			:return: geometry: RECTangular| LINear| HEXagonal| CIRCular
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:GEOMetry?')
		return Conversions.str_to_scalar_enum(response, enums.Geometry)

	def set_geometry(self, geometry: enums.Geometry) -> None:
		"""SCPI: ANTenna:MODel:CARRay:GEOMetry \n
		Snippet: driver.antenna.model.carray.set_geometry(geometry = enums.Geometry.CIRCular) \n
		Sets the geometry of the custom phased array antenna. \n
			:param geometry: RECTangular| LINear| HEXagonal| CIRCular
		"""
		param = Conversions.enum_scalar_to_str(geometry, enums.Geometry)
		self._core.io.write(f'ANTenna:MODel:CARRay:GEOMetry {param}')

	def get_pedestal(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:PEDestal \n
		Snippet: value: float = driver.antenna.model.carray.get_pedestal() \n
		Sets the Pedestal of the Planar Phased Array antenna. \n
			:return: pedestal: float Range: 0 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:PEDestal?')
		return Conversions.str_to_float(response)

	def set_pedestal(self, pedestal: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:PEDestal \n
		Snippet: driver.antenna.model.carray.set_pedestal(pedestal = 1.0) \n
		Sets the Pedestal of the Planar Phased Array antenna. \n
			:param pedestal: float Range: 0 to 1
		"""
		param = Conversions.decimal_value_to_str(pedestal)
		self._core.io.write(f'ANTenna:MODel:CARRay:PEDestal {param}')

	def clone(self) -> 'Carray':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Carray(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
