#!/usr/bin/env python3
"""
Water Balloon Launcher (Interactive)

Features requested:
- Asks the user for input (target and spring constant) when no CLI args given.
- Randomly generates wind, drag (Cd), and weight (mass) to emulate real-life variability.
- Optional: open a simple clickable map in Python (matplotlib) to choose the target on x–z plane.
- Full physics (gravity, air drag, wind), predicted (vacuum) vs actual landing, and diagnostic plots.

Examples:
    python water_balloon_launcher_interactive.py            # prompts for input and randomizes physics
    python water_balloon_launcher_interactive.py --click_map --k 300  # choose target by clicking a map
    python water_balloon_launcher_interactive.py --target 25 0 0 --k 250 --no_plot

Note: This script uses normal distributions to perturb mass, diameter, Cd, and wind.
      Bounds are applied to keep values physically reasonable.
"""

import math
import argparse
from dataclasses import dataclass, field
from typing import Tuple, List, Optional

import numpy as np
import matplotlib.pyplot as plt


@dataclass
class Env:
    g: float = 9.81            # gravitational acceleration (m/s^2)
    rho: float = 1.225         # air density (kg/m^3)
    wind: np.ndarray = field(default_factory=lambda: np.zeros(3))  # wind velocity vector (m/s)


@dataclass
class Projectile:
    m: float                   # mass (kg)
    cd: float                  # drag coefficient (sphere ~0.47)
    area: float                # cross-sectional area (m^2)


@dataclass
class Launcher:
    k: float                   # spring constant (N/m)
    eta: float = 0.85          # efficiency factor (0..1)
    s_max: float = 0.5         # max pullback (m)


@dataclass
class SimulationResult:
    t: np.ndarray
    pos: np.ndarray
    vel: np.ndarray
    ke: np.ndarray
    pe: np.ndarray
    me: np.ndarray
    p_mag: np.ndarray
    landing_point: np.ndarray
    max_height: float
    v0: float
    angle_deg: float
    yaw_deg: float
    pullback: float


def energy_to_speed(k: float, eta: float, s: float, m: float) -> float:
    return math.sqrt((eta * k * s * s) / m)


def speed_to_pullback(v0: float, k: float, eta: float, m: float) -> float:
    return math.sqrt((m * v0 * v0) / (eta * k))


def ideal_vacuum_angle_and_speed(R: float, dy: float, g: float, angle_min_deg: float = 5.0, angle_max_deg: float = 85.0) -> Tuple[float, float]:
    best_v02 = None
    best_angle = None
    for angle_deg in np.linspace(angle_min_deg, angle_max_deg, 161):
        th = math.radians(angle_deg)
        c = math.cos(th)
        denom = 2 * (c ** 2) * (R * math.tan(th) - dy)
        if denom <= 0:
            continue
        v02 = (g * R * R) / denom
        if v02 <= 0:
            continue
        if (best_v02 is None) or (v02 < best_v02):
            best_v02 = v02
            best_angle = angle_deg
    if best_v02 is None:
        best_angle = 45.0
        th = math.radians(best_angle)
        c = math.cos(th)
        denom = 2 * (c ** 2) * (R * math.tan(th) - dy if R * math.tan(th) - dy > 1e-6 else 1e-6)
        best_v02 = (g * R * R) / denom
    return best_angle, math.sqrt(best_v02)


