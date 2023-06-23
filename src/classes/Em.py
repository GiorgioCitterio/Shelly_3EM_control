import datetime
# TODO: mettere duration_in_milliseconds ecc...
class Em:
    shelly_id: int
    phase: int
    sensor_id: int
    sensor_value: float
    measurement_date: datetime
    duration: int
    def __init__(self, shelly_id, phase, sensor_id, sensor_value, measurement_date, duration):
        self.shelly_id = shelly_id
        self.phase = phase
        self.sensor_id = sensor_id
        self.sensor_value = sensor_value
        self.measurement_date = measurement_date
        self.duration = duration
        
    def __str__(self):
        return f"({self.shelly_id})({self.phase})({self.sensor_id})({self.sensor_value})({self.measurement_date})({self.duration})"
    
    def to_tuple(self):
        return (self.shelly_id, self.phase, self.sensor_id, self.sensor_value, self.measurement_date, self.duration)