import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export interface EnvironmentParams {
    wind_speed: number;
    wind_direction: number;
    air_density?: number;
    drag_coefficient?: number;
}

export interface CalculationRequest {
    target: {
        x: number;
        y: number;
        z: number;
    };
    spring_constant: number;
    environment?: EnvironmentParams;
}

export interface TrajectoryPoint {
    x: number;
    y: number;
    z: number;
    vx: number;
    vy: number;
    vz: number;
    time: number;
}

export interface CalculationResponse {
    launch_angle: number;
    azimuth_angle: number;
    velocity: number;
    pullback: number;
    trajectory: TrajectoryPoint[];
    status: string;
}

export const calculateTrajectory = async (
    x: number, y: number, z: number, k: number,
    env?: EnvironmentParams
): Promise<CalculationResponse> => {
    const response = await axios.post<CalculationResponse>(`${API_URL}/calculate`, {
        target: { x, y, z },
        spring_constant: k,
        environment: env
    });
    return response.data;
};
