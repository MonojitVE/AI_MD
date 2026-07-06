import os

def rewrite_auth_js():
    content = """import api from './client';

export const login = async (employee_id, password) => {
  const response = await api.post('/api/auth/login', { employee_id, password });
  return response.data;
};

export const verify = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/api/auth/logout');
  return response.data;
};
"""
    with open(r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\api\auth.js", "w") as f:
        f.write(content)

def rewrite_useauthstore():
    content = """import { create } from 'zustand';
import { login as apiLogin, verify as apiVerify, logout as apiLogout } from '../api/auth';
import api from '../api/client';

const TOKEN_KEY = 'sentry_fab_admin_token';

const useAuthStore = create((set, get) => ({
  user: null,
  isAdmin: false,
  token: localStorage.getItem(TOKEN_KEY) || null,
  loading: false,
  error: null,

  login: async (employeeId, password) => {
    set({ loading: true, error: null });
    try {
      const data = await apiLogin(employeeId, password);
      localStorage.setItem(TOKEN_KEY, data.access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      
      const user = await apiVerify();
      set({ user, isAdmin: user.role === 'admin', token: data.access_token, loading: false });
      return data;
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      set({ loading: false, error: message });
      throw new Error(message);
    }
  },

  checkAuth: async () => {
    const token = get().token;
    if (!token) {
      set({ user: null, isAdmin: false });
      return;
    }
    try {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const user = await apiVerify();
      set({ user, isAdmin: user.role === 'admin' });
    } catch {
      localStorage.removeItem(TOKEN_KEY);
      delete api.defaults.headers.common['Authorization'];
      set({ user: null, isAdmin: false, token: null });
    }
  },

  logout: async () => {
    try {
      await apiLogout();
    } catch {}
    localStorage.removeItem(TOKEN_KEY);
    delete api.defaults.headers.common['Authorization'];
    set({ user: null, isAdmin: false, token: null, error: null });
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;
"""
    with open(r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\store\useAuthStore.js", "w") as f:
        f.write(content)

def patch_adminlogin():
    path = r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\pages\AdminLogin.jsx"
    with open(path, "r") as f:
        content = f.read()

    content = content.replace("const [password, setPassword] = useState('');", 
                              "const [employeeId, setEmployeeId] = useState('');\n  const [password, setPassword] = useState('');")
    
    content = content.replace("await login(password);", "await login(employeeId, password);")
    content = content.replace("disabled={loading || !password.trim()}", "disabled={loading || !password.trim() || !employeeId.trim()}")
    
    content = content.replace("Admin <span style={{ color: 'var(--color-accent-lime)' }}>Access</span>", 
                              "System <span style={{ color: 'var(--color-accent-lime)' }}>Access</span>")
                              
    content = content.replace("Enter the admin password to unlock data management,<br />", 
                              "Enter your Employee ID and password to access<br />")
    content = content.replace("upload tools, and system settings.", "the Sentry Fab Dashboard.")
    
    # Add employee ID input
    new_input = """<div className="admin-input-group" style={{ marginBottom: '16px' }}>
            <label htmlFor="employee-id">Employee ID</label>
            <input
              id="employee-id"
              ref={inputRef}
              type="text"
              className="admin-input"
              placeholder="e.g. EMP001"
              value={employeeId}
              onChange={(e) => {
                setEmployeeId(e.target.value);
                if (error) clearError();
              }}
            />
          </div>"""
          
    content = content.replace('<div className="admin-input-group">', new_input + '\n\n          <div className="admin-input-group">')
    # fix the focus ref since we want it on employeeId
    content = content.replace('ref={inputRef}\n              type="password"', 'type="password"')

    with open(path, "w") as f:
        f.write(content)

def patch_sidebar():
    path = r"c:\TEST_CODES\GITHUB\AI_MD\frontend\src\components\layout\Sidebar.jsx"
    with open(path, "r") as f:
        content = f.read()
        
    content = content.replace("{isAdmin ? 'Logout Admin' : 'Admin Login'}", "{isAdmin ? 'Logout Admin' : 'Login'}")
    
    with open(path, "w") as f:
        f.write(content)

if __name__ == "__main__":
    rewrite_auth_js()
    rewrite_useauthstore()
    patch_adminlogin()
    patch_sidebar()
    print("Frontend Auth patched.")