def simulate(k: float, eta: float, s: float, angle_deg: float, yaw_deg: float,
             launch_pos: np.ndarray, proj: Projectile, env: Env,
             t_step: float = 0.002, t_max: float = 30.0, ground_y: float = 0.0) -> SimulationResult:
    v0 = energy_to_speed(k, eta, s, proj.m)
    th = math.radians(angle_deg)
    yaw = math.radians(yaw_deg)

    dir_h = np.array([math.cos(yaw), 0.0, math.sin(yaw)])
    v0_vec = v0 * (dir_h * math.cos(th) + np.array([0.0, math.sin(th), 0.0]))

    def accel(v: np.ndarray) -> np.ndarray:
        v_rel = v - env.wind
        speed_rel = np.linalg.norm(v_rel)
        if speed_rel < 1e-12:
            drag = np.zeros(3)
        else:
            drag_mag = 0.5 * env.rho * proj.cd * proj.area * speed_rel * speed_rel
            drag = -drag_mag * (v_rel / speed_rel)
        a = np.array([0.0, -env.g, 0.0]) + drag / proj.m
        return a

    t_list: List[float] = [0.0]
    pos_list: List[np.ndarray] = [launch_pos.copy()]
    vel_list: List[np.ndarray] = [v0_vec.copy()]

    while t_list[-1] < t_max:
        t = t_list[-1]
        r = pos_list[-1]
        v = vel_list[-1]
        if r[1] <= ground_y and t > 0:
            break

        a1 = accel(v)
        k1_v = a1 * t_step
        k1_r = v * t_step

        a2 = accel(v + 0.5 * k1_v)
        k2_v = a2 * t_step
        k2_r = (v + 0.5 * k1_v) * t_step

        a3 = accel(v + 0.5 * k2_v)
        k3_v = a3 * t_step
        k3_r = (v + 0.5 * k2_v) * t_step

        a4 = accel(v + k3_v)
        k4_v = a4 * t_step
        k4_r = (v + k3_v) * t_step

        v_next = v + (k1_v + 2*k2_v + 2*k3_v + k4_v)/6.0
        r_next = r + (k1_r + 2*k2_r + 2*k3_r + k4_r)/6.0

        t_list.append(t + t_step)
        pos_list.append(r_next)
        vel_list.append(v_next)

        if r_next[1] <= ground_y:
            y1, y2 = r[1], r_next[1]
            if y1 != y2:
                alpha = (y1 - ground_y) / (y1 - y2)
                r_land = r + alpha * (r_next - r)
                pos_list[-1] = r_land
            break

    pos = np.vstack(pos_list)
    vel = np.vstack(vel_list)
    t = np.array(t_list)

    speed = np.linalg.norm(vel, axis=1)
    ke = 0.5 * proj.m * (speed ** 2)
    pe = proj.m * env.g * pos[:, 1]
    me = ke + pe
    p_mag = proj.m * speed

    landing_point = pos[-1]
    max_height = np.max(pos[:, 1])

    return SimulationResult(
        t=t, pos=pos, vel=vel, ke=ke, pe=pe, me=me, p_mag=p_mag,
        landing_point=landing_point, max_height=max_height,
        v0=v0, angle_deg=angle_deg, yaw_deg=math.degrees(yaw), pullback=s,
    )


def plan_shot(target: np.ndarray, launch_pos: np.ndarray, env: Env, proj: Projectile, launcher: Launcher,
              t_step: float = 0.002, ground_y: float = 0.0,
              verbose: bool = True) -> Tuple[SimulationResult, SimulationResult]:
    dxz = target[[0, 2]] - launch_pos[[0, 2]]
    R = float(np.linalg.norm(dxz))
    dy = float(target[1] - launch_pos[1])
    yaw_deg = math.degrees(math.atan2(dxz[1], dxz[0])) if R > 1e-9 else 0.0

    angle_guess_deg, v0_vac = ideal_vacuum_angle_and_speed(R, dy, env.g)
    s_guess = speed_to_pullback(v0_vac, launcher.k, launcher.eta, proj.m)
    s_guess = float(np.clip(s_guess, 0.01, launcher.s_max))

    env_vac = Env(g=env.g, rho=0.0, wind=np.zeros(3))
    vac_sim = simulate(launcher.k, launcher.eta, s_guess, angle_guess_deg, yaw_deg,
                       launch_pos, proj, env_vac, t_step=t_step, ground_y=ground_y)

    s = s_guess
    angle_deg = angle_guess_deg
    step_s = max(0.02, 0.1 * s_guess)
    step_a = 2.0
    best_sim = simulate(launcher.k, launcher.eta, s, angle_deg, yaw_deg,
                        launch_pos, proj, env, t_step=t_step, ground_y=ground_y)

    def error(sim: SimulationResult) -> float:
        return float(np.linalg.norm(sim.landing_point - target))

    best_err = error(best_sim)
    if verbose:
        print(f"Initial guess -> s={s:.3f} m, angle={angle_deg:.2f}°, yaw={yaw_deg:.2f}°, v0={best_sim.v0:.2f} m/s, error={best_err:.3f} m")

    for it in range(200):
        improved = False
        candidates = [
            (s + step_s, angle_deg), (s - step_s, angle_deg),
            (s, angle_deg + step_a), (s, angle_deg - step_a),
            (s + 0.5*step_s, angle_deg + 0.5*step_a), (s - 0.5*step_s, angle_deg - 0.5*step_a),
        ]
        candidates = [
            (float(np.clip(cs, 0.01, launcher.s_max)), float(np.clip(ca, 5.0, 85.0)))
            for cs, ca in candidates
        ]

        sims = []
        errs = []
        for cs, ca in candidates:
            sim = simulate(launcher.k, launcher.eta, cs, ca, yaw_deg,
                           launch_pos, proj, env, t_step=t_step, ground_y=ground_y)
            sims.append(sim)
            errs.append(error(sim))

        min_idx = int(np.argmin(errs)) if errs else -1
        if min_idx >= 0 and errs[min_idx] + 1e-6 < best_err:
            best_sim = sims[min_idx]
            best_err = errs[min_idx]
            s = candidates[min_idx][0]
            angle_deg = candidates[min_idx][1]
            improved = True
        
        if improved:
            step_s *= 0.9
            step_a *= 0.9
        else:
            step_s *= 0.7
            step_a *= 0.7

        if verbose:
            print(f"Iter {it+1:02d}: error={best_err:.3f} m | s={s:.3f} m, angle={angle_deg:.2f}°, steps=({step_s:.3f},{step_a:.2f})")

        if best_err < 0.05 or (step_s < 1e-3 and step_a < 0.05):
            break

    return best_sim, vac_sim


