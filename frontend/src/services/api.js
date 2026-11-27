const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = Array.isArray(payload.detail) ? payload.detail[0]?.msg : payload.detail;
    throw new Error(detail || "Something went wrong. Please try again.");
  }
  return response.status === 204 ? null : response.json();
}

export const api = {
  register: (body) => request("/auth/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  login: (body) => request("/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  me: (token) => request("/users/me", { headers: { Authorization: `Bearer ${token}` } }),
  updateProfile: (token, body) => request("/users/me", { method: "PUT", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(body) }),
  workouts: (token) => request("/workouts", { headers: { Authorization: `Bearer ${token}` } }),
  saveWorkout: (token, body) => request("/workouts", { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(body) }),
  deleteWorkout: (token, workoutId) => request(`/workouts/${workoutId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } }),
  workoutVideo: async (token, workoutId) => {
    const response = await fetch(`${API_URL}/workouts/${workoutId}/video`, { headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || "Could not load the saved video.");
    }
    return URL.createObjectURL(await response.blob());
  },
  analyticsSummary: (token) => request("/analytics/summary", { headers: { Authorization: `Bearer ${token}` } }),
};
