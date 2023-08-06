from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Array:
	"""Array commands group definition. 8 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("array", core, parent)

	@property
	def element(self):
		"""element commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_element'):
			from .Element import Element
			self._element = Element(self._core, self._cmd_group)
		return self._element

	def get_cosn(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:COSN \n
		Snippet: value: float = driver.antenna.model.array.get_cosn() \n
		Sets Cos^N of the Planar Phased Array antenna. \n
			:return: cosn: float Range: 2 to 10
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:COSN?')
		return Conversions.str_to_float(response)

	def set_cosn(self, cosn: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:COSN \n
		Snippet: driver.antenna.model.array.set_cosn(cosn = 1.0) \n
		Sets Cos^N of the Planar Phased Array antenna. \n
			:param cosn: float Range: 2 to 10
		"""
		param = Conversions.decimal_value_to_str(cosn)
		self._core.io.write(f'ANTenna:MODel:ARRay:COSN {param}')

	# noinspection PyTypeChecker
	def get_distribution(self) -> enums.AntennaModelArray:
		"""SCPI: ANTenna:MODel:ARRay:DISTribution \n
		Snippet: value: enums.AntennaModelArray = driver.antenna.model.array.get_distribution() \n
		Sets the aperture distribution of the Planar Phased Array antenna. \n
			:return: distribution: UNIForm| PARabolic| COSine| CSQuared| COSN| TRIangular| HAMMing| HANN
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:DISTribution?')
		return Conversions.str_to_scalar_enum(response, enums.AntennaModelArray)

	def set_distribution(self, distribution: enums.AntennaModelArray) -> None:
		"""SCPI: ANTenna:MODel:ARRay:DISTribution \n
		Snippet: driver.antenna.model.array.set_distribution(distribution = enums.AntennaModelArray.COSine) \n
		Sets the aperture distribution of the Planar Phased Array antenna. \n
			:param distribution: UNIForm| PARabolic| COSine| CSQuared| COSN| TRIangular| HAMMing| HANN
		"""
		param = Conversions.enum_scalar_to_str(distribution, enums.AntennaModelArray)
		self._core.io.write(f'ANTenna:MODel:ARRay:DISTribution {param}')

	def get_nx(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:NX \n
		Snippet: value: float = driver.antenna.model.array.get_nx() \n
		Sets the number of elements of the antenna array. \n
			:return: nx: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:NX?')
		return Conversions.str_to_float(response)

	def set_nx(self, nx: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:NX \n
		Snippet: driver.antenna.model.array.set_nx(nx = 1.0) \n
		Sets the number of elements of the antenna array. \n
			:param nx: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		param = Conversions.decimal_value_to_str(nx)
		self._core.io.write(f'ANTenna:MODel:ARRay:NX {param}')

	def get_nz(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:NZ \n
		Snippet: value: float = driver.antenna.model.array.get_nz() \n
		Sets the number of elements of the antenna array. \n
			:return: nz: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:NZ?')
		return Conversions.str_to_float(response)

	def set_nz(self, nz: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:NZ \n
		Snippet: driver.antenna.model.array.set_nz(nz = 1.0) \n
		Sets the number of elements of the antenna array. \n
			:param nz: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		param = Conversions.decimal_value_to_str(nz)
		self._core.io.write(f'ANTenna:MODel:ARRay:NZ {param}')

	def get_pedestal(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:PEDestal \n
		Snippet: value: float = driver.antenna.model.array.get_pedestal() \n
		Sets the Pedestal of the Planar Phased Array antenna. \n
			:return: pedestal: float Range: 0 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:PEDestal?')
		return Conversions.str_to_float(response)

	def set_pedestal(self, pedestal: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:PEDestal \n
		Snippet: driver.antenna.model.array.set_pedestal(pedestal = 1.0) \n
		Sets the Pedestal of the Planar Phased Array antenna. \n
			:param pedestal: float Range: 0 to 1
		"""
		param = Conversions.decimal_value_to_str(pedestal)
		self._core.io.write(f'ANTenna:MODel:ARRay:PEDestal {param}')

	def get_xdistance(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:XDIStance \n
		Snippet: value: float = driver.antenna.model.array.get_xdistance() \n
		Sets the spacing between the elements of the array antenna. \n
			:return: xdistance: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:XDIStance?')
		return Conversions.str_to_float(response)

	def set_xdistance(self, xdistance: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:XDIStance \n
		Snippet: driver.antenna.model.array.set_xdistance(xdistance = 1.0) \n
		Sets the spacing between the elements of the array antenna. \n
			:param xdistance: float Range: 0.0001 to 1
		"""
		param = Conversions.decimal_value_to_str(xdistance)
		self._core.io.write(f'ANTenna:MODel:ARRay:XDIStance {param}')

	def get_zdistance(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:ZDIStance \n
		Snippet: value: float = driver.antenna.model.array.get_zdistance() \n
		Sets the spacing between the elements of the array antenna. \n
			:return: zdistance: float Range: 0.0001 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:ZDIStance?')
		return Conversions.str_to_float(response)

	def set_zdistance(self, zdistance: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:ZDIStance \n
		Snippet: driver.antenna.model.array.set_zdistance(zdistance = 1.0) \n
		Sets the spacing between the elements of the array antenna. \n
			:param zdistance: float Range: 0.0001 to 1
		"""
		param = Conversions.decimal_value_to_str(zdistance)
		self._core.io.write(f'ANTenna:MODel:ARRay:ZDIStance {param}')

	def clone(self) -> 'Array':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Array(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
