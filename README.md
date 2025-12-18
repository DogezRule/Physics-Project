# Water Balloon Launcher Simulation

A low-fidelity 3D physics simulation that allows users to launch water balloons at targets, accounting for complex environmental factors.

![Physics Simulation](https://img.shields.io/badge/Physics-Engine-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![React](https://img.shields.io/badge/Frontend-React-blue)
![Three.js](https://img.shields.io/badge/3D-Three.js-orange)

## Features

- **3D Interactive Scene**: Visualize trajectories in a beautiful 3D environment using Three.js and React Three Fiber.
- **Advanced Physics Engine**: Simulates air resistance, wind speed, wind direction, air density, and drag coefficients.
- **Mission Control Dashboard**: A premium "glassmorphism" UI for controlling environmental constants and viewing real-time telemetry.
- **Trajectory Prediction**: Real-time calculation and visualization of the balloon's path.
- **Telemetry & Stats**: Detailed output of flight statistics and integrated graphs.

## Tech Stack

- **Frontend**: Vite, React, TypeScript, Three.js, React Three Fiber, Recharts.
- **Backend**: Python, FastAPI, SciPy, Uvicorn.

## Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

1. Launch both the backend and frontend servers.
2. Open your browser to the local frontend URL (usually `http://localhost:5173`).
3. Use the **Mission Control** panel to adjust environmental variables.
4. Aim and launch the water balloon to observe the trajectory and telemetry data.

## License

This project is licensed under the MIT License.