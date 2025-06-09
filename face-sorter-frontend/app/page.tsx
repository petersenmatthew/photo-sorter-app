"use client"; // if using app directory
import React, { useState } from "react";
import { getApiUrl } from "./config";

interface ApiResponse {
  status: 'success' | 'error';
  message?: string;
  result?: any;
}

type Step = 'reference' | 'group' | 'processing' | 'complete';

export default function Home() {
  const [currentStep, setCurrentStep] = useState<Step>('reference');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>("");
  const [referenceFiles, setReferenceFiles] = useState<FileList | null>(null);

  const handleReferenceSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setDebugInfo("");
    setIsLoading(true);

    const formData = new FormData();
    const refInput = document.getElementById("ref") as HTMLInputElement;

    if (!refInput.files?.length) {
      setError("Please select reference faces");
      setIsLoading(false);
      return;
    }

    for (let file of refInput.files) {
      formData.append("reference_faces", file);
    }

    try {
      const apiUrl = getApiUrl('registerFaces');
      console.log('Making request to:', apiUrl);
      setDebugInfo(`Attempting to connect to: ${apiUrl}`);

      const res = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      console.log('Response status:', res.status);
      const data: ApiResponse = await res.json();
      console.log('Response data:', data);

      if (res.ok && data.status === 'success') {
        setReferenceFiles(refInput.files);
        setCurrentStep('group');
      } else {
        setError(data.message || "Failed to register faces. Please try again.");
      }
    } catch (error) {
      console.error('Error details:', error);
      setError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setDebugInfo(`Failed to connect to backend. Please make sure it's running at http://localhost:5000`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGroupSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setDebugInfo("");
    setIsLoading(true);
    setCurrentStep('processing');

    const formData = new FormData();
    const groupInput = document.getElementById("group") as HTMLInputElement;

    if (!groupInput.files?.length) {
      setError("Please select group photos");
      setIsLoading(false);
      setCurrentStep('group');
      return;
    }

    // Add reference files from previous step
    if (referenceFiles) {
      for (let file of referenceFiles) {
        formData.append("reference_faces", file);
      }
    }

    // Add group photos
    for (let file of groupInput.files) {
      formData.append("group_photos", file);
    }

    try {
      const apiUrl = getApiUrl('upload');
      console.log('Making request to:', apiUrl);
      setDebugInfo(`Attempting to connect to: ${apiUrl}`);

      const res = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      console.log('Response status:', res.status);
      const data: ApiResponse = await res.json();
      console.log('Response data:', data);

      if (res.ok && data.status === 'success') {
        setCurrentStep('complete');
      } else {
        setError(data.message || "Failed to process photos. Please try again.");
        setCurrentStep('group');
      }
    } catch (error) {
      console.error('Error details:', error);
      setError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setDebugInfo(`Failed to connect to backend. Please make sure it's running at http://localhost:5000`);
      setCurrentStep('group');
    } finally {
      setIsLoading(false);
    }
  };

  const resetProcess = () => {
    setCurrentStep('reference');
    setError(null);
    setDebugInfo("");
    setReferenceFiles(null);
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Face Sorter</h1>
          <p className="text-gray-600">Sort your photos by faces in two simple steps</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className={`flex items-center ${currentStep === 'reference' ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                currentStep === 'reference' ? 'border-blue-600' : 'border-gray-300'
              }`}>1</div>
              <span className="ml-2">Reference Faces</span>
            </div>
            <div className="flex-1 h-0.5 bg-gray-200 mx-4"></div>
            <div className={`flex items-center ${currentStep === 'group' || currentStep === 'processing' || currentStep === 'complete' ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                currentStep === 'group' || currentStep === 'processing' || currentStep === 'complete' ? 'border-blue-600' : 'border-gray-300'
              }`}>2</div>
              <span className="ml-2">Group Photos</span>
            </div>
          </div>
        </div>

        {/* Step 1: Reference Faces */}
        {currentStep === 'reference' && (
          <div className="bg-white p-8 rounded-lg shadow-sm">
            <h2 className="text-2xl font-semibold mb-4">Step 1: Upload Reference Faces</h2>
            <p className="text-gray-600 mb-6">Upload clear photos of the faces you want to sort by.</p>
            <form onSubmit={handleReferenceSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reference Faces
                </label>
                <input 
                  type="file" 
                  id="ref" 
                  multiple 
                  required 
                  className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  accept="image/*"
                />
              </div>
              <button 
                type="submit" 
                disabled={isLoading}
                className={`w-full py-3 px-4 rounded-md text-white font-medium ${
                  isLoading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isLoading ? 'Processing...' : 'Upload Reference Faces'}
              </button>
            </form>
          </div>
        )}

        {/* Step 2: Group Photos */}
        {currentStep === 'group' && (
          <div className="bg-white p-8 rounded-lg shadow-sm">
            <h2 className="text-2xl font-semibold mb-4">Step 2: Upload Group Photos</h2>
            <p className="text-gray-600 mb-6">Now upload the photos you want to sort.</p>
            <form onSubmit={handleGroupSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Group Photos
                </label>
                <input 
                  type="file" 
                  id="group" 
                  multiple 
                  required 
                  className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  accept="image/*"
                />
              </div>
              <button 
                type="submit" 
                disabled={isLoading}
                className={`w-full py-3 px-4 rounded-md text-white font-medium ${
                  isLoading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isLoading ? 'Processing...' : 'Upload & Sort Photos'}
              </button>
            </form>
          </div>
        )}

        {/* Processing State */}
        {currentStep === 'processing' && (
          <div className="bg-white p-8 rounded-lg shadow-sm text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h2 className="text-2xl font-semibold mb-2">Processing Photos</h2>
            <p className="text-gray-600">Please wait while we sort your photos...</p>
          </div>
        )}

        {/* Complete State */}
        {currentStep === 'complete' && (
          <div className="bg-white p-8 rounded-lg shadow-sm text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <h2 className="text-2xl font-semibold mb-2">Success!</h2>
            <p className="text-gray-600 mb-6">Your photos have been sorted successfully.</p>
            <button 
              onClick={resetProcess}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-md"
            >
              Start New Sort
            </button>
          </div>
        )}

        {/* Error Messages */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600">{error}</p>
          </div>
        )}
        {debugInfo && (
          <p className="mt-4 text-gray-500 text-sm">{debugInfo}</p>
        )}
      </div>
    </main>
  );
}
