import { computed, reactive, readonly } from 'vue';
import { clearSession, getUsername, getIsStaff, request, setSession } from '../api';

const state = reactive({
  username: getUsername() || '',
  isAuthenticated: !!getUsername(),
  isStaff: getIsStaff(),
  loading: false,
  error: '',
});

const setError = (message) => {
  state.error = message || '';
};

export const useAuth = () => {
  const fetchProfile = async () => {
    try {
      const profile = await request('/auth/me/');
      state.isStaff = !!profile?.is_staff;
      setSession({ isStaff: state.isStaff });
    } catch (err) {
      // ignore if unauthorized
      state.isStaff = false;
    }
  };

  const login = async (username, password) => {
    state.loading = true;
    setError('');
    try {
      const data = await request('/auth/token/', {
        method: 'POST',
        body: { username, password },
      });
      setSession({ access: data.access, refresh: data.refresh, username });
      state.username = username;
      state.isAuthenticated = true;
      await fetchProfile();
    } catch (err) {
      setError(err.message);
      state.isAuthenticated = false;
    } finally {
      state.loading = false;
    }
  };

  const register = async ({ username, email, password }) => {
    state.loading = true;
    setError('');
    try {
      await request('/register/', {
        method: 'POST',
        body: { username, email, password },
      });
      await login(username, password);
    } catch (err) {
      setError(err.message);
    } finally {
      state.loading = false;
    }
  };

  const logout = () => {
    clearSession();
    state.username = '';
    state.isAuthenticated = false;
    state.isStaff = false;
  };

  return {
    state: readonly(state),
    isAuthenticated: computed(() => state.isAuthenticated),
    isStaff: computed(() => state.isStaff),
    loading: computed(() => state.loading),
    error: computed(() => state.error),
    login,
    logout,
    register,
    fetchProfile,
  };
};
