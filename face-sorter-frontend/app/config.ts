export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  endpoints: {
    upload: '/upload',
    registerFaces: '/register_faces',
  },
} as const;

export const getApiUrl = (endpoint: keyof typeof API_CONFIG.endpoints) => {
  return `${API_CONFIG.baseUrl}${API_CONFIG.endpoints[endpoint]}`;
}; 