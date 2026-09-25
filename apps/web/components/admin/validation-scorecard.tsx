import { Badge } from "@/components/ui/badge";
import {
  VALIDATION_SEVERITY_LABELS,
  type ValidationResult,
} from "@/lib/types";

interface ValidationScorecardProps {
  validations: ValidationResult[];
}

function passedLabel(passed: boolean | null): string {
  if (passed === true) return "Passed";
  if (passed === false) return "Not passed";
  return "Not evaluable — required evidence is missing or unreadable.";
}

export function ValidationScorecard({
  validations,
}: ValidationScorecardProps) {
  if (validations.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No validation results available.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {validations.map((validation) => (
        <article
          key={validation.rule_id}
          className="rounded-lg border p-4"
        >
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h3 className="font-medium">{validation.rule_name}</h3>
              <p className="mt-1 text-xs text-muted-foreground">
                Rule ID: {validation.rule_id}
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary">
                {VALIDATION_SEVERITY_LABELS[validation.severity]}
              </Badge>
              <Badge variant="outline">
                {passedLabel(validation.passed)}
              </Badge>
            </div>
          </div>

          <dl className="mt-4 grid gap-4 sm:grid-cols-3">
            <div>
              <dt className="text-xs font-medium text-muted-foreground">
                Extracted value
              </dt>
              <dd className="mt-1 text-sm">
                {validation.extracted_value ?? "Not available"}
              </dd>
            </div>

            <div>
              <dt className="text-xs font-medium text-muted-foreground">
                Expected condition
              </dt>
              <dd className="mt-1 text-sm">
                {validation.expected_condition ?? "Not available"}
              </dd>
            </div>

            <div>
              <dt className="text-xs font-medium text-muted-foreground">
                Result
              </dt>
              <dd className="mt-1 text-sm">
                {passedLabel(validation.passed)}
              </dd>
            </div>
          </dl>

          <div className="mt-4">
            <p className="text-xs font-medium text-muted-foreground">
              Reasoning
            </p>
            <p className="mt-1 text-sm">
              {validation.reasoning ?? "No reasoning available."}
            </p>
          </div>
        </article>
      ))}
    </div>
  );
}