def make_plots(actual: SimulationResult, vacuum: SimulationResult, target: np.ndarray, show: bool = True,
               save_prefix: Optional[str] = None):
    yaw = math.radians(actual.yaw_deg)
    R_yaw = np.array([[ math.cos(yaw), 0.0, math.sin(yaw)],
                      [ 0.0,           1.0, 0.0           ],
                      [-math.sin(yaw), 0.0, math.cos(yaw)]])

    def to_plane(pos3):
        pos_rot = pos3 @ R_yaw.T
        return pos_rot[:, 0], pos_rot[:, 1]

    ax_act_x, ax_act_y = to_plane(actual.pos)
    ax_vac_x, ax_vac_y = to_plane(vacuum.pos)

    tgt_rot = (target.reshape(1,3) @ R_yaw.T).flatten()

    fig, axs = plt.subplots(2, 2, figsize=(12, 9))

    ax = axs[0,0]
    ax.plot(ax_vac_x, ax_vac_y, label='Vacuum', color='tab:blue')
    ax.plot(ax_act_x, ax_act_y, label='Drag+Wind', color='tab:orange')
    ax.scatter([tgt_rot[0]], [tgt_rot[1]], marker='x', s=100, color='red', label='Target')
    ax.scatter([ax_vac_x[-1]], [ax_vac_y[-1]], marker='o', color='tab:blue', label='Vacuum landing')
    ax.scatter([ax_act_x[-1]], [ax_act_y[-1]], marker='o', color='tab:orange', label='Actual landing')
    ax.set_title('Trajectory (yaw-aligned plane)')
    ax.set_xlabel('Along-track distance (m)')
    ax.set_ylabel('Height (m)')
    ax.legend(); ax.grid(True, ls=':')

    ax = axs[0,1]
    ax.plot(actual.t, np.linalg.norm(actual.vel, axis=1), label='Speed', color='tab:green')
    ax.set_title('Speed vs Time'); ax.set_xlabel('Time (s)'); ax.set_ylabel('Speed (m/s)')
    ax.grid(True, ls=':')

    ax = axs[1,0]
    ax.plot(actual.t, actual.ke, label='KE')
    ax.plot(actual.t, actual.pe, label='PE')
    ax.plot(actual.t, actual.me, label='ME')
    ax.set_title('Energies vs Time'); ax.set_xlabel('Time (s)'); ax.set_ylabel('Energy (J)')
    ax.legend(); ax.grid(True, ls=':')

    ax = axs[1,1]
    ax.plot(actual.t, actual.p_mag, label='|p|')
    ax.set_title('Momentum magnitude vs Time'); ax.set_xlabel('Time (s)'); ax.set_ylabel('Momentum (kg·m/s)')
    ax.grid(True, ls=':')

    fig.tight_layout()

    if save_prefix:
        fig.savefig(f"{save_prefix}_plots.png", dpi=160)
    if show:
        plt.show()


def prompt_or_args(args):
    """Collect target and k via prompts when not supplied, and randomize physics params."""
    # Target
    if args.target is None and not args.click_map:
        print("Enter target coordinates (x y z) in meters, e.g., 25 0 0")
        parts = input("Target x y z: ").strip().split()
        if len(parts) != 3:
            raise ValueError("Expected three numbers for target.")
        target = np.array([float(parts[0]), float(parts[1]), float(parts[2])], dtype=float)
    else:
        target = np.array(args.target if args.target is not None else [0.0, 0.0, 0.0], dtype=float)

    # Spring constant
    if args.k is None:
        k = float(input("Enter spring constant k (N/m), e.g., 300: ").strip())
    else:
        k = float(args.k)

    # Randomize physics
    rng = np.random.default_rng()
    # Mass ~ N(0.20, 0.05), clipped to [0.12, 0.35]
    mass = float(np.clip(rng.normal(0.20, 0.05), 0.12, 0.35))
    # Diameter ~ N(0.12, 0.02), clipped to [0.08, 0.16]
    diameter = float(np.clip(rng.normal(0.12, 0.02), 0.08, 0.16))
    # Drag coefficient ~ N(0.47, 0.05), clipped to [0.35, 0.65]
    cd = float(np.clip(rng.normal(0.47, 0.05), 0.35, 0.65))
    # Wind components ~ N(0, 1.5) m/s (mild variability), clipped to [-5, 5]
    wind = rng.normal(0.0, 1.5, size=3)
    wind = np.clip(wind, -5.0, 5.0)

    print("\n--- Randomized real-life variability ---")
    print(f"Mass:     {mass:.3f} kg")
    print(f"Diameter: {diameter:.3f} m")
    print(f"Cd:       {cd:.3f}")
    print(f"Wind:     ({wind[0]:.2f}, {wind[1]:.2f}, {wind[2]:.2f}) m/s")

    return target, k, mass, diameter, cd, wind


