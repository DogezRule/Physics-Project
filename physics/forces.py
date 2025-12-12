import numpy as np
from utils.constants import (
    AIR_DENSITY,
    DRAG_COEFFICIENT,
    WIND_SPEED,
    WIND_DIRECTION_DEG,
    KINEMATIC_VISCOSITY
)


class ForceCalculator:
    """
    Calculates forces acting on projectile during flight.
    
    Includes:
    - Drag force (proportional to v²)
    - Wind effects
    - Air density variations
    """
    
    def __init__(self, air_density=AIR_DENSITY, 
                 drag_coefficient=DRAG_COEFFICIENT,
                 wind_speed=WIND_SPEED,
                 wind_direction_deg=WIND_DIRECTION_DEG):
        self.air_density = air_density
        self.drag_coefficient = drag_coefficient
        self.wind_speed = wind_speed
        self.wind_direction_rad = np.radians(wind_direction_deg)
    
    
    def calculate_drag_force(self, velocity_magnitude, cross_sectional_area):
        drag_force = 0.5 * self.air_density * (velocity_magnitude**2) * \
                     self.drag_coefficient * cross_sectional_area
        return drag_force
    
    
    def calculate_wind_effects(self):
        wind_force_x = self.wind_speed * np.cos(self.wind_direction_rad) * 0.1
        wind_force_y = 0.0
        wind_force_z = self.wind_speed * np.sin(self.wind_direction_rad) * 0.1
        
        return wind_force_x, wind_force_y, wind_force_z
    
    
    def calculate_reynolds_number(self, velocity_magnitude, diameter):
        reynolds = (velocity_magnitude * diameter) / KINEMATIC_VISCOSITY
        return reynolds
    
    
    def get_drag_coefficient(self, reynolds_number):
        if reynolds_number < 1:
            return 24 / (reynolds_number + 0.001)
        elif reynolds_number < 1000:
            return 24 / (reynolds_number + 0.001) + 4 / np.sqrt(reynolds_number + 0.001) + 0.4
        else:
            return 0.47
    
    
    def estimate_wind_correction(self, launch_angle, velocity):
        """
        Higher momentum = greater wind resistance.
        Lower momentum = higher wind susceptibility.
            
        Returns:
            dict: Corrections with keys:
                - angle_adjustment: degrees to adjust launch angle
                - velocity_adjustment: m/s to adjust velocity
                - drag_force: estimated drag force at launch
                - confidence: confidence score (0-1) for hit accuracy
        """
        from utils.constants import WATER_BALLOON_MASS
        
        momentum = WATER_BALLOON_MASS * velocity
        
        balloon_area = np.pi * 0.08**2  # ~8cm radius balloon
        drag_at_launch = self.calculate_drag_force(velocity, balloon_area)
        
        wind_force = np.sqrt(self.wind_speed**2)
        
        angle_adjustment = np.degrees(np.arctan2(wind_force, momentum))
        
        velocity_adjustment = wind_force * 0.1
        
        # Confidence: higher momentum and lower wind = higher confidence
        max_reasonable_wind = 10.0
        momentum_factor = min(momentum / 10.0, 1.0)
        wind_factor = max(1.0 - (self.wind_speed / max_reasonable_wind), 0.0)
        
        confidence = momentum_factor * wind_factor
        
        return {
            'angle_adjustment': angle_adjustment,
            'velocity_adjustment': velocity_adjustment,
            'drag_force': drag_at_launch,
            'confidence': confidence,
            'momentum': momentum,
            'wind_force': wind_force
        }