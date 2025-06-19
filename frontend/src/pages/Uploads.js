import React, { useState, useEffect } from 'react';
import { Upload as UploadIcon, File, Trash2, Download } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

function Uploads() {
  const [uploads, setUploads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchUploads();
  }, []);

  const fetchUploads = async () => {
    try {
      const response = await api.get('/uploads/uploads');
      setUploads(response.uploads);
    } catch (error) {
      toast.error('Failed to fetch uploads');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Only PDF and DOCX files are allowed');
      return;
    }

    // Validate file size (20MB)
    if (file.size > 20 * 1024 * 1024) {
      toast.error('File size must be less than 20MB');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('/uploads/exam', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      toast.success('File uploaded successfully!');
      fetchUploads();
    } catch (error) {
      toast.error('Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteUpload = async (uploadId) => {
    if (window.confirm('Are you sure you want to delete this upload?')) {
      try {
        await api.delete(`/uploads/uploads/${uploadId}`);
        toast.success('Upload deleted successfully');
        fetchUploads();
      } catch (error) {
        toast.error('Failed to delete upload');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Uploads</h1>
        <p className="text-gray-600">Upload study materials for AI analysis</p>
      </div>

      {/* Upload Area */}
      <div className="card">
        <div className="text-center py-8">
          <UploadIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Upload Study Materials
          </h3>
          <p className="text-gray-600 mb-4">
            Upload PDF or DOCX files to extract questions and concepts
          </p>
          
          <label className="btn btn-primary cursor-pointer">
            <UploadIcon size={20} />
            {uploading ? 'Uploading...' : 'Choose File'}
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploading}
            />
          </label>
          
          <p className="text-xs text-gray-500 mt-2">
            Maximum file size: 20MB
          </p>
        </div>
      </div>

      {/* Uploads List */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Your Uploads</h2>
        
        {uploads.length === 0 ? (
          <div className="text-center py-8">
            <File className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-sm font-medium text-gray-900 mb-2">No uploads yet</h3>
            <p className="text-sm text-gray-500">
              Upload your first study material to get started.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {uploads.map((upload) => (
              <div key={upload.id} className="card">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <File className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 truncate">
                        {upload.filename}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {upload.file_type.toUpperCase()} • {Math.round(upload.file_size / 1024)}KB
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDeleteUpload(upload.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
                
                <div className="mt-3 pt-3 border-t">
                  <div className="flex items-center justify-between">
                    <span className={`status-badge status-${upload.status}`}>
                      {upload.status}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(upload.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  {upload.parsed_data && (
                    <div className="mt-2 text-xs text-gray-600">
                      <p>Questions: {upload.parsed_data.total_questions || 0}</p>
                      <p>Concepts: {upload.parsed_data.total_concepts || 0}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Uploads; 