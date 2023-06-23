class Sensor:
    shelly_id: int
    phase: int
    sensor_id: int
    sensor_description: str
    
    def __init__(self, shelly_id, phase, sensor_id, sensor_description):
        self.shelly_id = shelly_id
        self.phase = phase
        self.sensor_id = sensor_id
        self.sensor_description = sensor_description
        
    def __str__(self):
        return f"({self.shelly_id})({self.phase})({self.sensor_id})({self.sensor_description})".format
    
    def to_tuple(self):
        return (self.shelly_id, self.phase, self.sensor_id, self.sensor_description)