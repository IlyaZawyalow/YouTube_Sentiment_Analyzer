import axios from 'axios';

const parsingServiceURL = 'http://localhost:8000';
const mlServiceURL = 'http://localhost:8080';

const parsingServiceAPI = axios.create({
  baseURL: parsingServiceURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const mlServiceAPI = axios.create({
  baseURL: mlServiceURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const parseVideo = async (videoUrl) => {
  try {
    const response = await parsingServiceAPI.post('/parse/', { video_url: videoUrl });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getComments = async (videoId) => {
  try {
    const response = await mlServiceAPI.get(`/ml/${videoId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};
