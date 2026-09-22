/**
 * MoTA Scholarship System
 * Frontend API/domain types
 *
 * IMPORTANT:
 * These types mirror the current Day 2 backend API contract.
 * Do not introduce frontend-only enums for backend-controlled values.
 */

/* -------------------------------------------------------------------------- */
/* Scheme                                                                      */
/* -------------------------------------------------------------------------- */

export type SchemeId =
  | "PRE_MATRIC"
  | "POST_MATRIC"
  | "TOP_CLASS"
  | "NATIONAL_FELLOWSHIP"
  | "NATIONAL_OVERSEAS";

/**
 * User-facing labels are presentation concerns.
 * API/database values must always use SchemeId.
 */
export const SCHEME_LABELS: Record<SchemeId, string> = {
  PRE_MATRIC: "Pre-Matric Scholarship",
  POST_MATRIC: "Post-Matric Scholarship",
  TOP_CLASS: "National Scholarship Scheme - Top Class",
  NATIONAL_FELLOWSHIP: "National Fellowship Scheme",
  NATIONAL_OVERSEAS: "National Overseas Scholarship",
};

/* -------------------------------------------------------------------------- */
/* Application                                                                 */
/* -------------------------------------------------------------------------- */

export type ApplicationStatus =
  | "SUBMITTED"
  | "PROCESSING"
  | "APPROVED"
  | "DEFICIENT"
  | "RESUBMITTED"
  | "FLAGGED_FOR_REVIEW"
  | "REJECTED";

export interface Application {
  id: string;
  student_id: string;
  scheme_id: SchemeId;
  status: ApplicationStatus;
  risk_score: number | null;
  created_at: string;
  updated_at: string;
}

/**
 * Request body for:
 * POST /api/v1/applications
 */
export interface CreateApplicationRequest {
  student_id: string;
  scheme_id: SchemeId;
}

/* -------------------------------------------------------------------------- */
/* Documents                                                                  */
/* -------------------------------------------------------------------------- */

export type OcrStatus =
  | "PROCESSING"
  | "READABLE"
  | "UNREADABLE"
  | "PARTIALLY_READABLE";

export interface Document {
  id: string;
  application_id: string;
  document_type: string;
  ocr_status: OcrStatus;
}

/**
 * NOTE:
 * The exact document_type values and upload request/response contract
 * are still pending backend confirmation.
 *
 * Do not add guessed document types here yet.
 */

/* -------------------------------------------------------------------------- */
/* Validation                                                                 */
/* -------------------------------------------------------------------------- */

export type ValidationSeverity =
  | "NONE"
  | "LOW"
  | "MEDIUM"
  | "HIGH";

export interface ValidationResult {
  passed: boolean | null;
  rule_id: string;
  rule_name: string;
  extracted_value: string | null;
  expected_condition: string | null;
  reasoning: string | null;
  severity: ValidationSeverity;
}

/**
 * IMPORTANT:
 *
 * The current backend/DB contract does NOT define:
 * - NOT_EVALUABLE as a separate state
 * - validation.document_id
 *
 * Therefore the frontend must not invent either field.
 */

/* -------------------------------------------------------------------------- */
/* API Errors                                                                 */
/* -------------------------------------------------------------------------- */

export interface ApiError {
  detail: string;
}

/* -------------------------------------------------------------------------- */
/* Generic API State Helpers                                                  */
/* -------------------------------------------------------------------------- */

export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

/* -------------------------------------------------------------------------- */
/* Application UI Helpers                                                     */
/* -------------------------------------------------------------------------- */

/**
 * User-facing status labels.
 * These do NOT replace ApplicationStatus in API payloads.
 */
export const APPLICATION_STATUS_LABELS: Record<
  ApplicationStatus,
  string
> = {
  SUBMITTED: "Submitted",
  PROCESSING: "Processing",
  APPROVED: "Approved",
  DEFICIENT: "Deficient",
  RESUBMITTED: "Resubmitted",
  FLAGGED_FOR_REVIEW: "Flagged for Review",
  REJECTED: "Rejected",
};

/**
 * OCR status labels.
 */
export const OCR_STATUS_LABELS: Record<OcrStatus, string> = {
  PROCESSING: "Processing",
  READABLE: "Readable",
  UNREADABLE: "Unreadable",
  PARTIALLY_READABLE: "Partially Readable",
};

/**
 * Validation severity labels.
 */
export const VALIDATION_SEVERITY_LABELS: Record<
  ValidationSeverity,
  string
> = {
  NONE: "None",
  LOW: "Low",
  MEDIUM: "Medium",
  HIGH: "High",
};

/* -------------------------------------------------------------------------- */
/* Type Guards                                                                */
/* -------------------------------------------------------------------------- */

export function isSchemeId(value: string): value is SchemeId {
  return (
    value === "PRE_MATRIC" ||
    value === "POST_MATRIC" ||
    value === "TOP_CLASS" ||
    value === "NATIONAL_FELLOWSHIP" ||
    value === "NATIONAL_OVERSEAS"
  );
}

export function isApplicationStatus(
  value: string,
): value is ApplicationStatus {
  return (
    value === "SUBMITTED" ||
    value === "PROCESSING" ||
    value === "APPROVED" ||
    value === "DEFICIENT" ||
    value === "RESUBMITTED" ||
    value === "FLAGGED_FOR_REVIEW" ||
    value === "REJECTED"
  );
}

export function isOcrStatus(value: string): value is OcrStatus {
  return (
    value === "PROCESSING" ||
    value === "READABLE" ||
    value === "UNREADABLE" ||
    value === "PARTIALLY_READABLE"
  );
}

export function isValidationSeverity(
  value: string,
): value is ValidationSeverity {
  return (
    value === "NONE" ||
    value === "LOW" ||
    value === "MEDIUM" ||
    value === "HIGH"
  );
}

/* -------------------------------------------------------------------------- */
/* UI Status Helpers                                                          */
/* -------------------------------------------------------------------------- */

/**
 * Maps backend application status to a stable UI category.
 *
 * Keep the backend status as the source of truth.
 * This mapping is presentation-only.
 */
export type ApplicationStatusTone =
  | "neutral"
  | "processing"
  | "success"
  | "warning"
  | "danger";

export const APPLICATION_STATUS_TONES: Record<
  ApplicationStatus,
  ApplicationStatusTone
> = {
  SUBMITTED: "neutral",
  PROCESSING: "processing",
  APPROVED: "success",
  DEFICIENT: "warning",
  RESUBMITTED: "neutral",
  FLAGGED_FOR_REVIEW: "danger",
  REJECTED: "danger",
};
