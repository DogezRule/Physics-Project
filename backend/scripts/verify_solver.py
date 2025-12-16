import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.physics.solver import Solver
import numpy as np

def verify():
    solver = Solver()
    
    target = (100, 0, 50)
    target_dist = np.sqrt(target[0]**2 + target[2]**2)
    print(f"Target: {target}, Distance: {target_dist:.2f}m")
    
    env = {
        'wind_speed': 20.0,
        'wind_direction': 90.0,
        'air_density': 1.225,
        'drag_coefficient': 0.47
    }
    print(f"Environment: {env}")
    
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Target: {target}\nEnv: {env}\n")
        
        solution = solver.find_optimal_trajectory(
            target, 
            spring_constant=500, 
            env_params=env,
            angle_range=(30, 60),
            angle_step=10
        )
        
        if solution:
            f.write("\nSolution Found:\n")
            f.write(f"  Launch Angle: {solution['launch_angle']} deg\n")
            f.write(f"  Launch Azimuth: {solution['azimuth_angle']:.2f} deg\n")
            f.write(f"  Velocity: {solution['velocity']:.2f} m/s\n")
            f.write(f"  Error: {solution['error']:.4f} meters\n")
            
            traj = solution['trajectory']
            f.write(f"  Flight Time: {traj['time'][-1]:.4f} s\n")
            f.write(f"  Impact X: {traj['x'][-1]:.4f}\n")
            f.write(f"  Impact Z: {traj['z'][-1]:.4f}\n")
            
            geom_az = np.degrees(np.arctan2(target[2], target[0]))
            f.write(f"  Geometric Azimuth: {geom_az:.2f} deg\n")
            f.write(f"  Azimuth Correction: {solution['azimuth_angle'] - geom_az:.2f} deg\n")
            
            if solution['error'] < 0.5:
                print("\nSUCCESS: Target hit within tolerance.")
                f.write("SUCCESS\n")
            else:
                print("\nFAILURE: Solution found but error too high.")
                f.write("FAILURE\n")
                sys.exit(1)
                
        else:
            print("\nFAILURE: No solution found.")
            f.write("FAILURE: No solution\n")
            sys.exit(1)

if __name__ == "__main__":
    verify()
