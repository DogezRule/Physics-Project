import numpy as np

WATER_BALLOON_MASS = 0.125  # kg
BALLOON_RADIUS = 0.08  # meters

EARTH_GRAVITY = 9.81  # m/s² (standard Earth gravity)
AIR_DENSITY = 1.225  # kg/m³ (sea level, 15°C)
KINEMATIC_VISCOSITY = 1.81e-5  # m²/s (air at 15°C)

DRAG_COEFFICIENT = 0.47  # Dimensionless (sphere in turbulent flow)

WIND_SPEED = 5.0  # m/s
WIND_DIRECTION_DEG = 45.0  # degrees (wind direction relative to launcher)

LAUNCHER_SPRING_CONSTANT = 500.0  # N/m (typical rubber band/spring launcher)

SIMULATION_MAX_TIME = 10.0  # seconds (max flight time)
SIMULATION_NUM_POINTS = 1000  # integration points
SIMULATION_TOLERANCE = 1e-8  # ODE solver tolerance

# X: Forward direction (primary launch axis)
# Y: Vertical direction (up is positive)
# Z: Lateral direction (perpendicular to X and Y)

TEMPERATURE_CELSIUS = 15  # °C (affects air density)
HUMIDITY_PERCENT = 60  # % (affects air density slightly)
ALTITUDE_METERS = 0  # m (above sea level - affects air density)