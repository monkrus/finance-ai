import { apiClient } from '@/services/api';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

describe('API Service', () => {
  let mock: MockAdapter;

  beforeAll(() => {
    mock = new MockAdapter(apiClient);
  });

  afterEach(() => {
    mock.reset();
    useAuthStore.setState({ accessToken: null, user: null, isAuthenticated: false });
  });

  afterAll(() => {
    mock.restore();
  });

  it('should attach Authorization header when token exists', async () => {
    useAuthStore.setState({ accessToken: 'mock-token' });
    mock.onGet('/test').reply(200, {});

    const response = await apiClient.get('/test');
    
    expect(response.config.headers?.Authorization).toBe('Bearer mock-token');
  });

  it('should not attach Authorization header when token does not exist', async () => {
    mock.onGet('/test').reply(200, {});

    const response = await apiClient.get('/test');
    
    expect(response.config.headers?.Authorization).toBeUndefined();
  });

  it('should logout on 401 error', async () => {
    useAuthStore.setState({ 
      accessToken: 'old-token', 
      isAuthenticated: true
    });
    
    mock.onGet('/test-401').reply(401, {});

    try {
      await apiClient.get('/test-401');
    } catch (e) {
      // Expected to throw
    }
    
    // In our current stub implementation, 401 triggers logout directly
    // Wait for promise rejection chain
    await new Promise(process.nextTick);
    
    // State logout should be called or state reset
    const state = useAuthStore.getState();
    expect(state.accessToken).toBeNull();
  });
});
