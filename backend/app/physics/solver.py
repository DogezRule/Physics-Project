import numpy as np
from scipy.optimize import least_squares
from app.physics.trajectory import TrajectoryCalculator
from app.physics.constants import WATER_BALLOON_MASS

class Solver:
    def __init__(self):
        self.traj_calc = TrajectoryCalculator()
        
    def find_optimal_trajectory(self, target_pos, spring_constant, 
                                env_params=None,
                                angle_range=(15, 75), angle_step=5):
        env = env_params or {}
        tx, ty, tz = target_pos
        
        best_solution = None
        min_velocity = float('inf')
        
        global_min_error = float('inf')
        global_best_solution = None
        
        for angle in range(angle_range[0], angle_range[1] + 1, angle_step):
            
            result = self._solve_params_for_angle_robust(
                angle, target_pos, env_params=env
            )
            
            if result:
                v0, az, solution_error, sim = result
                
                pullback = v0 * np.sqrt(WATER_BALLOON_MASS / spring_constant)
                
                current_solution = {
                    "launch_angle": angle,
                    "azimuth_angle": az,
                    "velocity": v0,
                    "pullback": pullback,
                    "trajectory": sim,
                    "error": solution_error
                }

                if solution_error < global_min_error:
                    global_min_error = solution_error
                    global_best_solution = current_solution
                
                if solution_error < 0.5:
                    if v0 < min_velocity:
                        min_velocity = v0
                        best_solution = current_solution
        
        if best_solution:
            return best_solution
            
        if global_best_solution:
            print(f"Warning: Could not hit target perfectly. Best error: {global_min_error:.2f}m")
        return global_best_solution

    def _solve_params_for_angle_robust(self, angle, target_pos, env_params=None):
        tx, ty, tz = target_pos
        env = env_params or {}
        
        wind_speed = env.get('wind_speed', 0)
        wind_dir = env.get('wind_direction', 0)
        air_density = env.get('air_density')
        drag_coeff = env.get('drag_coefficient')

        geom_azimuth = np.degrees(np.arctan2(tz, tx))
        
        dist = np.sqrt(tx**2 + tz**2)
        g = 9.81
        rad_angle = np.radians(angle)
        
        try:
            denom = np.sin(2 * rad_angle)
            if abs(denom) < 1e-4: denom = 1e-4
            v_guess = np.sqrt(dist * g / denom)
        except:
            v_guess = 50.0 
            
        if np.isnan(v_guess) or v_guess > 300: v_guess = 50.0
        
        x0 = [v_guess * 1.1, geom_azimuth]
        
        bounds = (
            [1.0, geom_azimuth - 120], 
            [300.0, geom_azimuth + 120]
        )

        def residuals(params):
            v_curr, az_curr = params
            
            sim = self.traj_calc.simulate(
                v0=v_curr,
                launch_angle_deg=angle,
                azimuth_deg=az_curr,
                wind_speed=wind_speed,
                wind_direction_deg=wind_dir,
                air_density=air_density,
                drag_coefficient=drag_coeff,
                dt=0.01,
                max_time=20.0
            )
            
            final_x = sim['x'][-1]
            final_z = sim['z'][-1]
            
            res_x = final_x - tx
            res_z = final_z - tz
            
            return [res_x, res_z]

        try:
            res = least_squares(
                residuals, 
                x0, 
                bounds=bounds, 
                ftol=1e-6,
                xtol=1e-6,
                loss='linear',
                max_nfev=100 
            )
        except Exception as e:
            return None
            
        best_v, best_az = res.x
        
        final_sim = self.traj_calc.simulate(
            v0=best_v,
            launch_angle_deg=angle,
            azimuth_deg=best_az,
            wind_speed=wind_speed,
            wind_direction_deg=wind_dir,
            air_density=air_density,
            drag_coefficient=drag_coeff,
            dt=0.01
        )
        
        final_x = final_sim['x'][-1]
        final_z = final_sim['z'][-1]
        dist_err = np.sqrt((final_x - tx)**2 + (final_z - tz)**2)
        
        if dist_err > 100.0:
            return None
            
        return best_v, best_az, dist_err, final_sim
