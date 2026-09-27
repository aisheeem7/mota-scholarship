import type {
  Application,
  CreateApplicationRequest,
  Document,
  DocumentType,
  ValidationResult,
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
    // Fall through to the generic HTTP error below.
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

export async function createApplication(
  payload: CreateApplicationRequest,
): Promise<Application> {
  return apiPost<Application>(
    "/api/v1/applications",
    payload,
  );
}

export async function getApplication(
  applicationId: string,
): Promise<Application> {
  return apiGet<Application>(
    `/api/v1/applications/${applicationId}`,
  );
}

export async function processApplication(
  applicationId: string,
): Promise<Application> {
  return apiPost<Application>(
    `/api/v1/applications/${applicationId}/process`,
    {},
  );
}

export async function getApplicationValidations(
  applicationId: string,
): Promise<ValidationResult[]> {
  return apiGet<ValidationResult[]>(
    `/api/v1/applications/${applicationId}/validations`,
  );
}

export async function getAdminApplications(): Promise<Application[]> {
  return apiGet<Application[]>(
    "/api/v1/admin/applications",
  );
}

export async function uploadApplicationDocument(
  applicationId: string,
  documentType: DocumentType,
  file: File,
): Promise<Document> {
  const formData = new FormData();

  formData.append("document_type", documentType);
  formData.append("file", file);

  const response = await fetch(
    `${API_URL}/api/v1/applications/${applicationId}/documents`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json() as Promise<Document>;
}