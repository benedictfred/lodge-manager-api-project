import axios from "axios";

const baseURL =
  import.meta.env.VITE_BASE_API_URL ?? "http://localhost:8000/api/v1";

export const axiosInstance = axios.create({
  baseURL,
  withCredentials: true,
});