def click_to_target(args) -> np.ndarray:
    """Open a simple 2D map (x–z plane) and let the user click to set target.
       The y (height) is taken from --target y if provided else 0.
    """
    print("\nClick on the map to choose the target (x–z). Close the window when done.")
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title('Choose Target on Map (x–z plane)')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('z (m)')
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.grid(True, ls=':')

    target = [0.0, 0.0, 0.0]
    target_y = args.target[1] if (args.target is not None and len(args.target) == 3) else 0.0

    marker = [None]

    def onclick(event):
        if not event.inaxes:
            return
        x, z = event.xdata, event.ydata
        target[0] = float(x)
        target[1] = float(target_y)
        target[2] = float(z)
        if marker[0] is not None:
            marker[0].remove()
        marker[0] = ax.scatter([x], [z], c='red', s=100, marker='x')
        fig.canvas.draw_idle()
        print(f"Selected target: x={x:.2f} m, z={z:.2f} m, y={target_y:.2f} m")

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    fig.canvas.mpl_disconnect(cid)

    return np.array(target, dtype=float)


def main():
    parser = argparse.ArgumentParser(description='Interactive water balloon launcher')
    parser.add_argument('--target', nargs=3, type=float, help='Target (x y z) in meters')
    parser.add_argument('--k', type=float, help='Spring constant (N/m)')
    parser.add_argument('--click_map', action='store_true', help='Click to choose target on a simple x–z map')

    # Optional physical parameters
    parser.add_argument('--eta', type=float, default=0.85, help='Spring energy efficiency (0..1)')
    parser.add_argument('--launch', nargs=3, type=float, default=[0.0, 1.0, 0.0], help='Launcher origin (x y z) m')

    # Numerical/constraints
    parser.add_argument('--s_max', type=float, default=0.5, help='Maximum pullback (m)')
    parser.add_argument('--t_step', type=float, default=0.002, help='Integration time step (s)')
    parser.add_argument('--ground_y', type=float, default=0.0, help='Ground height y (m)')
    parser.add_argument('--no_plot', action='store_true', help='Disable plotting')
    parser.add_argument('--save_prefix', type=str, default=None, help='Prefix to save plots')

    args = parser.parse_args()

    # Target and randomized physics
    if args.click_map:
        tgt = click_to_target(args)
    else:
        tgt = None
    target, k, mass, diameter, cd, wind = prompt_or_args(args)
    if tgt is not None:
        target = tgt

    # Build objects
    area = math.pi * (0.5 * diameter) ** 2
    proj = Projectile(m=mass, cd=cd, area=area)
    env = Env(g=9.81, rho=1.225, wind=np.array(wind, dtype=float))
    launcher = Launcher(k=k, eta=args.eta, s_max=args.s_max)

    launch_pos = np.array(args.launch, dtype=float)

    actual_sim, vacuum_sim = plan_shot(target, launch_pos, env, proj, launcher,
                                       t_step=args.t_step, ground_y=args.ground_y, verbose=True)

    print("\n=== Summary (Actual) ===")
    print(f"Angle:     {actual_sim.angle_deg:.2f}°\nYaw:       {actual_sim.yaw_deg:.2f}°\nPullback:  {actual_sim.pullback:.3f} m\nInitial v: {actual_sim.v0:.2f} m/s")
    print(f"Landing:   ({actual_sim.landing_point[0]:.3f}, {actual_sim.landing_point[1]:.3f}, {actual_sim.landing_point[2]:.3f}) m")
    print(f"Max height:{actual_sim.max_height:.3f} m")

    print("\n=== Comparison ===")
    print(f"Vacuum landing: ({vacuum_sim.landing_point[0]:.3f}, {vacuum_sim.landing_point[1]:.3f}, {vacuum_sim.landing_point[2]:.3f}) m")
    err = np.linalg.norm(actual_sim.landing_point - target)
    print(f"Target:         ({target[0]:.3f}, {target[1]:.3f}, {target[2]:.3f}) m | error={err:.3f} m")

    if not args.no_plot:
        make_plots(actual_sim, vacuum_sim, target, show=True, save_prefix=args.save_prefix)


if __name__ == '__main__':
    main()
