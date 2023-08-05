from __future__ import annotations
import asyncio
import logging
from bosch_thermostat_client.const import (
    RESULT,
    URI,
    VALUE,
    INTERVAL,
    RECORDING,
    TEMP_CELSIUS,
    ENERGY_KILO_WATT_HOUR,
)
from .sensor import Sensor
from bosch_thermostat_client.exceptions import DeviceException

from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)


class RecordingSensor(Sensor):
    def __init__(self, path: str, **kwargs) -> None:
        super().__init__(path=path, **kwargs)
        self._lock = asyncio.Lock()
        self._past_data = []

        def unit_chooser():
            if any(x in path.lower() for x in ["energy", "power"]):
                return ENERGY_KILO_WATT_HOUR
            if any(x in path.lower() for x in ["temp", "outdoor"]):
                return TEMP_CELSIUS
            return None

        self._unit_of_measurement = unit_chooser()

    @property
    def kind(self) -> str:
        return RECORDING

    @property
    def unit_of_measurement(self) -> str:
        return self._unit_of_measurement

    def process_results(self, result: dict, time: datetime) -> None:
        """Convert multi-level json object to one level object."""

        def get_last_full_hour() -> time:
            return time - timedelta(hours=1)

        if result and RECORDING in result:
            last_hour = get_last_full_hour()
            # recording = result[RECORDING][last_hour.hour - 1]
            self._data[self.attr_id][RESULT][VALUE] = []
            for idx, recording in enumerate(result[RECORDING]):
                if recording["c"] == 0:
                    continue
                self._data[self.attr_id][RESULT][VALUE].append(
                    {
                        "d": last_hour.replace(
                            hour=idx + 1, minute=0, second=0, microsecond=0
                        ),
                        VALUE: round((recording["y"] / recording["c"]), 1),
                    }
                )

    async def fetch_range(self, start_time: datetime, stop_time: datetime) -> list:
        async with self._lock:
            if self._past_data:
                return self._past_data
            current_date = start_time
            while current_date < stop_time:
                uri = self.build_uri(time=current_date)
                data = await self._connector.get(uri)
                if not data:
                    continue
                if RECORDING in data:
                    for idx, recording in enumerate(data[RECORDING]):
                        if recording["y"] == 0 or recording["c"] == 0:
                            continue
                        _d = current_date.replace(
                            hour=idx, minute=0, second=0, microsecond=0
                        )
                        if start_time <= _d <= stop_time:
                            self._past_data.append(
                                {
                                    "d": _d,
                                    VALUE: round((recording["y"] / recording["c"]), 1),
                                }
                            )
                current_date += timedelta(days=1)
            return self._past_data

    @property
    def state(self) -> str | None:
        """Retrieve state of the record sensor."""
        return self._data[self.attr_id].get(RESULT, {}).get(VALUE)

    def build_uri(self, time: datetime) -> str:
        interval = (time - timedelta(hours=1)).strftime("%Y-%m-%d")
        return f"{self._data[self.attr_id][URI]}?{INTERVAL}={interval}"

    async def update(self, time: datetime = datetime.utcnow()) -> None:
        """Update info about Recording Sensor asynchronously."""
        try:
            result = await self._connector.get(self.build_uri(time))
            self.process_results(result, time)
        except DeviceException as err:
            _LOGGER.error(
                f"Can't update data for {self.name}. Trying uri: {self._data[URI]}. Error message: {err}"
            )
            self._extra_message = f"Can't update data. Error: {err}"
