"""
Calculations with time series
"""

from dataclasses import dataclass
from pandas import DataFrame
from seven2one import TechStack
from typing import Union
from .utils import _parse_timepoint

@dataclass(frozen=True)
class InventoryItemInfo:
    """
    Contains infos about an inventory
    """

    inventory_name: str
    inventory_item_id: str
    factor: int
    time_unit: str
    unit: str

def _ensure_inventory_item_compatibility(one: InventoryItemInfo, other: InventoryItemInfo) -> None:
    if one.factor != other.factor:
        raise ValueError(f'Unequal resolution factors "{one.factor}" and "{other.factor}".')
    if one.time_unit != other.time_unit:
        raise ValueError(f'Unequal resolution time units "{one.time_unit}" and "{other.time_unit}".')
    if one.unit != other.unit:
        raise ValueError(f'Unequal units "{one.unit}" and "{other.unit}".')

def _assert_inventory_item_compatibility(inventory_item_info: InventoryItemInfo, data_frame: DataFrame) -> None:
    assert len(data_frame.columns) == 1
    assert len(data_frame.columns.names) == 2
    assert data_frame.columns.names[0] == 'sys_inventoryItemId'
    assert data_frame.columns.names[1] == 'unit'
    assert len(data_frame.columns.levels) == 2
    assert len(data_frame.columns.levels[0]) == 1
    assert len(data_frame.columns.levels[1]) == 1
    assert data_frame.columns.levels[0].name == 'sys_inventoryItemId'
    assert data_frame.columns.levels[1].name == 'unit'
    inventory_item_id = data_frame.columns.levels[0][0]
    unit = data_frame.columns.levels[1][0]
    assert inventory_item_id == inventory_item_info.inventory_item_id
    assert unit == inventory_item_info.unit

class TimeSeries:
    """
    A time series
    """

    _FILL_VALUE = 0.0
    _EMPTY_INVENTORY_ITEM_ID = '-'
    _PRECISION = 12

    calc_types = Union[int, float, 'TimeSeries']

    def __init__(self, inventory_item_info: InventoryItemInfo, data_frame: DataFrame):
        _assert_inventory_item_compatibility(inventory_item_info, data_frame)
        self._inventory_item_info = inventory_item_info
        self._data_frame = data_frame

    @property
    def inventory_item_info(self) -> InventoryItemInfo:
        return self._inventory_item_info

    def set_values(self, value: Union[int, float]) -> None:
        rounded_value = round(value, TimeSeries._PRECISION)
        self._data_frame.loc[:, :] = rounded_value

    def __add__(self, other: calc_types) -> 'TimeSeries':
        return self._calculate(self._data_frame.add, other)

    def __sub__(self, other:calc_types) -> 'TimeSeries':
        return self._calculate(self._data_frame.subtract, other)

    def __mul__(self, other:calc_types) -> 'TimeSeries':
        return self._calculate(self._data_frame.multiply, other)

    def __truediv__(self, other:calc_types) -> 'TimeSeries':
        return self._calculate(self._data_frame.truediv, other)

    def __iter__(self):
        return self._get_data_points().__iter__()

    def _get_data_points(self):
        return self._data_frame[self._inventory_item_info.inventory_item_id][self._inventory_item_info.unit]

    def round(self, precision: int) -> 'TimeSeries':
        return self._new_rounded_time_series(self._data_frame, precision)

    def _calculate(self, calc_func, other: calc_types) -> 'TimeSeries':
        if isinstance(other, TimeSeries):
            # pylint: disable=protected-access
            _ensure_inventory_item_compatibility(self._inventory_item_info, other._inventory_item_info)
            data_frame = calc_func(other._data_frame[other._inventory_item_info.inventory_item_id], fill_value=TimeSeries._FILL_VALUE)
        elif isinstance(other, int) or isinstance(other, float):
            rounded_other = round(other, TimeSeries._PRECISION)
            data_frame = calc_func(rounded_other, fill_value=TimeSeries._FILL_VALUE)
        else:
            raise ValueError(f'Unsupported type {type(other)}.')
        return self._new_rounded_time_series(data_frame, TimeSeries._PRECISION)

    def _new_rounded_time_series(self, data_frame: DataFrame, precision: int) -> 'TimeSeries':
        inventory_item_info = InventoryItemInfo(
            self._inventory_item_info.inventory_name,
            TimeSeries._EMPTY_INVENTORY_ITEM_ID,
            self._inventory_item_info.factor,
            self._inventory_item_info.time_unit,
            self._inventory_item_info.unit)
        copied_data_frame = data_frame.copy(deep=True)
        copied_data_frame.columns = copied_data_frame.columns.set_levels([TimeSeries._EMPTY_INVENTORY_ITEM_ID], level=0)
        rounded_data_frame = copied_data_frame.round(precision)
        return TimeSeries(inventory_item_info, rounded_data_frame)

    def __len__(self):
        return self._get_data_points().__len__()

    def __getitem__(self, index: int):
        return self._get_data_points().__getitem__(index)

    def __str__(self) -> str:
        return self._data_frame.__str__()

    def __repr__(self) -> str:
        if hasattr(self, '_data_frame'):
            return self._data_frame.__repr__()
        return 'no data frame'

    def _repr_html_(self) -> Union[str, None]:
        if hasattr(self, '_data_frame'):
            # pylint: disable=protected-access
            return self._data_frame._repr_html_()
        return None

