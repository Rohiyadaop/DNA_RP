import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 120000
});

export async function uploadFastaFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/upload-fasta", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
  return response.data;
}

export async function predictResistance(payload) {
  const response = await api.post("/predict", payload);
  return response.data;
}

export default api;
