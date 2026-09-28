"use client";

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

import { ValidationScorecard } from "@/components/admin/validation-scorecard";
import { useLanguage } from "@/components/layout/language-provider";
import { documentTypeLabel, ocrStatusLabel, schemeLabel, statusLabel } from "@/lib/i18n";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  getApplication,
  getApplicationDocuments,
  getApplicationValidations,
  reviewApplication,
  type AdminReviewDecision,
} from "@/lib/api";
import {
  type Application,
  type Document,
  type ValidationResult,
} from "@/lib/types";

function statusClass(
  status: Application["status"],
): string {
  if (status === "APPROVED") {
    return "border-green-600 text-green-700";
  }

  if (status === "DEFICIENT") {
    return "border-yellow-600 text-yellow-700";
  }

  if (status === "FLAGGED_FOR_REVIEW") {
    return "border-orange-600 text-orange-700";
  }

  if (status === "REJECTED") {
    return "border-red-600 text-red-700";
  }

  return "";
}

export default function ApplicationDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { language, t } = useLanguage();
  const [applicationId, setApplicationId] = useState<string | null>(null);
  const [application, setApplication] =
    useState<Application | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [validations, setValidations] =
    useState<ValidationResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reviewReason, setReviewReason] = useState(
    "Reviewed by administrator based on the submitted evidence.",
  );

  useEffect(() => {
    let cancelled = false;

    async function loadApplication() {
      try {
        const { id } = await params;

        if (cancelled) {
          return;
        }

        setApplicationId(id);

        const [applicationData, documentData, validationData] =
          await Promise.all([
            getApplication(id),
            getApplicationDocuments(id),
            getApplicationValidations(id),
          ]);

        if (cancelled) {
          return;
        }

        setApplication(applicationData);
        setDocuments(documentData);
        setValidations(validationData);
      } catch (requestError) {
        if (cancelled) {
          return;
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : t("errorApplication"),
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadApplication();

    return () => {
      cancelled = true;
    };
  }, [params]);

  async function handleReview(
    decision: AdminReviewDecision,
  ) {
    if (!applicationId || !application) {
      return;
    }

    setReviewing(true);
    setError(null);

    try {
      const updated = await reviewApplication(
        applicationId,
        decision,
        reviewReason.trim() ||
          "Reviewed by administrator based on submitted evidence.",
      );

      setApplication(updated);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : t("errorReview"),
      );
    } finally {
      setReviewing(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-muted/30">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <Card>
            <CardContent className="py-12 text-center text-sm text-muted-foreground">
              {t("loadingApplication")}
            </CardContent>
          </Card>
        </div>
      </main>
    );
  }

  if (error && !application) {
    return (
      <main className="min-h-screen bg-muted/30">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </main>
    );
  }

  if (!application) {
    return null;
  }

  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        <header>
          <p className="text-sm font-medium text-muted-foreground">
            {t("adminReview")}
          </p>
          <h1 className="mt-2 break-all text-3xl font-semibold">
            {application.id}
          </h1>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge
              variant="outline"
              className={statusClass(application.status)}
            >
              {statusLabel(language, application.status)}
            </Badge>
            <Badge variant="secondary">
              {t("riskScore")}: {application.risk_score ?? t("notEvaluated")}
            </Badge>
          </div>
        </header>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Card>
          <CardHeader>
            <CardTitle>{t("studentInformation")}</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-muted-foreground">{t("studentId")}</p>
              <p className="mt-1 font-medium">
                {application.student_id}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{t("scheme")}</p>
              <p className="mt-1 font-medium">
                {schemeLabel(language, application.scheme_id)}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("uploadedDocuments")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {documents.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                {t("noDocuments")}
              </p>
            ) : (
              documents.map((document) => (
                <div
                  key={document.id}
                  className="flex items-center justify-between rounded-md border p-3"
                >
                  <div>
                    <p className="text-sm font-medium">
                      {documentTypeLabel(language, document.document_type)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {t("ocrStatus")}: {ocrStatusLabel(language, document.ocr_status)}
                    </p>
                  </div>
                  {document.ocr_status === "READABLE" ? (
                    <CheckCircle2 className="h-4 w-4" />
                  ) : (
                    <Badge variant="secondary">
                      {ocrStatusLabel(language, document.ocr_status)}
                    </Badge>
                  )}
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("validationScorecard")}</CardTitle>
          </CardHeader>
          <CardContent>
            <ValidationScorecard validations={validations} />
          </CardContent>
        </Card>

        {application.status === "FLAGGED_FOR_REVIEW" && (
          <Card>
            <CardHeader>
              <CardTitle>{t("humanReview")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {t("flaggedReview")}
              </p>

              <textarea
                value={reviewReason}
                onChange={(event) =>
                  setReviewReason(event.target.value)
                }
                className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm"
                aria-label={t("reviewReason")}
              />

              <div className="flex flex-wrap gap-3">
                <Button
                  disabled={reviewing}
                  onClick={() => void handleReview("APPROVE")}
                >
                  {reviewing && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  {t("approve")}
                </Button>

                <Button
                  variant="outline"
                  disabled={reviewing}
                  onClick={() =>
                    void handleReview("REQUEST_RESUBMISSION")
                  }
                >
                  {t("requestResubmission")}
                </Button>

                <Button
                  variant="destructive"
                  disabled={reviewing}
                  onClick={() => void handleReview("REJECT")}
                >
                  {t("reject")}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  );
}