class Scope:
    """
    A scope for time series data with a time range and an inventory name.
    """

    def __init__(self, client: TechStack, inventory_name: str, from_timepoint: str, to_timepoint: str):
        self._client = client
        self._inventory_name = inventory_name
        self._from_timepoint = _parse_timepoint(from_timepoint, is_begin=True)
        self._to_timepoint = _parse_timepoint(to_timepoint, is_begin=False)

    def time_series(self, inventory_item_id: str) -> TimeSeries:
        inventory_item_info = self._get_inventory_item_info(self._inventory_name, inventory_item_id)
        data_frame = self._client.TimeSeries.timeSeriesData(
            self._inventory_name,
            self._from_timepoint.strftime('%Y-%m-%d %H:%M:%S.%f'),
            self._to_timepoint.strftime('%Y-%m-%d %H:%M:%S.%f'),
            fields=['sys_inventoryItemId', 'unit'],
            where=f'sys_inventoryItemId eq "{inventory_item_id}"',
            displayMode='pivot',
            includeMissing=True)
        return TimeSeries(inventory_item_info, data_frame)

    def write(self, inventory_item_id: str, time_series: TimeSeries) -> None:
        inventory_item_info = self._get_inventory_item_info(self._inventory_name, inventory_item_id)
        _ensure_inventory_item_compatibility(time_series.inventory_item_info, inventory_item_info)
        # pylint: disable=protected-access
        data_points = time_series._get_data_points()
        self._client.TimeSeries.setTimeSeriesData(
            inventory_item_info.inventory_name,
            inventory_item_info.inventory_item_id,
            inventory_item_info.time_unit,
            inventory_item_info.factor,
            inventory_item_info.unit,
            data_points)

    def _get_inventory_item_info(self, inventory_name: str, inventory_item_id: str) -> InventoryItemInfo:
        inventory_item = self._client.items(inventory_name, where=f'sys_inventoryItemId eq "{inventory_item_id}"')
        resolution = inventory_item['resolution']
        resolution_parts = str(resolution[0]).split(' ')
        factor = int(resolution_parts[0])
        time_unit = str(resolution_parts[1])
        unit = str(inventory_item['unit'][0])
        return InventoryItemInfo(inventory_name, inventory_item_id, factor, time_unit, unit)

class CalQlator:

    def __init__(self, client: TechStack):
        self._client = client

    def scope(self, inventory_name: str, from_timepoint: str, to_timepoint: str) -> Scope:
        return Scope(self._client, inventory_name, from_timepoint, to_timepoint)
