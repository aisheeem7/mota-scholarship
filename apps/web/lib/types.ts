export type ApplicationStatus =
  | "SUBMITTED"
  | "PROCESSING"
  | "APPROVED"
  | "DEFICIENT"
  | "RESUBMITTED"
  | "FLAGGED_FOR_REVIEW";

export interface HealthResponse {
  status: string;
  service: string;
}

export interface Application {
  id: string;
  student_name: string;
  scheme_id: string;
  status: ApplicationStatus;
  risk_score?: number;
  created_at?: string;
  updated_at?: string;
}

export interface ValidationResult {
  passed: boolean;
  rule_id: string;
  rule_name: string;
  extracted_value?: string;
  expected_condition: string;
  reasoning: string;
  severity: string;
}