const API_URL = import.meta.env.VITE_API_URL;

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

export const documentApi = {
  upload(file) {
    const formData = new FormData();
    formData.append("file", file);

    return fetch(`${API_URL}/api/v1/documents/upload-pdf`, {
      method: "POST",
      body: formData,
      credentials: "include",
    }).then(async (response) => {
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      return data;
    });
  },

  getDocuments() {
    return request("/api/v1/documents");
  },

  deleteDocument(documentId) {
    return request(`/api/v1/documents/${documentId}`, {
      method: "DELETE",
    });
  },
};