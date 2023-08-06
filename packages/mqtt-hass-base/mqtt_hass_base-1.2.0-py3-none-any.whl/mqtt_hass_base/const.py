"""Const variables."""

from homeassistant.components.sensor import SensorDeviceClass

DEVICE_CLASSES = tuple([s.lower() for s in SensorDeviceClass] + [None])
