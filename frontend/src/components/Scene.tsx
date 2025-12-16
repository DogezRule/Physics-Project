import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Text, Line, Sphere, Box } from '@react-three/drei';
import * as THREE from 'three';
import type { TrajectoryPoint } from '../api';

interface SceneProps {
    trajectory: TrajectoryPoint[];
    target: { x: number, y: number, z: number };
}

const Scene: React.FC<SceneProps> = ({ trajectory, target }) => {

    const points = useMemo(() => {
        return trajectory.map(p => new THREE.Vector3(p.x, p.y, p.z));
    }, [trajectory]);

    return (
        <Canvas camera={{ position: [-5, 5, 5], fov: 50 }}>
            <color attach="background" args={['#202020']} />
            <ambientLight intensity={0.7} />
            <pointLight position={[10, 10, 10]} intensity={1.5} />

            <OrbitControls makeDefault />

            <Grid
                width={100} height={100}
                sectionSize={5} sectionColor="#888"
                sectionThickness={1.5}
                cellSize={1} cellColor="#555"
                cellThickness={1}
                position={[0, -0.01, 0]}
                infiniteGrid
                fadeDistance={60}
            />

            <axesHelper args={[5]} />
            <Text position={[5.2, 0, 0]} fontSize={0.5} color="red">X (Distance)</Text>
            <Text position={[0, 5.2, 0]} fontSize={0.5} color="green">Y (Height)</Text>
            <Text position={[0, 0, 5.2]} fontSize={0.5} color="blue">Z (Lateral)</Text>

            <Box position={[0, 0.25, 0]} args={[0.5, 0.5, 0.5]}>
                <meshStandardMaterial color="orange" />
            </Box>
            <Text position={[0, 0.8, 0]} fontSize={0.3} color="orange">Launcher</Text>

            <Sphere position={[target.x, target.y, target.z]} args={[0.3]}>
                <meshStandardMaterial color="cyan" emissive="cyan" emissiveIntensity={0.5} />
            </Sphere>
            <Text position={[target.x, target.y + 0.6, target.z]} fontSize={0.3} color="cyan">
                Target ({target.x.toFixed(1)}, {target.y.toFixed(1)}, {target.z.toFixed(1)})
            </Text>

            {points.length > 0 && (
                <Line
                    points={points}
                    color="yellow"
                    lineWidth={3}
                />
            )}

            {points.length > 0 && (
                <Sphere position={points[points.length - 1]} args={[0.15]}>
                    <meshStandardMaterial color="red" />
                </Sphere>
            )}

        </Canvas>
    );
};

export default Scene;
