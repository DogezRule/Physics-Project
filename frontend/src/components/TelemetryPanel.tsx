import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { TrajectoryPoint, CalculationResponse } from '../api';
import { WATER_BALLOON_MASS, EARTH_GRAVITY } from '../constants';

interface TelemetryPanelProps {
    trajectory: TrajectoryPoint[];
    lastResult: CalculationResponse | null;
}

const TelemetryPanel: React.FC<TelemetryPanelProps> = ({ trajectory, lastResult }) => {
    if (!trajectory || trajectory.length === 0) return null;

    const flightData = trajectory.filter(p => p.y >= 0);

    const chartData = flightData.map(p => {
        const v = Math.sqrt(p.vx ** 2 + p.vy ** 2 + p.vz ** 2);
        const ke = 0.5 * WATER_BALLOON_MASS * v ** 2;
        const pe = WATER_BALLOON_MASS * EARTH_GRAVITY * p.y;
        return {
            time: p.time.toFixed(2),
            velocity: v,
            ke,
            pe,
            me: ke + pe,
            momentum: WATER_BALLOON_MASS * v
        };
    });

    const panelStyle = {
        position: 'absolute' as const,
        right: 20,
        top: 20,
        bottom: 20,
        width: '350px',
        background: 'rgba(10, 15, 30, 0.75)',
        backdropFilter: 'blur(10px)',
        padding: '20px',
        borderRadius: '12px',
        color: 'white',
        border: '1px solid rgba(0, 255, 0, 0.1)',
        boxShadow: '0 0 20px rgba(0,0,0,0.5)',
        overflowY: 'auto' as const,
        display: 'flex',
        flexDirection: 'column' as const,
        gap: '20px'
    };

    const statBoxStyle = {
        background: 'rgba(0, 255, 0, 0.05)',
        border: '1px solid rgba(0, 255, 0, 0.2)',
        padding: '10px',
        borderRadius: '6px'
    };

    const statLabel = {
        fontSize: '10px',
        color: '#8f8',
        textTransform: 'uppercase' as const,
        letterSpacing: '1px'
    };

    const statValue = {
        fontSize: '18px',
        fontWeight: 'bold',
        color: '#fff',
        fontFamily: 'monospace'
    };

    return (
        <div style={panelStyle}>
            <h2 style={{
                marginTop: 0,
                textAlign: 'center',
                color: '#fff',
                fontFamily: 'monospace',
                borderBottom: '1px solid rgba(0,255,0,0.3)',
                paddingBottom: '10px'
            }}>
                TELEMETRY
            </h2>

            {lastResult && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <div style={statBoxStyle}>
                        <div style={statLabel}>Launch Angle</div>
                        <div style={statValue}>{lastResult.launch_angle.toFixed(1)}°</div>
                    </div>
                    <div style={statBoxStyle}>
                        <div style={statLabel}>Azimuth</div>
                        <div style={statValue}>{lastResult.azimuth_angle.toFixed(1)}°</div>
                    </div>
                    <div style={statBoxStyle}>
                        <div style={statLabel}>Init Velocity</div>
                        <div style={statValue}>{lastResult.velocity.toFixed(2)} m/s</div>
                    </div>
                    <div style={statBoxStyle}>
                        <div style={statLabel}>Pullback</div>
                        <div style={statValue}>{(lastResult.pullback * 100).toFixed(1)} cm</div>
                    </div>
                </div>
            )}

            <div style={{ flex: 1, minHeight: '200px' }}>
                <h4 style={statLabel}>Velocity Profile</h4>
                <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                        <XAxis dataKey="time" stroke="#666" tick={{ fontSize: 10 }} />
                        <YAxis stroke="#8884d8" tick={{ fontSize: 10 }} />
                        <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }} />
                        <Line type="monotone" dataKey="velocity" stroke="#00ccff" dot={false} strokeWidth={2} />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div style={{ flex: 1, minHeight: '200px' }}>
                <h4 style={statLabel}>Energy Distribution</h4>
                <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                        <XAxis dataKey="time" stroke="#666" tick={{ fontSize: 10 }} />
                        <YAxis stroke="#8884d8" tick={{ fontSize: 10 }} />
                        <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }} />
                        <Legend />
                        <Line type="monotone" dataKey="ke" stroke="#ff0055" dot={false} name="KE" />
                        <Line type="monotone" dataKey="pe" stroke="#00ff99" dot={false} name="PE" />
                        <Line type="monotone" dataKey="me" stroke="#ffaa00" dot={false} name="ME (Total)" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default TelemetryPanel;
