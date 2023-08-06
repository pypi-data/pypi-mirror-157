"""
Calculations with time series
"""

from typing import Union
from pandas import DataFrame
from seven2one import TechStack

class InventoryItemInfo:
    """
    Contains infos about an inventory
    """

    def __init__(self, inventory_name: str, inventory_item_id: str, factor: int, time_unit: str, unit: str):
        self._inventory_name = inventory_name
        self._inventory_item_id = inventory_item_id
        self._factor = factor
        self._time_unit = time_unit
        self._unit = unit

    @property
    def inventory_name(self) -> str:
        return self._inventory_name

    @property
    def inventory_item_id(self) -> str:
        return self._inventory_item_id

    @property
    def factor(self) -> int:
        return self._factor

    @property
    def time_unit(self) -> str:
        return self._time_unit

    @property
    def unit(self) -> str:
        return self._unit

    def __repr__(self) -> str:
        return f"InventoryItemInfo('{self._inventory_name}', '{self._inventory_item_id}', {self._factor}, '{self._time_unit}', '{self._unit}')"

class TimeSeries:
    """
    A time series
    """

    _FILL_VALUE = 0.0
    _EMPTY_INVENTORY_ITEM_ID = '-'
    _PRECISION = 12

    calc_types = Union[int, float, 'TimeSeries']

    def __init__(self, inventory_item_info: InventoryItemInfo, data_frame: DataFrame):
        self._assert_inventory_item(inventory_item_info, data_frame)
        self._inventory_item_info = inventory_item_info
        self._data_frame = data_frame

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
            self._ensure_compatibility(other._inventory_item_info)
            data_frame = calc_func(other._data_frame[other._inventory_item_info.inventory_item_id], fill_value=TimeSeries._FILL_VALUE)
        elif isinstance(other, int) or isinstance(other, float):
            data_frame = calc_func(other, fill_value=TimeSeries._FILL_VALUE)
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
        #copied_data_frame.index = copied_data_frame.columns.set_levels([TimeSeries._EMPTY_INVENTORY_ITEM_ID], level=0)
        copied_data_frame.index = copied_data_frame.columns.set_levels(
            copied_data_frame.index.levels[copied_data_frame.index.names.index('sys_inventoryItemId')] \
                .str.replace(self._inventory_item_info.inventory_item_id, TimeSeries._EMPTY_INVENTORY_ITEM_ID),
            level=0)
        rounded_data_frame = copied_data_frame.round(precision)
        return TimeSeries(inventory_item_info, rounded_data_frame)

    def _ensure_compatibility(self, inventory_item_info: InventoryItemInfo) -> None:
        if self._inventory_item_info.factor != inventory_item_info.factor:
            raise ValueError(f'Unequal resolution factors "{self._inventory_item_info.factor}" and "{inventory_item_info.factor}".')
        if self._inventory_item_info.time_unit != inventory_item_info.time_unit:
            raise ValueError(f'Unequal resolution time units "{self._inventory_item_info.time_unit}" and "{inventory_item_info.time_unit}".')
        if self._inventory_item_info.unit != inventory_item_info.unit:
            raise ValueError(f'Unequal units "{self._inventory_item_info.unit}" and "{inventory_item_info.unit}".')

    def _assert_inventory_item(self, inventory_item_info: InventoryItemInfo, data_frame: DataFrame) -> None:
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

    def _repr_html_(self) -> Union[str , None]:
        if hasattr(self, '_data_frame'):
            # pylint: disable=protected-access
            return repr(self._data_frame)
        return None

class Range:
    """
    A time range foe an inventory name to load time series data for.
    """

    def __init__(self, client: TechStack, inventory_name: str, from_timepoint: str, to_timepoint: str):
        self._client = client
        self._inventory_name = inventory_name
        self._from_timepoint = from_timepoint
        self._to_timepoint = to_timepoint

    def time_series(self, inventory_item_id: str) -> TimeSeries:
        inventory_item_info = self._get_inventory_item_info(self._inventory_name, inventory_item_id)
        data_frame = self._client.TimeSeries.timeSeriesData(
            self._inventory_name,
            self._from_timepoint,
            self._to_timepoint,
            fields=['sys_inventoryItemId', 'unit'],
            where=f'sys_inventoryItemId eq "{inventory_item_id}"',
            displayMode='pivot',
            includeMissing=True)
        return TimeSeries(inventory_item_info, data_frame)

    def write(self, inventory_item_id: str, time_series: TimeSeries) -> None:
        inventory_item_info = self._get_inventory_item_info(self._inventory_name, inventory_item_id)
        # pylint: disable=protected-access
        time_series._ensure_compatibility(inventory_item_info)
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

    def range(self, inventory_name: str, from_timepoint: str, to_timepoint: str) -> Range:
        return Range(self._client, inventory_name, from_timepoint, to_timepoint)
