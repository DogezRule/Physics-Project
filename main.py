import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from physics.trajectory import TrajectoryCalculator
from physics.forces import ForceCalculator
from utils.visualization import TrajectoryVisualizer
from utils.constants import WATER_BALLOON_MASS, EARTH_GRAVITY


def get_user_input():
    print("\n" + "="*60)
    print("WATER BALLOON LAUNCHER - TRAJECTORY CALCULATOR")
    print("="*60 + "\n")
    
    print("Enter target landing location (meters):")
    try:
        target_x = float(input("  Target X position (horizontal distance): "))
        target_y = float(input("  Target Y position (vertical distance): "))
        target_z = float(input("  Target Z position (lateral distance): "))
        
        spring_constant = float(input("\nSpring constant k (N/m): "))
        
        print("\nAvailable preset launch angles:")
        print("  1) 15° (low angle)")
        print("  2) 30° (medium-low)")
        print("  3) 45° (optimal range)")
        print("  4) 60° (high)")
        print("  5) 75° (very high)")
        
        angle_choice = int(input("Select angle preset (1-5): "))
        angles = {1: 15, 2: 30, 3: 45, 4: 60, 5: 75}
        launch_angle = angles.get(angle_choice, 45)
        
        return target_x, target_y, target_z, spring_constant, launch_angle
    
    except ValueError:
        print("ERROR: Please enter valid numeric values.")
        return get_user_input()


def validate_inputs(target_x, target_y, target_z, spring_constant, launch_angle):
    if target_x < 0 or target_y < -5 or target_z < 0:
        print("ERROR: Target coordinates must be non-negative (Y can be below launch)")
        return False
    
    if spring_constant <= 0:
        print("ERROR: Spring constant must be positive")
        return False
    
    if not (0 <= launch_angle <= 90):
        print("ERROR: Launch angle must be between 0° and 90°")
        return False
    
    if target_x > 100:
        print("WARNING: Target distance exceeds 100m (very long range)")
    
    return True


def main():
    target_x, target_y, target_z, spring_constant, launch_angle = get_user_input()
    
    if not validate_inputs(target_x, target_y, target_z, spring_constant, launch_angle):
        print("\nRetrying with new inputs...\n")
        return main()
    
    print("\n" + "-"*60)
    print("CALCULATING TRAJECTORY PARAMETERS...")
    print("-"*60 + "\n")
    
    traj_calc = TrajectoryCalculator(
        target_x=target_x,
        target_y=target_y,
        target_z=target_z,
        launch_angle_deg=launch_angle
    )
    
    force_calc = ForceCalculator()
    
    required_velocity = traj_calc.calculate_required_velocity()
    
    if required_velocity is None:
        print("ERROR: Target is unreachable with current angle.")
        print("Try adjusting the target location or launch angle.")
        return
    
    pullback_distance = np.sqrt(
        (WATER_BALLOON_MASS * required_velocity**2) / spring_constant
    )
    
    trajectory = traj_calc.simulate_trajectory(
        initial_velocity=required_velocity,
        force_calculator=force_calc
    )
    
    time_points = trajectory['time']
    velocities = trajectory['velocity_magnitude']
    positions = trajectory['position']
    
    kinetic_energy = 0.5 * WATER_BALLOON_MASS * velocities**2
    
    potential_energy = WATER_BALLOON_MASS * EARTH_GRAVITY * positions[:, 1]
    
    mechanical_energy = kinetic_energy + potential_energy
    
    momentum = WATER_BALLOON_MASS * velocities
    
    wind_correction = force_calc.estimate_wind_correction(
        launch_angle=launch_angle,
        velocity=required_velocity
    )
    
    print("\n" + "="*60)
    print("CALCULATION RESULTS")
    print("="*60 + "\n")
    
    print(f"Target Location: ({target_x:.2f}m, {target_y:.2f}m, {target_z:.2f}m)")
    print(f"Launch Angle: {launch_angle}°\n")
    
    print("REQUIRED PARAMETERS:")
    print(f"  Required Launch Velocity: {required_velocity:.3f} m/s")
    print(f"  Required Pullback Distance: {pullback_distance:.4f} m")
    print(f"  Spring Constant: {spring_constant:.1f} N/m\n")
    
    print("ENERGY & MOMENTUM:")
    print(f"  Initial Kinetic Energy: {kinetic_energy[0]:.3f} J")
    print(f"  Initial Potential Energy: {potential_energy[0]:.3f} J")
    print(f"  Initial Mechanical Energy: {mechanical_energy[0]:.3f} J")
    print(f"  Initial Momentum: {momentum[0]:.3f} kg·m/s")
    print(f"  Final Mechanical Energy (at impact): {mechanical_energy[-1]:.3f} J\n")
    
    print("FORCE CORRECTIONS:")
    print(f"  Wind Correction Factor: {wind_correction['angle_adjustment']:.2f}°")
    print(f"  Estimated Drag Force (initial): {wind_correction['drag_force']:.3f} N")
    print(f"  Confidence Score (1.0 = high): {wind_correction['confidence']:.2f}\n")
    
    visualizer = TrajectoryVisualizer(trajectory)
    
    visualizer.plot_trajectory_3d()
    visualizer.plot_energy_evolution(kinetic_energy, potential_energy, mechanical_energy)
    visualizer.plot_velocity_and_momentum(velocities, momentum)
    visualizer.plot_force_analysis(trajectory, force_calc)
    
    print("-"*60)
    print("Visualization plots saved to /output/ directory")
    print("-"*60 + "\n")
    
    return trajectory, {
        'required_velocity': required_velocity,
        'pullback_distance': pullback_distance,
        'launch_angle': launch_angle,
        'kinetic_energy': kinetic_energy,
        'potential_energy': potential_energy,
        'mechanical_energy': mechanical_energy,
        'momentum': momentum,
        'wind_correction': wind_correction
    }


if __name__ == "__main__":
    main()