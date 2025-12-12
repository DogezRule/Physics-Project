import numpy as np
from utils.constants import EARTH_GRAVITY, WATER_BALLOON_MASS


class EnergyCalculator:
    """
    Tracks:
    - Kinetic Energy (KE = 0.5 * m * v²)
    - Potential Energy (PE = m * g * h)
    - Mechanical Energy (ME = KE + PE)
    - Energy dissipation due to drag
    """
    
    def __init__(self, balloon_mass=WATER_BALLOON_MASS, gravity=EARTH_GRAVITY):
        self.mass = balloon_mass
        self.gravity = gravity
    
    
    def calculate_kinetic_energy(self, velocity_magnitude):
        return 0.5 * self.mass * velocity_magnitude**2
    
    
    def calculate_potential_energy(self, height):
        return self.mass * self.gravity * height
    
    
    def calculate_mechanical_energy(self, velocity_magnitude, height):
        ke = self.calculate_kinetic_energy(velocity_magnitude)
        pe = self.calculate_potential_energy(height)
        return ke + pe
    
    
    def calculate_energy_loss(self, initial_me, final_me):
        loss_joules = initial_me - final_me
        loss_percentage = (loss_joules / initial_me * 100) if initial_me > 0 else 0
        
        return {
            'loss_joules': loss_joules,
            'loss_percentage': loss_percentage,
        }
    
    
    def calculate_momentum(self, velocity_vector):
        return self.mass * velocity_vector
    
    
    def calculate_momentum_magnitude(self, velocity_magnitude):
        return self.mass * velocity_magnitude