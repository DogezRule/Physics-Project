from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np

from app.physics.solver import Solver

router = APIRouter()
solver = Solver()

class Target(BaseModel):
    x: float
    y: float
    z: float

class EnvironmentParams(BaseModel):
    wind_speed: float = 0
    wind_direction: float = 0
    air_density: Optional[float] = None
    drag_coefficient: Optional[float] = None

class CalculationRequest(BaseModel):
    target: Target
    spring_constant: float
    environment: Optional[EnvironmentParams] = None
    
class TrajectoryPoint(BaseModel):
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    time: float

class CalculationResponse(BaseModel):
    launch_angle: float
    azimuth_angle: float
    velocity: float
    pullback: float
    trajectory: List[TrajectoryPoint]
    status: str

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/calculate", response_model=CalculationResponse)
def calculate_trajectory(request: CalculationRequest):
    target_pos = (request.target.x, request.target.y, request.target.z)
    
    env_dict = {}
    if request.environment:
        env_dict = request.environment.dict(exclude_none=True)
    
    result = solver.find_optimal_trajectory(
        target_pos, 
        request.spring_constant,
        env_params=env_dict
    )
    
    if result is None:
        raise HTTPException(status_code=400, detail="Target unreachable within physics constraints")
    
    traj_data = result['trajectory']
    points = []
    for i in range(len(traj_data['time'])):
        points.append(TrajectoryPoint(
            x=float(traj_data['x'][i]),
            y=float(traj_data['y'][i]),
            z=float(traj_data['z'][i]),
            vx=float(traj_data['vx'][i]),
            vy=float(traj_data['vy'][i]),
            vz=float(traj_data['vz'][i]),
            time=float(traj_data['time'][i])
        ))
    
    return CalculationResponse(
        launch_angle=result['launch_angle'],
        azimuth_angle=result['azimuth_angle'],
        velocity=result['velocity'],
        pullback=result['pullback'],
        trajectory=points,
        status="success"
    )
