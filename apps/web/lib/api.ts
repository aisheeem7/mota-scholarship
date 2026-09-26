import type {
  Application,
  CreateApplicationRequest,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ApiErrorResponse {
  detail?: string;
}

async function parseError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as ApiErrorResponse;

    if (body.detail) {
      return body.detail;
    }
  } catch {
    // Ignore invalid/non-JSON error responses.
  }

  return `API request failed: ${response.status}`;
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "GET",
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json() as Promise<T>;
}

export async function apiPost<T>(
  path: string,
  body: unknown,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json() as Promise<T>;
}

/* -------------------------------------------------------------------------- */
/* Application API                                                            */
/* -------------------------------------------------------------------------- */

/**
 * POST /api/v1/applications
 */
export async function createApplication(
  payload: CreateApplicationRequest,
): Promise<Application> {
  return apiPost<Application>(
    "/api/v1/applications",
    payload,
  );
}

/**
 * GET /api/v1/applications/{application_id}
 */
export async function getApplication(
  applicationId: string,
): Promise<Application> {
  return apiGet<Application>(
    `/api/v1/applications/${applicationId}`,
  );
}

/**
 * GET /api/v1/admin/applications
 *
 * Uses the shared Application contract. No frontend-only application type.
 */
export async function getAdminApplications(): Promise<Application[]> {
  return apiGet<Application[]>("/api/v1/admin/applications");
}