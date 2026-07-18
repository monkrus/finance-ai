import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { apiClient } from '@/services/api';
import { useAuthStore } from '@/store/auth';

const mock = new MockAdapter(apiClient);
const axiosMock = new MockAdapter(axios); // for the direct axios.post call in refresh

describe('API Interceptors - Auth', () => {
  beforeEach(() => {
    mock.reset();
    axiosMock.reset();
    useAuthStore.setState({
      user: { id: 1, email: 'test@test.com', role: 'USER', isEmailVerified: true, firstName: 'T', lastName: 'T', createdAt: '' },
      accessToken: 'old-token',
      isAuthenticated: true,
    });
  });

  it('attaches authorization header', async () => {
    mock.onGet('/test').reply(200);
    const response = await apiClient.get('/test');
    expect(response.config.headers.Authorization).toBe('Bearer old-token');
  });

  it('handles 401 and refreshes token successfully', async () => {
    // 1. Initial request fails with 401
    mock.onGet('/protected').replyOnce(401);
    
    // 2. Refresh endpoint succeeds
    axiosMock.onPost('http://localhost:8000/api/v1/auth/refresh').reply(200, {
      access_token: 'new-token'
    });

    // 3. Retry succeeds
    mock.onGet('/protected').replyOnce(200, { data: 'success' });

    const response = await apiClient.get('/protected');
    
    expect(response.data).toEqual({ data: 'success' });
    expect(useAuthStore.getState().accessToken).toBe('new-token');
  });

  it('logs out if refresh fails', async () => {
    // 1. Initial request fails with 401
    mock.onGet('/protected').replyOnce(401);
    
    // 2. Refresh endpoint fails
    axiosMock.onPost('http://localhost:8000/api/v1/auth/refresh').reply(401);

    await expect(apiClient.get('/protected')).rejects.toThrow();
    
    // 3. Should be logged out
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().accessToken).toBeNull();
  });

  it('queues requests while refreshing and resolves them after refresh succeeds', async () => {
    // 1. Setup delayed refresh response so we can queue another request
    mock.onGet('/protected1').replyOnce(401);
    mock.onGet('/protected2').replyOnce(401);
    
    axiosMock.onPost('http://localhost:8000/api/v1/auth/refresh').reply(() => {
      return new Promise((resolve) => {
        setTimeout(() => resolve([200, { access_token: 'new-token-2' }]), 100);
      });
    });

    mock.onGet('/protected1').replyOnce(200, { data: 'success1' });
    mock.onGet('/protected2').replyOnce(200, { data: 'success2' });

    // Fire both requests. The first triggers refresh, the second gets queued.
    const p1 = apiClient.get('/protected1');
    const p2 = apiClient.get('/protected2');
    
    const [res1, res2] = await Promise.all([p1, p2]);
    
    expect(res1.data).toEqual({ data: 'success1' });
    expect(res2.data).toEqual({ data: 'success2' });
    expect(useAuthStore.getState().accessToken).toBe('new-token-2');
  });

  it('queues requests while refreshing and rejects them if refresh fails', async () => {
    mock.onGet('/protected3').replyOnce(401);
    mock.onGet('/protected4').replyOnce(401);
    
    axiosMock.onPost('http://localhost:8000/api/v1/auth/refresh').reply(() => {
      return new Promise((resolve) => {
        setTimeout(() => resolve([401]), 100);
      });
    });

    const p1 = apiClient.get('/protected3');
    const p2 = apiClient.get('/protected4');

    await expect(p1).rejects.toThrow();
    await expect(p2).rejects.toThrow();
  });
});
