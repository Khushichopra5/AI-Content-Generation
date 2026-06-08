import { API_BASE_URL, STORAGE_KEYS } from "@/lib/config";
import { useAppStore } from "@/lib/store";
import type {
  BrandProfile,
  ContentTemplate,
  GenerationJob,
  GenerationSubmissionResponse,
  GuestBootstrapResponse,
  PaginatedResponse,
  UsageEvent
} from "@/lib/types";

function loadGuestHeaders() {
  if (typeof window === "undefined") {
    return {} as Record<string, string>;
  }
  const raw = window.localStorage.getItem(STORAGE_KEYS.guestSession);
  if (!raw) {
    return {} as Record<string, string>;
  }
  const parsed = JSON.parse(raw) as GuestBootstrapResponse;
  return {
    "X-Guest-Id": parsed.session.guest_id,
    "X-Session-Id": parsed.session.session_id,
    "X-Device-Id": parsed.session.device_id
  };
}

async function parseResponse<T>(response: Response): Promise<T> {
  const json = await response.json().catch(() => ({}));
  useAppStore.getState().setLastResponse({
    label: `${response.status} ${response.url}`,
    payload: json
  });
  if (!response.ok) {
    throw new Error(
      typeof json === "object" && json && "detail" in json
        ? String((json as { detail: unknown }).detail)
        : `Request failed with ${response.status}`
    );
  }
  return json as T;
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body) {
    headers.set("Content-Type", "application/json");
  }
  for (const [key, value] of Object.entries(loadGuestHeaders())) {
    headers.set(key, value);
  }

  const requestInit: RequestInit = {
    ...init,
    headers
  };
  useAppStore.getState().setLastRequest({
    label: `${init?.method ?? "GET"} ${path}`,
    payload: init?.body ? JSON.parse(String(init.body)) : null
  });
  const response = await fetch(`${API_BASE_URL}${path}`, requestInit);
  return parseResponse<T>(response);
}

export const guestApi = {
  bootstrap: (payload?: Partial<GuestBootstrapResponse["session"]>) =>
    apiRequest<GuestBootstrapResponse>("/api/v1/guest/bootstrap/", {
      method: "POST",
      body: JSON.stringify(payload ?? {})
    })
};

export const platformApi = {
  health: () =>
    apiRequest<{ status: string; database: boolean; redis: boolean; debug: boolean }>("/api/health"),
  brands: {
    list: async () => apiRequest<PaginatedResponse<BrandProfile>>("/api/v1/brands/"),
    create: async (payload: Omit<BrandProfile, "id" | "created_at" | "updated_at">) =>
      apiRequest<BrandProfile>("/api/v1/brands/", {
        method: "POST",
        body: JSON.stringify(payload)
      })
  },
  templates: {
    list: async () => apiRequest<PaginatedResponse<ContentTemplate>>("/api/v1/templates/"),
    create: async (
      payload: Omit<ContentTemplate, "id" | "created_at" | "updated_at">
    ) =>
      apiRequest<ContentTemplate>("/api/v1/templates/", {
        method: "POST",
        body: JSON.stringify(payload)
      })
  },
  jobs: {
    list: async () => apiRequest<PaginatedResponse<GenerationJob>>("/api/v1/jobs/"),
    detail: async (jobId: string) => apiRequest<GenerationJob>(`/api/v1/jobs/${jobId}/`),
    regenerate: async (jobId: string) =>
      apiRequest<GenerationSubmissionResponse>(`/api/v1/regenerate/${jobId}/`, {
        method: "POST",
        body: JSON.stringify({})
      })
  },
  usage: {
    list: async () => apiRequest<PaginatedResponse<UsageEvent>>("/api/v1/usage/")
  },
  generate: async (payload: Record<string, unknown>) =>
    apiRequest<GenerationSubmissionResponse>("/api/v1/generate/", {
      method: "POST",
      body: JSON.stringify(payload)
    })
};
