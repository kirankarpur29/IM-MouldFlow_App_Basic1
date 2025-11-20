import { useState, useRef } from 'react'
import { api } from '../../api/client'

interface FileUploadProps {
  projectId: number
  onUploaded: (part: any) => void
}

export default function FileUpload({ projectId, onUploaded }: FileUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.stl')) {
      alert('Please upload an STL file')
      return
    }

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('project_id', String(projectId))
      formData.append('name', file.name)

      const response = await api.post('/api/v1/parts/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      onUploaded(response.data)
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Failed to upload file')
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      handleFile(e.target.files[0])
    }
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      }`}
      onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
      onDragLeave={() => setDragActive(false)}
      onDrop={handleDrop}
    >
      {uploading ? (
        <div>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Processing geometry...</p>
        </div>
      ) : (
        <>
          <div className="text-4xl mb-3">📁</div>
          <p className="text-gray-700 mb-2">
            Drag and drop STL file here
          </p>
          <p className="text-gray-500 text-sm mb-4">or</p>
          <button
            onClick={() => inputRef.current?.click()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Browse Files
          </button>
          <input
            ref={inputRef}
            type="file"
            accept=".stl"
            onChange={handleChange}
            className="hidden"
          />
          <p className="text-xs text-gray-400 mt-4">
            Supported: STL files up to 50MB
          </p>
        </>
      )}
    </div>
  )
}
