import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface IndexRecord {
  index_date: string;
  index_value: number;
  base_period: string;
  daily_inflation_rate: number | null;
  formula_used: string;
  computed_at: string;
}

export interface ElasticityMetric {
  advance_window: string;
  avg_base_fare: number;
  avg_fuel_surcharge: number;
  avg_taxes: number;
  avg_convenience_fee: number;
  avg_total_fare: number;
  sample_count: number;
}

export interface RouteBreakdown {
  route_id: string;
  origin_city: string;
  destination_city: string;
  dgca_passenger_weight: number;
  avg_total_fare: number;
  min_fare: number;
  max_fare: number;
  quote_count: number;
}

export const fetchLatestIndex = async (): Promise<IndexRecord> => {
  const { data } = await apiClient.get('/index/latest');
  return data;
};

export const fetchElasticity = async (): Promise<ElasticityMetric[]> => {
  const { data } = await apiClient.get('/analytics/elasticity');
  return data;
};

export const fetchRoutes = async (): Promise<RouteBreakdown[]> => {
  const { data } = await apiClient.get('/analytics/routes');
  return data;
};

export interface BenchmarkPoint {
  index_date: string;
  apix_value: number;
  mospi_proxy_value: number;
}

export const fetchBenchmark = async (): Promise<BenchmarkPoint[]> => {
  const { data } = await apiClient.get('/analytics/benchmark');
  return data;
};