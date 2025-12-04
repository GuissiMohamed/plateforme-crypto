import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// 🔐 Gestion du token JWT
export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("token", token);
  } else {
    delete api.defaults.headers.common["Authorization"];
    localStorage.removeItem("token");
  }
}

// 🔄 Recharger le token si présent dans le localStorage
const savedToken = localStorage.getItem("token");
if (savedToken) setAuthToken(savedToken);

// ================================
// 💡 FONCTION SPÉCIALE POUR LE LOGIN
// ================================

export async function loginRequest(email: string, password: string) {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);

  return api.post("/auth/login", form, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
}
