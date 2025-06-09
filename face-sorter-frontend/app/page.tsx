"use client"; // if using app directory
import React, { useState } from "react";
import { getApiUrl } from "./config";

interface ApiResponse {
  status: 'success' | 'error';
  message?: string;
  result?: any;
}

export default function Home() {
  const [status, setStatus] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setStatus("");
    setError(null);
    setDebugInfo("");
    setIsLoading(true);

    const formData = new FormData();
    const refInput = document.getElementById("ref") as HTMLInputElement;
    const groupInput = document.getElementById("group") as HTMLInputElement;

    if (!refInput.files?.length || !groupInput.files?.length) {
      setError("Please select both reference faces and group photos");
      setIsLoading(false);
      return;
    }

    for (let file of refInput.files) {
      formData.append("reference_faces", file);
    }

    for (let file of groupInput.files) {
      formData.append("group_photos", file);
    }

    const apiUrl = getApiUrl('upload');
    setDebugInfo(`Attempting to connect to: ${apiUrl}`);

    try {
      console.log('Sending request to:', apiUrl);
      const res = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      console.log('Response status:', res.status);
      const data: ApiResponse = await res.json();
      console.log('Response data:', data);

      if (res.ok && data.status === 'success') {
        setStatus("Success! Photos sorted.");
      } else {
        setError(data.message || "Upload failed. Please try again.");
      }
    } catch (error) {
      console.error('Error details:', error);
      setError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setDebugInfo(`Failed to connect to ${apiUrl}. Make sure the backend is running at http://localhost:5000`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Face Sorter</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-2">Reference Faces:</label>
          <input 
            type="file" 
            id="ref" 
            multiple 
            required 
            className="w-full p-2 border rounded"
            accept="image/*"
          />
        </div>
        <div>
          <label className="block mb-2">Group Photos:</label>
          <input 
            type="file" 
            id="group" 
            multiple 
            required 
            className="w-full p-2 border rounded"
            accept="image/*"
          />
        </div>
        <button 
          type="submit" 
          disabled={isLoading}
          className={`px-4 py-2 rounded ${
            isLoading 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-blue-500 hover:bg-blue-600'
          } text-white`}
        >
          {isLoading ? 'Processing...' : 'Upload & Sort'}
        </button>
      </form>
      {status && <p className="mt-4 text-green-600">{status}</p>}
      {error && <p className="mt-4 text-red-600">{error}</p>}
      {debugInfo && <p className="mt-4 text-gray-600 text-sm">{debugInfo}</p>}
    </main>
  );
}
