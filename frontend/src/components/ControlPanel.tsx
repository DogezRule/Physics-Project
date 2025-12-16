import React, { useState } from 'react';
import { calculateTrajectory } from '../api';
import type { CalculationResponse, EnvironmentParams } from '../api';

interface ControlPanelProps {
    onCalculationResult: (data: CalculationResponse, target: { x: number, y: number, z: number }) => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({ onCalculationResult }) => {
    const [target, setTarget] = useState({ x: 10, y: 0, z: 0 });
    const [k, setK] = useState(100);
    const [env, setEnv] = useState<EnvironmentParams>({
        wind_speed: 0,
        wind_direction: 0,
        air_density: 1.225,
        drag_coefficient: 0.47
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleCalculate = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await calculateTrajectory(target.x, target.y, target.z, k, env);
            onCalculationResult(data, target);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Calculation failed");
        } finally {
            setLoading(false);
        }
    };

    const inputStyle = {
        width: '100%',
        padding: '8px',
        marginTop: '4px',
        background: 'rgba(0,0,0,0.3)',
        border: '1px solid #444',
        color: '#fff',
        borderRadius: '4px'
    };

    const labelStyle = {
        display: 'block',
        marginTop: '10px',
        fontSize: '12px',
        color: '#aaa',
        textTransform: 'uppercase' as const,
        letterSpacing: '1px'
    };

    const sectionHeaderStyle = {
        borderBottom: '1px solid #333',
        paddingBottom: '5px',
        marginBottom: '10px',
        color: '#00ccff',
        textTransform: 'uppercase' as const,
        fontSize: '14px',
        fontWeight: 'bold' as const
    };

    return (
        <div style={{
            position: 'absolute',
            top: 20,
            left: 20,
            width: '280px',
            background: 'rgba(10, 15, 30, 0.75)',
            backdropFilter: 'blur(10px)',
            padding: '20px',
            borderRadius: '12px',
            color: 'white',
            border: '1px solid rgba(0, 255, 255, 0.1)',
            boxShadow: '0 0 20px rgba(0,0,0,0.5)',
            maxHeight: '90vh',
            overflowY: 'auto'
        }}>
            <h2 style={{
                marginTop: 0,
                textAlign: 'center',
                color: '#fff',
                textShadow: '0 0 10px rgba(0,255,255,0.5)',
                fontFamily: 'monospace'
            }}>
                MISSION CONTROL
            </h2>

            <div style={{ marginBottom: 20 }}>
                <div style={sectionHeaderStyle}>Target Coordinates</div>

                <label style={labelStyle}>Range (X) [m]</label>
                <input
                    type="number" step="0.5"
                    value={target.x}
                    onChange={e => setTarget({ ...target, x: parseFloat(e.target.value) })}
                    style={inputStyle}
                />

                <label style={labelStyle}>Height (Y) [m]</label>
                <input
                    type="number" step="0.5"
                    value={target.y}
                    onChange={e => setTarget({ ...target, y: parseFloat(e.target.value) })}
                    style={inputStyle}
                />

                <label style={labelStyle}>Offset (Z) [m]</label>
                <input
                    type="number" step="0.5"
                    value={target.z}
                    onChange={e => setTarget({ ...target, z: parseFloat(e.target.value) })}
                    style={inputStyle}
                />
            </div>

            <div style={{ marginBottom: 20 }}>
                <div style={sectionHeaderStyle}>Launcher Config</div>

                <label style={labelStyle}>Spring Constant (k) [N/m]</label>
                <input
                    type="range" min="10" max="500" step="1"
                    value={k}
                    onChange={e => setK(parseFloat(e.target.value))}
                    style={{ ...inputStyle, padding: 0 }}
                />
                <div style={{ textAlign: 'right', color: '#00ccff', fontSize: '12px' }}>{k} N/m</div>
            </div>

            <div style={{ marginBottom: 20 }}>
                <div style={{ ...sectionHeaderStyle, color: '#ffaa00' }}>Environment (Beta)</div>

                <label style={labelStyle}>Wind Speed [m/s]</label>
                <input
                    type="range" min="0" max="20" step="0.5"
                    value={env.wind_speed}
                    onChange={e => setEnv({ ...env, wind_speed: parseFloat(e.target.value) })}
                    style={{ ...inputStyle, padding: 0 }}
                />
                <div style={{ textAlign: 'right', color: '#ff0055', fontSize: '12px' }}>{env.wind_speed} m/s</div>

                <label style={labelStyle}>Wind Direction [deg] <span style={{ fontSize: '10px', color: '#666', textTransform: 'none' }}>(0°=+X, 90°=+Z)</span></label>
                <input
                    type="range" min="0" max="360" step="15"
                    value={env.wind_direction}
                    onChange={e => setEnv({ ...env, wind_direction: parseFloat(e.target.value) })}
                    style={{ ...inputStyle, padding: 0 }}
                />
                <div style={{ textAlign: 'right', color: '#ff0055', fontSize: '12px' }}>{env.wind_direction}°</div>

                <label style={labelStyle}>Air Density [kg/m³]</label>
                <input
                    type="number" step="0.01"
                    value={env.air_density}
                    onChange={e => setEnv({ ...env, air_density: parseFloat(e.target.value) })}
                    style={inputStyle}
                />
            </div>

            <button
                onClick={handleCalculate}
                disabled={loading}
                style={{
                    width: '100%',
                    padding: '12px',
                    background: loading ? '#333' : 'linear-gradient(45deg, #00ccff, #007bff)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading ? 'wait' : 'pointer',
                    fontWeight: 'bold',
                    textTransform: 'uppercase',
                    letterSpacing: '1px',
                    boxShadow: '0 0 15px rgba(0, 204, 255, 0.4)'
                }}
            >
                {loading ? "CALCULATING..." : "INITIATE LAUNCH"}
            </button>

            {error && <div style={{ color: '#ff4444', marginTop: 15, fontSize: '12px', border: '1px solid #ff4444', padding: '5px' }}>{error}</div>}
        </div>
    );
};

export default ControlPanel;
