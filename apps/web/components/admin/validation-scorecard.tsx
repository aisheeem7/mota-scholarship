import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/components/layout/language-provider";
import type { TranslationKey } from "@/lib/i18n";
import {
  type ValidationResult,
} from "@/lib/types";

interface ValidationScorecardProps {
  validations: ValidationResult[];
}

function passedLabel(passed: boolean | null, t: (key: TranslationKey) => string): string {
  if (passed === true) {
    return t("passed");
  }

  if (passed === false) {
    return t("notPassed");
  }

  return t("notAvailable");
}

function severityLabel(
  severity: ValidationResult["severity"],
  t: (key: TranslationKey) => string,
): string {
  if (severity === null) {
    return t("notAvailable");
  }

  const keys: Record<Exclude<ValidationResult["severity"], null>, TranslationKey> = {
    NONE: "none", LOW: "low", MEDIUM: "medium", HIGH: "high",
  };

  return t(keys[severity]);
}

export function ValidationScorecard({
  validations,
}: ValidationScorecardProps) {
  const { t } = useLanguage();

  if (validations.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        {t("noValidation")}
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
              <h3 className="font-medium">
                {validation.rule_name}
              </h3>

              <p className="mt-1 text-xs text-muted-foreground">
                Rule ID: {validation.rule_id}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-muted-foreground">
                  {t("severity")}:
                </span>

                <Badge variant="secondary">
                  {severityLabel(validation.severity, t)}
                </Badge>
              </div>

              <div className="flex items-center gap-1.5">
                <span className="text-xs text-muted-foreground">
                  {t("result")}:
                </span>

                <Badge variant="outline">
                  {passedLabel(validation.passed, t)}
                </Badge>
              </div>
            </div>
          </div>

          <dl className="mt-4 grid gap-4 sm:grid-cols-3">
            <div>
              <dt className="text-xs font-medium text-muted-foreground">
                {t("extractedValue")}
              </dt>

              <dd className="mt-1 text-sm">
                {validation.extracted_value ??
                  t("notAvailable")}
              </dd>
            </div>

            <div>
              <dt className="text-xs font-medium text-muted-foreground">
                {t("expectedCondition")}
              </dt>

              <dd className="mt-1 text-sm">
                {validation.expected_condition ??
                  t("notAvailable")}
              </dd>
            </div>

            <div>
              <dt className="text-xs font-medium text-muted-foreground">
                Result
              </dt>

              <dd className="mt-1 text-sm">
                {passedLabel(validation.passed, t)}
              </dd>
            </div>
          </dl>

          <div className="mt-4">
            <p className="text-xs font-medium text-muted-foreground">
              {t("reasoning")}
            </p>

            <p className="mt-1 text-sm">
              {validation.reasoning ??
                t("noReasoning")}
            </p>
          </div>
        </article>
      ))}
    </div>
  );
}