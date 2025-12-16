import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { TrajectoryPoint } from '../api';
import { WATER_BALLOON_MASS, EARTH_GRAVITY } from '../constants';



interface ChartsProps {
    data: TrajectoryPoint[];
}

const Charts: React.FC<ChartsProps> = ({ data }) => {
    if (!data || data.length === 0) return null;

    // Filter data to ensure we only show flight (y >= 0)
    // Although backend should handle this, double check for graph cleanliness
    const flightData = data.filter(p => p.y >= 0);

    const chartData = flightData.map(p => {
        const v = Math.sqrt(p.vx ** 2 + p.vy ** 2 + p.vz ** 2);
        const ke = 0.5 * WATER_BALLOON_MASS * v ** 2;
        const pe = WATER_BALLOON_MASS * EARTH_GRAVITY * p.y;
        const me = ke + pe;
        const momentum = WATER_BALLOON_MASS * v;

        return {
            time: p.time.toFixed(2),
            velocity: v,
            ke,
            pe,
            me,
            momentum
        };
    });

    return (
        <div style={{
            position: 'absolute',
            bottom: 10,
            right: 10,
            background: 'rgba(0,0,0,0.85)',
            padding: '15px',
            borderRadius: '8px',
            color: 'white',
            width: '450px',
            maxHeight: '40vh',
            overflowY: 'auto',
            zIndex: 10,
            boxShadow: '0 0 10px rgba(0,0,0,0.5)'
        }}>
            <h3 style={{ marginTop: 0, fontSize: '16px' }}>Physics Data</h3>

            <div style={{ height: '180px', marginBottom: '20px' }}>
                <h4 style={{ margin: '5px 0', fontSize: '14px' }}>Velocity & Momentum</h4>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                        <XAxis dataKey="time" stroke="#ccc" tick={{ fontSize: 10 }} />
                        <YAxis yAxisId="left" stroke="#8884d8" tick={{ fontSize: 10 }} />
                        <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" tick={{ fontSize: 10 }} />
                        <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '10px' }} />
                        <Line yAxisId="left" type="monotone" dataKey="velocity" stroke="#8884d8" dot={false} name="Velocity (m/s)" />
                        <Line yAxisId="right" type="monotone" dataKey="momentum" stroke="#82ca9d" dot={false} name="Momentum (kg·m/s)" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div style={{ height: '180px' }}>
                <h4 style={{ margin: '5px 0', fontSize: '14px' }}>Energy</h4>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                        <XAxis dataKey="time" stroke="#ccc" tick={{ fontSize: 10 }} />
                        <YAxis stroke="#ff7300" tick={{ fontSize: 10 }} />
                        <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '10px' }} />
                        <Line type="monotone" dataKey="ke" stroke="#8884d8" dot={false} name="KE (J)" />
                        <Line type="monotone" dataKey="pe" stroke="#82ca9d" dot={false} name="PE (J)" />
                        <Line type="monotone" dataKey="me" stroke="#ff7300" dot={false} name="Total ME (J)" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default Charts;
