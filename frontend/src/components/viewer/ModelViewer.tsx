import { useEffect, useRef, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Center } from '@react-three/drei'
import * as THREE from 'three'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import { api } from '../../api/client'

interface ModelViewerProps {
  partId: number
}

function Model({ geometry }: { geometry: THREE.BufferGeometry | null }) {
  if (!geometry) return null

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial color="#3b82f6" metalness={0.3} roughness={0.7} />
    </mesh>
  )
}

export default function ModelViewer({ partId }: ModelViewerProps) {
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadModel()
  }, [partId])

  const loadModel = async () => {
    try {
      const response = await api.get(`/api/v1/parts/${partId}/geometry`, {
        responseType: 'arraybuffer'
      })

      const loader = new STLLoader()
      const geom = loader.parse(response.data)
      geom.computeVertexNormals()
      geom.center()

      setGeometry(geom)
      setError(null)
    } catch (err) {
      console.error('Failed to load model:', err)
      setError('Failed to load 3D model')
    }
  }

  if (error) {
    return (
      <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
        <p className="text-gray-500">{error}</p>
      </div>
    )
  }

  return (
    <div className="h-64 bg-gray-900 rounded-lg overflow-hidden">
      <Canvas camera={{ position: [100, 100, 100], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <directionalLight position={[-10, -10, -5]} intensity={0.3} />
        <Center>
          <Model geometry={geometry} />
        </Center>
        <OrbitControls enableDamping dampingFactor={0.1} />
        <gridHelper args={[200, 20, '#444', '#333']} />
      </Canvas>
    </div>
  )
}
