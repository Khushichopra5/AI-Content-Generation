export type GuestSessionPayload = {
  guest_id: string;
  session_id: string;
  device_id: string;
  status: string;
  preferences: Record<string, unknown>;
  last_seen_at: string;
  expires_at: string;
};

export type GuestBootstrapResponse = {
  session: GuestSessionPayload;
  limits: {
    brands_used: number;
    templates_used: number;
    generations_used: number;
    brands_soft_limit: number;
    templates_soft_limit: number;
    generations_soft_limit: number;
  };
  capabilities: {
    guest_first: boolean;
    auth_optional: boolean;
  };
};

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type BrandProfile = {
  id: string;
  brand_name: string;
  brand_voice: string;
  banned_phrases: string[];
  preferred_tone: string;
  example_copy: string;
  product_description: string;
  target_audience: string;
  created_at: string;
  updated_at: string;
};

export type ContentTemplate = {
  id: string;
  name: string;
  channel: string;
  objective: string;
  prompt_template: string;
  created_at: string;
  updated_at: string;
};

export type GenerationJob = {
  id: string;
  brand_profile_id: string;
  template_id: string | null;
  status: string;
  model_name: string;
  output_payload: Record<string, unknown>;
  error_message: string;
  cache_hit: boolean;
  include_image: boolean;
  assets: Array<{
    id: string;
    asset_type: string;
    storage_url: string;
    mime_type: string;
    metadata: Record<string, unknown>;
    created_at: string;
  }>;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

export type GenerationSubmissionResponse = {
  job_id: string;
  status: string;
  cache_hit: boolean;
  deduplicated: boolean;
};

export type UsageEvent = {
  id: string;
  event_type: string;
  tokens_in: number;
  tokens_out: number;
  latency_ms: number;
  cache_hit: boolean;
  created_at: string;
  metadata: Record<string, unknown>;
};
