// api.js — Centralised API client for ReturnShield AI backend
import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const client = axios.create({
  baseURL: BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

export const api = {
  health:          () => client.get('/api/health'),
  dashboardOverview: () => client.get('/api/dashboard/overview'),
  metrics:         () => client.get('/api/metrics'),
  thresholds:      () => client.get('/api/metrics/thresholds'),
  returns:         (skip = 0, limit = 100) => client.get(`/api/returns?skip=${skip}&limit=${limit}`),
  getReturn:       (id) => client.get(`/api/returns/${id}`),
  customers:       (skip = 0, limit = 50) => client.get(`/api/customers?skip=${skip}&limit=${limit}`),
  getCustomer:     (id) => client.get(`/api/customers/${id}`),
  investigations:  (skip = 0, limit = 50) => client.get(`/api/investigations?skip=${skip}&limit=${limit}`),
  getInvestigation:(id) => client.get(`/api/investigations/${id}`),
  scoreRisk:       (customer_id, return_id) => client.post('/api/risk/score', { customer_id, return_id }),
  aiSummary:       (case_id) => client.post(`/api/investigations/${case_id}/ai-summary`),
  approveReturn:   (return_id, performed_by, notes) => client.post(`/api/returns/${return_id}/approve`, { performed_by, notes }),
  verifyReturn:    (return_id, performed_by, notes) => client.post(`/api/returns/${return_id}/verify`, { performed_by, notes }),
  manualReview:    (return_id, performed_by, notes) => client.post(`/api/returns/${return_id}/manual-review`, { performed_by, notes }),
};

export default api;
