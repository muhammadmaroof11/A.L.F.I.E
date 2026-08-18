import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useGLTF, Float, Environment, ContactShadows } from '@react-three/drei';

function Model({ url, scale = 1.35, autoRotate = false, position = [0, 0.05, 0], rotation = [0.1, 0.42, -0.05] }) {
  const { scene } = useGLTF(url);
  const ref = useRef();

  useFrame((state, delta) => {
    if (autoRotate && ref.current) {
      ref.current.rotation.y += delta * 0.08;
    }
  });

  return (
    <primitive 
      ref={ref} 
      object={scene} 
      scale={scale} 
      position={position} 
      rotation={rotation} 
    />
  );
}

function Loader() {
  return null;
}

export default function ModelViewer({
  url,
  scale = 1.35,
  rotation = [0.1, 0.42, -0.05],
  position = [0, 0.05, 0],
  floatSpeed = 0,
  rotationIntensity = 0,
  floatIntensity = 0,
  autoRotate = false,
  cameraPosition = [0, 0, 4.6],
  className = "w-full h-full min-h-[360px]",
  interactive = false,
  shadows = true,
  enableFloat = false
}) {
  return (
    <div className={`relative ${className} select-none`}>
      <Canvas
        camera={{ position: cameraPosition, fov: 38 }}
        gl={{ antialias: true, alpha: true }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[6, 8, 6]} intensity={1.8} color="#E2E8F0" />
        <directionalLight position={[-6, 2, -4]} intensity={0.5} color="#38BDF8" />
        <pointLight position={[0, 4, 3]} intensity={0.4} color="#818CF8" />

        <Suspense fallback={<Loader />}>
          {enableFloat ? (
            <Float
              speed={floatSpeed}
              rotationIntensity={rotationIntensity}
              floatIntensity={floatIntensity}
            >
              <Model url={url} scale={scale} autoRotate={autoRotate} position={position} rotation={rotation} />
            </Float>
          ) : (
            <Model url={url} scale={scale} autoRotate={autoRotate} position={position} rotation={rotation} />
          )}

          {shadows && (
            <ContactShadows
              position={[0, -1.2, 0]}
              opacity={0.3}
              scale={5.5}
              blur={2.4}
              far={3.5}
              color="#000000"
            />
          )}

          <Environment preset="night" />
        </Suspense>
      </Canvas>
    </div>
  );
}
