import numpy as np
from scipy.integrate import odeint, solve_ivp
from utils.constants import (
    EARTH_GRAVITY,
    AIR_DENSITY,
    DRAG_COEFFICIENT,
    BALLOON_RADIUS,
    WIND_SPEED,
    WIND_DIRECTION_DEG
)


class TrajectoryCalculator:
    """
    Calculates projectile trajectory with environmental factors.
    
    Uses kinematic equations with drag and wind effects.
    Solves using numerical integration for accuracy.
    """
    
    def __init__(self, target_x, target_y, target_z, launch_angle_deg, 
                 balloon_mass=0.125):
        self.target_x = target_x
        self.target_y = target_y
        self.target_z = target_z
        self.launch_angle_rad = np.radians(launch_angle_deg)
        self.balloon_mass = balloon_mass
        
        # Cross-sectional area of balloon
        self.balloon_radius = BALLOON_RADIUS
        self.cross_sectional_area = np.pi * self.balloon_radius**2
        
        # Wind parameters
        self.wind_speed = WIND_SPEED
        self.wind_direction_rad = np.radians(WIND_DIRECTION_DEG)
    
    
    def calculate_required_velocity(self):        
        cos_angle = np.cos(self.launch_angle_rad)
        sin_angle = np.sin(self.launch_angle_rad)
        
        # For projectile motion: y = x*tan(θ) - (g*x²)/(2*v²*cos²(θ))
        # Rearranging: v² = (g*x²) / (2*cos²(θ)*(x*tan(θ) - y))
        
        denominator = self.target_x * sin_angle - self.target_y * cos_angle
        
        if abs(denominator) < 1e-6:
            return None
        
        v_squared = (EARTH_GRAVITY * self.target_x**2) / (2 * cos_angle**2 * denominator)
        
        if v_squared < 0:
            return None
        
        return np.sqrt(v_squared)
    
    
    def simulate_trajectory(self, initial_velocity, force_calculator, 
                           max_time=10.0, num_points=1000):
        """
        Simulate complete trajectory with all forces using RK4 integration.
        
        Solves system of ODEs:
        d²x/dt² = -(Fd_x / m) + wind_x
        d²y/dt² = -g - (Fd_y / m)
        d²z/dt² = -(Fd_z / m) + wind_z
        
        Args:
            initial_velocity (float): Initial launch velocity (m/s)
            force_calculator (ForceCalculator): Force calculation object
            max_time (float): Maximum simulation time (s)
            num_points (int): Number of integration points
            
        Returns:
            dict: Trajectory data including position, velocity, acceleration, time
        """
        
        vx0 = initial_velocity * np.cos(self.launch_angle_rad)
        vy0 = initial_velocity * np.sin(self.launch_angle_rad)
        vz0 = 0.0
        
        x0 = np.array([0, 0, 0, vx0, vy0, vz0])
        
        t_eval = np.linspace(0, max_time, num_points)
        
        def derivatives(t, state):
            x, y, z, vx, vy, vz = state
            
            if y < 0:
                return [0, 0, 0, 0, 0, 0]
            
            velocity = np.array([vx, vy, vz])
            velocity_mag = np.linalg.norm(velocity)
            
            drag_force = force_calculator.calculate_drag_force(
                velocity_magnitude=velocity_mag,
                cross_sectional_area=self.cross_sectional_area
            )
            
            if velocity_mag > 0:
                drag_x = -drag_force * (vx / velocity_mag)
                drag_y = -drag_force * (vy / velocity_mag)
                drag_z = -drag_force * (vz / velocity_mag)
            else:
                drag_x = drag_y = drag_z = 0
            
            wind_x, wind_y, wind_z = force_calculator.calculate_wind_effects()
            
            ax = (drag_x + wind_x) / self.balloon_mass
            ay = -EARTH_GRAVITY + (drag_y + wind_y) / self.balloon_mass
            az = (drag_z + wind_z) / self.balloon_mass
            
            return [vx, vy, vz, ax, ay, az]
        
        solution = solve_ivp(
            derivatives,
            t_span=(0, max_time),
            y0=x0,
            t_eval=t_eval,
            method='RK45',
            dense_output=True,
            events=self._landing_event
        )
        
        trajectory = {
            'time': solution.t,
            'position': solution.y[:3].T,
            'velocity': solution.y[3:].T,
            'velocity_magnitude': np.linalg.norm(solution.y[3:].T, axis=1),
        }
        
        return trajectory
    
    
    @staticmethod
    def _landing_event(t, state):
        return state[1]
    
    _landing_event.terminal = True