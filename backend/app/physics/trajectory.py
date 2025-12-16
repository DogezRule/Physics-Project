import numpy as np
from scipy.integrate import solve_ivp
from app.physics.constants import (
    EARTH_GRAVITY,
    BALLOON_RADIUS,
    WATER_BALLOON_MASS
)
from app.physics.forces import ForceCalculator

class TrajectoryCalculator:
    def __init__(self, mass=WATER_BALLOON_MASS, radius=BALLOON_RADIUS):
        self.mass = mass
        self.radius = radius
        self.area = np.pi * radius**2
        self.force_calc = ForceCalculator()

    def simulate(self, v0, launch_angle_deg, azimuth_deg, 
                 wind_speed=0, wind_direction_deg=0,
                 air_density=None, drag_coefficient=None,
                 max_time=20.0, dt=0.01):
        theta = np.radians(launch_angle_deg)
        phi = np.radians(azimuth_deg)
        wind_phi = np.radians(wind_direction_deg)
        
        vx0 = v0 * np.cos(theta) * np.cos(phi)
        vy0 = v0 * np.sin(theta)
        vz0 = v0 * np.cos(theta) * np.sin(phi)
        
        initial_state = [0.0, 0.0, 0.0, vx0, vy0, vz0]
        
        w_x = wind_speed * np.cos(wind_phi)
        w_z = wind_speed * np.sin(wind_phi)
        wind_vec = np.array([w_x, 0, w_z])
        
        def derivatives(t, state):
            x, y, z, vx, vy, vz = state
            
            v_vec = np.array([vx, vy, vz])
            rel_v = v_vec - wind_vec
            rel_v_mag = np.linalg.norm(rel_v)
            
            if rel_v_mag > 0:
                drag_force_mag = self.force_calc.calculate_drag_force(
                    rel_v_mag, 
                    self.area,
                    air_density=air_density,
                    drag_coefficient=drag_coefficient
                )
                drag_vec = -drag_force_mag * (rel_v / rel_v_mag)
            else:
                drag_vec = np.zeros(3)
                
            ax = drag_vec[0] / self.mass
            ay = -EARTH_GRAVITY + drag_vec[1] / self.mass
            az = drag_vec[2] / self.mass
            
            return [vx, vy, vz, ax, ay, az]

        def ground_event(t, state):
            return state[1]
        ground_event.terminal = True
        ground_event.direction = -1

        t_eval = np.arange(0, max_time, dt)

        sol = solve_ivp(
            derivatives, 
            [0, max_time], 
            initial_state, 
            events=ground_event,
            t_eval=t_eval,
            rtol=1e-6
        )
        
        return {
            "time": sol.t,
            "x": sol.y[0],
            "y": sol.y[1],
            "z": sol.y[2],
            "vx": sol.y[3],
            "vy": sol.y[4],
            "vz": sol.y[5]
        }
