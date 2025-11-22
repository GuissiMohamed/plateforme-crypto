import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("token", token);
  } else {
    delete api.defaults.headers.common["Authorization"];
    localStorage.removeItem("token");
  }
}

const savedToken = localStorage.getItem("token");
if (savedToken) setAuthToken(savedToken);
