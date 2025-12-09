const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const ACCESS_KEY = 'accessToken';
const REFRESH_KEY = 'refreshToken';
const USER_KEY = 'username';
const STAFF_KEY = 'isStaff';

export const getAccessToken = () => localStorage.getItem(ACCESS_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_KEY);
export const getUsername = () => localStorage.getItem(USER_KEY);

export const setSession = ({ access, refresh, username, isStaff }) => {
  if (access) localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  if (username) localStorage.setItem(USER_KEY, username);
  if (typeof isStaff === 'boolean') localStorage.setItem(STAFF_KEY, String(isStaff));
};

export const clearSession = () => {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(STAFF_KEY);
};
export const getIsStaff = () => localStorage.getItem(STAFF_KEY) === 'true';

const parseError = async (response) => {
  try {
    const data = await response.json();
    if (data?.detail) return data.detail;
    return JSON.stringify(data);
  } catch (e) {
    return response.statusText || 'Request failed';
  }
};

const refreshAccessToken = async () => {
  const refresh = getRefreshToken();
  if (!refresh) return null;
  const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) return null;
  const data = await res.json();
  if (data?.access) {
    setSession({ access: data.access });
    return data.access;
  }
  return null;
};

export const request = async (path, { method = 'GET', body, headers = {} } = {}) => {
  const token = getAccessToken();
  const buildHeaders = (authToken) => ({
    'Content-Type': 'application/json',
    ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    ...headers,
  });
  const doFetch = async (authToken) =>
    fetch(`${API_BASE}${path}`, {
      method,
      headers: buildHeaders(authToken),
      body: body ? JSON.stringify(body) : undefined,
    });

  let response = await doFetch(token);

  if (response.status === 401 && getRefreshToken()) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      response = await doFetch(refreshed);
    } else {
      clearSession();
    }
  }

  if (response.status === 401) {
    // clear stale tokens and retry once without auth for public endpoints
    clearSession();
    const fallback = await doFetch(null);
    if (fallback.ok) {
      return fallback.status === 204 ? null : fallback.json();
    }
    response = fallback;
  }

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  if (response.status === 204) return null;
  return response.json();
};

export { API_BASE };
