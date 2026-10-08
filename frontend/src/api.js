const API_URL = "http://localhost:8000";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong");
  }

  return data;
}

export const authApi = {
  login() {
    window.location.href = `${API_URL}/auth/login`;
  },

  logout() {
    return request("/auth/logout");
  },

  getCurrentUser() {
    return request("/auth/me");
  },
};