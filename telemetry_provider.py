"""Data provider for any element hooked up."""


class TelemetryProvider:
    """Data provider to update any subscribed element."""

    registered_dashboards = []

    def __init__(self):
        self.data_queue = []
        self.ui_items = {}
        self.registered_dashboards.append(self)

    def notify(self, **telemetries):
        """Notify all registered dashboards with the telemetries received."""
        for telemetry, value in telemetries.items():
            for instance in self.registered_dashboards:
                instance.data_queue.append({telemetry: value})

    def subscribe(self, telemetry, element):
        """Add the ui element to the telemetry's list."""
        self.ui_items.setdefault(telemetry, []).append(element)

    def unsubscribe(self, telemetry, element):
        """Remove the ui element from the telemetry's list."""
        self.ui_items[telemetry].remove(element)

    def update(self):
        """Update every ui element depending on it's telemetry subscriptions."""
        for telemetry in self.data_queue:
            (telemetry_name, telemetry_value), = telemetry.items()
            for ui_item in self.ui_items.get(telemetry_name, []):
                ui_item.run(telemetry_name, telemetry_value)
        self.data_queue = []
