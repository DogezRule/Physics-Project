import numpy as np
import sys
import os

# Add the current directory to path so we can import app
sys.path.append(os.getcwd())

from backend.app.physics.solver import Solver

def test_solver():
    solver = Solver()
    
    # Test Case:
    # Target: (0, 0, 20) -> Straight North (+Z)
    # Wind: 10 m/s from West (blowing East, +X, Direction=0)
    # Expected: Launcher should aim West (Result Azimuth > 90) to compensate.
    
    target_pos = (0, 0, 20)
    k = 100
    
    env = {
        'wind_speed': 10,
        'wind_direction': 0, # +X (East)
        'air_density': 1.225,
        'drag_coefficient': 0.47
    }
    
    print(f"Target: {target_pos}")
    print(f"Env: {env}")
    
    # Manually running the logic from find_optimal_trajectory to debug print
    
    tx, ty, tz = target_pos
    target_azimuth_deg = np.degrees(np.arctan2(tz, tx)) # Should be 90
    target_dist_xz = np.sqrt(tx**2 + tz**2)
    
    print(f"Geometric Azimuth: {target_azimuth_deg:.2f}°")
    
    angle = 45 # Fixed angle for debugging
    current_azimuth = target_azimuth_deg
    
    for i in range(10):
        print(f"\n--- Iteration {i} ---")
        print(f"Aiming Azimuth: {current_azimuth:.2f}°")
        
        v, error, idx, sim = solver._solve_velocity_for_angle(
            angle, current_azimuth, target_pos, target_dist_xz, env
        )
        
        if v is None:
            print("Failed to find velocity")
            break
            
        print(f"Found V: {v:.2f} m/s, Error: {error:.2f} m")
        
        cx = sim['x'][idx]
        cz = sim['z'][idx]
        print(f"Impact: ({cx:.2f}, {sim['y'][idx]:.2f}, {cz:.2f})")
        
        impact_azimuth = np.degrees(np.arctan2(cz, cx))
        print(f"Impact Azimuth: {impact_azimuth:.2f}°")
        
        angle_error = impact_azimuth - target_azimuth_deg
        print(f"Angle Error: {angle_error:.2f}°")
        
        correction = angle_error * 1.0
        current_azimuth -= correction
        print(f"New Azimuth: {current_azimuth:.2f}°")
        
        if error < 0.5:
            print("HIT!")
            break

if __name__ == "__main__":
    test_solver()
