import numpy as np
from app.physics.constants import (
    AIR_DENSITY,
    DRAG_COEFFICIENT,
    KINEMATIC_VISCOSITY
)

class ForceCalculator:
    
    def __init__(self, air_density=AIR_DENSITY, 
                 drag_coefficient=DRAG_COEFFICIENT):
        self.air_density = air_density
        self.drag_coefficient = drag_coefficient
    
    def calculate_drag_force(self, velocity_magnitude, cross_sectional_area, 
                             air_density=None, drag_coefficient=None):
        rho = air_density if air_density is not None else self.air_density
        cd = drag_coefficient if drag_coefficient is not None else self.drag_coefficient
        
        drag_force = 0.5 * rho * (velocity_magnitude**2) * \
                     cd * cross_sectional_area
        return drag_force
    
    def calculate_wind_force(self, wind_speed, wind_direction_rad):
        wind_x = wind_speed * np.cos(wind_direction_rad)
        wind_z = wind_speed * np.sin(wind_direction_rad)
        return np.array([wind_x, 0, wind_z])

    @staticmethod
    def get_drag_coefficient(reynolds_number):
        if reynolds_number < 1:
            return 24 / (reynolds_number + 1e-6)
        elif reynolds_number < 1000:
            return 24 / (reynolds_number + 1e-6) + 4 / np.sqrt(reynolds_number + 1e-6) + 0.4
        else:
            return 0.47
