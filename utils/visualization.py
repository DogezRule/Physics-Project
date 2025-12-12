import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
from pathlib import Path


class TrajectoryVisualizer:
    """    
    Generates:
    - 3D trajectory plot
    - Energy evolution over time
    - Velocity and momentum profiles
    - Force analysis
    """
    
    def __init__(self, trajectory_data):
        self.trajectory = trajectory_data
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        plt.style.use('seaborn-v0_8-darkgrid')
    
    
    def plot_trajectory_3d(self):
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        pos = self.trajectory['position']
        
        ax.plot(pos[:, 0], pos[:, 1], pos[:, 2], 
               'b-', linewidth=2, label='Trajectory')
        
        ax.scatter([0], [0], [0], color='green', s=100, label='Launch', marker='^')
        
        ax.scatter([pos[-1, 0]], [pos[-1, 1]], [pos[-1, 2]], 
                  color='red', s=100, label='Landing', marker='v')
        
        ax.set_xlabel('Distance X (m)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Height Y (m)', fontsize=11, fontweight='bold')
        ax.set_zlabel('Lateral Z (m)', fontsize=11, fontweight='bold')
        ax.set_title('Water Balloon Trajectory (3D)', fontsize=13, fontweight='bold')
        
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '01_trajectory_3d.png', dpi=300, bbox_inches='tight')
        print("Saved: 01_trajectory_3d.png")
        plt.close()
    
    
    def plot_energy_evolution(self, ke, pe, me):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        time = self.trajectory['time']
        pos = self.trajectory['position']
        
        ax = axes[0, 0]
        ax.plot(time, ke, 'r-', linewidth=2.5, label='Kinetic Energy')
        ax.plot(time, pe, 'b-', linewidth=2.5, label='Potential Energy')
        ax.plot(time, me, 'g-', linewidth=2.5, label='Mechanical Energy')
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Energy (J)', fontweight='bold')
        ax.set_title('Energy Evolution Over Time', fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        ax = axes[0, 1]
        ax.fill_between(time, pos[:, 1], alpha=0.3, color='cyan')
        ax.plot(time, pos[:, 1], 'b-', linewidth=2.5)
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Height (m)', fontweight='bold')
        ax.set_title('Height vs Time', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        ax = axes[1, 0]
        ax.fill_between(time, 0, ke, alpha=0.6, color='red', label='Kinetic Energy')
        ax.fill_between(time, ke, ke + pe, alpha=0.6, color='blue', label='Potential Energy')
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Energy (J)', fontweight='bold')
        ax.set_title('Energy Composition (Stacked)', fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        ax = axes[1, 1]
        energy_loss = me[0] - me
        ax.fill_between(time, energy_loss, alpha=0.4, color='orange')
        ax.plot(time, energy_loss, 'orange', linewidth=2.5, label='Energy Loss')
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Cumulative Energy Loss (J)', fontweight='bold')
        ax.set_title('Energy Dissipation (Drag & Air Resistance)', fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '02_energy_analysis.png', dpi=300, bbox_inches='tight')
        print("Saved: 02_energy_analysis.png")
        plt.close()
    
    
    def plot_velocity_and_momentum(self, velocity_mag, momentum_mag):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        time = self.trajectory['time']
        vel = self.trajectory['velocity']
        
        # Plot 1: Velocity magnitude
        ax = axes[0, 0]
        ax.plot(time, velocity_mag, 'purple', linewidth=2.5)
        ax.fill_between(time, velocity_mag, alpha=0.3, color='purple')
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Velocity Magnitude (m/s)', fontweight='bold')
        ax.set_title('Speed Profile', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Momentum magnitude
        ax = axes[0, 1]
        ax.plot(time, momentum_mag, 'darkgreen', linewidth=2.5)
        ax.fill_between(time, momentum_mag, alpha=0.3, color='darkgreen')
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Momentum Magnitude (kg·m/s)', fontweight='bold')
        ax.set_title('Momentum Profile (Wind Resistance)', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Velocity components
        ax = axes[1, 0]
        ax.plot(time, vel[:, 0], 'r-', linewidth=2, label='Vx (Forward)')
        ax.plot(time, vel[:, 1], 'b-', linewidth=2, label='Vy (Vertical)')
        ax.plot(time, vel[:, 2], 'g-', linewidth=2, label='Vz (Lateral)')
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Velocity Component (m/s)', fontweight='bold')
        ax.set_title('Velocity Components Over Time', fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Phase space (velocity vs position)
        ax = axes[1, 1]
        distance = self.trajectory['position'][:, 0]
        ax.plot(distance, velocity_mag, 'darkblue', linewidth=2.5)
        ax.scatter(distance[0], velocity_mag[0], color='green', s=80, 
                  marker='o', label='Launch', zorder=5)
        ax.scatter(distance[-1], velocity_mag[-1], color='red', s=80, 
                  marker='s', label='Landing', zorder=5)
        ax.set_xlabel('Horizontal Distance (m)', fontweight='bold')
        ax.set_ylabel('Velocity Magnitude (m/s)', fontweight='bold')
        ax.set_title('Velocity vs Distance (Phase Space)', fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '03_velocity_momentum.png', 
                   dpi=300, bbox_inches='tight')
        print("Saved: 03_velocity_momentum.png")
        plt.close()
    
    
    def plot_force_analysis(self, trajectory, force_calculator):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        time = trajectory['time']
        vel = trajectory['velocity']
        velocity_mag = trajectory['velocity_magnitude']
        pos = trajectory['position']
        
        balloon_area = np.pi * 0.08**2
        drag_forces = np.array([
            force_calculator.calculate_drag_force(v, balloon_area) 
            for v in velocity_mag
        ])
        
        # Plot 1: Drag force over time
        ax = axes[0, 0]
        ax.plot(time, drag_forces, 'darkred', linewidth=2.5)
        ax.fill_between(time, drag_forces, alpha=0.3, color='red')
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Drag Force (N)', fontweight='bold')
        ax.set_title('Air Resistance (Drag Force) Profile', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Drag force vs velocity
        ax = axes[0, 1]
        ax.scatter(velocity_mag, drag_forces, alpha=0.6, s=30, color='darkred')
        ax.set_xlabel('Velocity (m/s)', fontweight='bold')
        ax.set_ylabel('Drag Force (N)', fontweight='bold')
        ax.set_title('Drag Force vs Velocity (F ∝ v²)', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Acceleration magnitude
        ax = axes[1, 0]
        acceleration_mag = np.linalg.norm(np.gradient(vel, axis=0), axis=1)
        ax.plot(time, acceleration_mag, 'darkorange', linewidth=2.5)
        ax.fill_between(time, acceleration_mag, alpha=0.3, color='orange')
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Acceleration Magnitude (m/s²)', fontweight='bold')
        ax.set_title('Total Acceleration (All Forces)', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Wind effect visualization
        ax = axes[1, 1]
        wind_x = np.ones_like(time) * force_calculator.wind_speed * \
                 np.cos(force_calculator.wind_direction_rad)
        ax.arrow(0.1, 0.9, wind_x[0]/20, 0, head_width=0.05, head_length=0.05,
                fc='darkblue', ec='darkblue', transform=ax.transAxes)
        ax.text(0.2, 0.95, f'Wind: {force_calculator.wind_speed:.1f} m/s',
               fontsize=11, fontweight='bold', transform=ax.transAxes)
        
        ax.plot(pos[:, 0], pos[:, 2], 'b-', linewidth=2.5, label='Actual (with wind)')
        ax.set_xlabel('Distance X (m)', fontweight='bold')
        ax.set_ylabel('Lateral Z (m)', fontweight='bold')
        ax.set_title('Wind Effect on Trajectory (Top View)', fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '04_force_analysis.png', dpi=300, bbox_inches='tight')
        print("Saved: 04_force_analysis.png")
        plt.close()