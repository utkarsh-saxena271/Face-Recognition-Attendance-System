/**
 * API client — centralised fetch wrapper with JWT injection.
 */

const API_BASE = import.meta.env.VITE_API_URL || "https://face-attendance-backend-os6u.onrender.com";

function getToken() {
  return localStorage.getItem("token");
}

async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const error = new Error(data.message || "Something went wrong");
    error.status = res.status;
    error.data = data;
    throw error;
  }

  return data;
}

/* ─── Auth ────────────────────────────────────────────────────── */

export function signup(name, email, password, role) {
  return request("/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password, role }),
  });
}

export function login(email, password) {
  return request("/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function getMe() {
  return request("/me");
}

/* ─── Groups ──────────────────────────────────────────────────── */

export function getGroups() {
  return request("/groups");
}

export function createGroup(name) {
  return request("/groups", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export function updateGroup(id, name) {
  return request(`/groups/${id}`, {
    method: "PUT",
    body: JSON.stringify({ name }),
  });
}

export function deleteGroup(id) {
  return request(`/groups/${id}`, { method: "DELETE" });
}

export function getGroupStudents(groupId) {
  return request(`/groups/${groupId}/students`);
}

export function addStudentToGroup(groupId, email) {
  return request(`/groups/${groupId}/add-student`, {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function removeStudentFromGroup(groupId, studentId) {
  return request(`/groups/${groupId}/remove-student`, {
    method: "DELETE",
    body: JSON.stringify({ student_id: studentId }),
  });
}

/* ─── Face ────────────────────────────────────────────────────── */

export function uploadFace(imageBase64) {
  return request("/upload-face", {
    method: "POST",
    body: JSON.stringify({ image: imageBase64 }),
  });
}

export function recognizeFace(imageBase64, groupId, sessionId) {
  return request("/recognize-face", {
    method: "POST",
    body: JSON.stringify({
      image: imageBase64,
      group_id: groupId,
      session_id: sessionId,
    }),
  });
}

/* ─── Attendance ──────────────────────────────────────────────── */

export function startAttendanceSession(groupId) {
  return request("/attendance/start", {
    method: "POST",
    body: JSON.stringify({ group_id: groupId }),
  });
}

export function endAttendanceSession(sessionId) {
  return request("/attendance/end", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export function getMyAttendance() {
  return request("/attendance/my");
}

export function getStudentAttendance(studentId) {
  return request(`/attendance/student/${studentId}`);
}

export function getGroupAttendance(groupId) {
  return request(`/attendance/group/${groupId}`);
}

export function getSessionAttendance(sessionId) {
  return request(`/attendance/session/${sessionId}`);
}
