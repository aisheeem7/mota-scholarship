"use client";

import { useEffect, useRef, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Loader2,
  UploadCloud,
} from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

import {
  createApplication,
  getApplication,
  getApplicationDocuments,
  getApplicationValidations,
  processApplication,
  uploadApplicationDocument,
} from "@/lib/api";

import {
  type Application,
  type Document,
  type DocumentType,
  type SchemeId,
  type ValidationResult,
} from "@/lib/types";
import { documentTypeLabel, ocrStatusLabel, schemeLabel, statusLabel } from "@/lib/i18n";
import { useLanguage } from "@/components/layout/language-provider";

import { ValidationScorecard } from "@/components/admin/validation-scorecard";

type UploadState =
  | "DEFAULT"
  | "CREATING_APPLICATION"
  | "UPLOADING"
  | "PROCESSING"
  | "SUCCESS"
  | "ERROR";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const ACCEPTED_TYPES = ".pdf,.jpg,.jpeg,.png";

const TERMINAL_STATUSES = new Set([
  "APPROVED",
  "DEFICIENT",
  "FLAGGED_FOR_REVIEW",
  "ADMIN_REVIEW",
  "REJECTED",
]);

const POLL_INTERVAL_MS = 2000;

const MAX_POLL_ATTEMPTS = 60;

const DOCUMENT_TYPES: {
  value: DocumentType;
  label: string;
}[] = [
  {
    value: "INCOME_CERTIFICATE",
    label: "Income Certificate",
  },
  {
    value: "CASTE_CERTIFICATE",
    label: "Caste Certificate",
  },
  {
    value: "ACADEMIC_RECORD",
    label: "Academic Record",
  },
  {
    value: "IDENTITY_DOCUMENT",
    label: "Identity Document",
  },
];

const SCHEMES: {
  value: SchemeId;
  label: string;
}[] = [
  {
    value: "PRE_MATRIC",
    label: "Pre-Matric Scholarship",
  },
  {
    value: "POST_MATRIC",
    label: "Post-Matric Scholarship",
  },
  {
    value: "TOP_CLASS",
    label: "National Scholarship Scheme (Top Class)",
  },
  {
    value: "NATIONAL_FELLOWSHIP",
    label: "National Fellowship Scheme",
  },
  {
    value: "NATIONAL_OVERSEAS",
    label: "National Overseas Scholarship",
  },
];

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function statusBadgeClass(
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

export default function UploadPage() {
  const { language, t } = useLanguage();

  const [status, setStatus] =
    useState<UploadState>("DEFAULT");

  const [selectedScheme, setSelectedScheme] =
    useState<SchemeId>("PRE_MATRIC");

  const [selectedFiles, setSelectedFiles] =
    useState<Record<DocumentType, File | null>>({
      INCOME_CERTIFICATE: null,
      CASTE_CERTIFICATE: null,
      ACADEMIC_RECORD: null,
      IDENTITY_DOCUMENT: null,
    });

  const [application, setApplication] =
    useState<Application | null>(null);

  const [uploadedDocuments, setUploadedDocuments] =
    useState<Document[]>([]);

  const [validations, setValidations] =
    useState<ValidationResult[]>([]);

  const [errorMessage, setErrorMessage] =
    useState<string | null>(null);

  const [processingMessage, setProcessingMessage] =
    useState("Starting verification...");

  const pollCancelled = useRef(false);

  const demoStudentId =
    process.env.NEXT_PUBLIC_DEMO_STUDENT_ID;

  useEffect(() => {
    pollCancelled.current = false;

    return () => {
      pollCancelled.current = true;
    };
  }, []);

  function handleFileChange(
    documentType: DocumentType,
    fileList: FileList | null,
  ) {
    if (!fileList || fileList.length === 0) {
      return;
    }

    const file = fileList[0];

    const extension =
      `.${file.name.split(".").pop()?.toLowerCase()}`;

    if (
      ![".pdf", ".jpg", ".jpeg", ".png"].includes(
        extension,
      ) ||
      file.size === 0 ||
      file.size > MAX_FILE_SIZE
    ) {
      setErrorMessage(
        `${file.name} ${t("invalidFile")}`,
      );

      setStatus("ERROR");

      return;
    }

    setErrorMessage(null);

    setSelectedFiles((current) => ({
      ...current,
      [documentType]: file,
    }));

    setStatus("DEFAULT");
  }

  async function handleCreateApplication() {
    if (!demoStudentId) {
      setErrorMessage(
        t("demoIdMissing"),
      );

      setStatus("ERROR");

      return;
    }

    setErrorMessage(null);
    setStatus("CREATING_APPLICATION");

    try {
      const createdApplication =
        await createApplication({
          student_id: demoStudentId,
          scheme_id: selectedScheme,
        });

      setApplication(createdApplication);
      setStatus("DEFAULT");
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Application creation failed.",
      );

      setStatus("ERROR");
    }
  }

  async function pollApplicationUntilComplete(
    applicationId: string,
  ): Promise<Application> {
    for (
      let attempt = 0;
      attempt < MAX_POLL_ATTEMPTS;
      attempt += 1
    ) {
      if (pollCancelled.current) {
        throw new Error(
          "Processing was interrupted because the page was closed.",
        );
      }

      await wait(POLL_INTERVAL_MS);

      const [currentApplication, currentDocuments] =
        await Promise.all([
          getApplication(applicationId),
          getApplicationDocuments(applicationId),
        ]);

      setApplication(currentApplication);
      setUploadedDocuments(currentDocuments);

      if (
        TERMINAL_STATUSES.has(
          currentApplication.status,
        )
      ) {
        return currentApplication;
      }

      setProcessingMessage(
        `Verification is still processing... (${attempt + 1}/${MAX_POLL_ATTEMPTS})`,
      );
    }

    throw new Error(
      "Verification is taking longer than expected. Please check the application status again.",
    );
  }

  async function handleUpload() {
    if (!application) {
      setErrorMessage(
        t("createBeforeUpload"),
      );

      setStatus("ERROR");

      return;
    }

    const selectedDocumentCount =
      Object.values(selectedFiles).filter(Boolean).length;

    if (selectedDocumentCount === 0) {
      setErrorMessage(
        t("selectDocument"),
      );

      setStatus("ERROR");

      return;
    }

    setErrorMessage(null);
    setStatus("UPLOADING");

    try {
      const uploaded: Document[] = [];

      for (const documentType of DOCUMENT_TYPES) {
        const file = selectedFiles[documentType.value];

        if (!file) {
          continue;
        }

        const document =
          await uploadApplicationDocument(
            application.id,
            documentType.value,
            file,
          );

        uploaded.push(document);
      }

      setUploadedDocuments((current) => [
        ...current,
        ...uploaded,
      ]);

      setSelectedFiles({
        INCOME_CERTIFICATE: null,
        CASTE_CERTIFICATE: null,
        ACADEMIC_RECORD: null,
        IDENTITY_DOCUMENT: null,
      });

      setStatus("PROCESSING");

      setProcessingMessage(
        "Starting OCR and verification...",
      );

      const processingApplication =
        await processApplication(application.id);

      setApplication(processingApplication);

      const completedApplication =
        await pollApplicationUntilComplete(
          application.id,
        );

      setApplication(completedApplication);

      const validationResults =
        await getApplicationValidations(
          application.id,
        );

      setValidations(validationResults);

      setStatus("SUCCESS");
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Document verification failed.",
      );

      setStatus("ERROR");
    }
  }

  return (
    <main className="container mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">
          {t("uploadDocuments")}
        </h1>

        <p className="mt-2 text-muted-foreground">
          {t("demoMode")} — {t("uploadDocuments")}.
        </p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>
              {t("selectScheme")}
            </CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            <select
              value={selectedScheme}
              onChange={(event) =>
                setSelectedScheme(
                  event.target.value as SchemeId,
                )
              }
              disabled={Boolean(application)}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            >
              {SCHEMES.map((scheme) => (
                <option
                  key={scheme.value}
                  value={scheme.value}
                >
                  {schemeLabel(language, scheme.value)}
                </option>
              ))}
            </select>

            {!application && (
              <Button
                type="button"
                onClick={handleCreateApplication}
                disabled={
                  status ===
                  "CREATING_APPLICATION"
                }
              >
                {status ===
                "CREATING_APPLICATION"
                  ? "Creating application..."
                  : t("createApplication")}
              </Button>
            )}

            {application && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />

                <AlertDescription>
                  {t("applicationCreated")}

                  <span className="mt-1 block break-all font-mono text-xs">
                    {application.id}
                  </span>
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              {t("uploadStep")}
            </CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            <div className="rounded-lg border p-4">
              <p className="font-medium">
                {t("uploadAvailable")}
              </p>

              <p className="mt-1 text-sm text-muted-foreground">
                {t("uploadHelp")}
              </p>

              <div className="mt-4 space-y-3">
                {DOCUMENT_TYPES.map((documentType) => {
                  const selectedFile =
                    selectedFiles[documentType.value];

                  return (
                    <div
                      key={documentType.value}
                      className="flex flex-col gap-3 rounded-md border p-4 sm:flex-row sm:items-center sm:justify-between"
                    >
                      <div className="min-w-0">
                        <p className="text-sm font-medium">
                          {documentType.label}
                        </p>

                        <p className="mt-1 truncate text-xs text-muted-foreground">
                          {selectedFile
                            ? selectedFile.name
                            : "No file selected"}
                        </p>
                      </div>

                      <label
                        htmlFor={`document-upload-${documentType.value}`}
                        className={`inline-flex shrink-0 cursor-pointer items-center justify-center rounded-md border px-4 py-2 text-sm font-medium transition-colors ${
                          application &&
                          status !== "UPLOADING" &&
                          status !== "PROCESSING"
                            ? "hover:bg-accent hover:text-accent-foreground"
                            : "pointer-events-none opacity-50"
                        }`}
                      >
                        {selectedFile
                          ? t("changeFile")
                          : t("chooseFile")}
                      </label>

                      <input
                        id={`document-upload-${documentType.value}`}
                        type="file"
                        accept={ACCEPTED_TYPES}
                        disabled={
                          !application ||
                          status === "UPLOADING" ||
                          status === "PROCESSING"
                        }
                        className="sr-only"
                        onChange={(event) => {
                          handleFileChange(
                            documentType.value,
                            event.target.files,
                          );

                          event.currentTarget.value = "";
                        }}
                      />
                    </div>
                  );
                })}
              </div>
            </div>

            {Object.values(selectedFiles).some(Boolean) && (
              <div className="rounded-md border bg-muted/30 p-4">
                <p className="text-sm font-medium">
                  {t("documentsSelected")}:{" "}
                  {
                    Object.values(selectedFiles).filter(
                      Boolean,
                    ).length
                  }
                  /4
                </p>

                <p className="mt-1 text-xs text-muted-foreground">
                  {t("missingDocuments")}
                </p>
              </div>
            )}

            <Button
              type="button"
              onClick={handleUpload}
              disabled={
                !application ||
                status === "UPLOADING" ||
                status === "PROCESSING"
              }
            >
              {status === "UPLOADING"
                ? "Uploading..."
                : t("uploadVerify")}
            </Button>

            {status === "UPLOADING" && (
              <div className="space-y-3">
                <Alert>
                  <UploadCloud className="h-4 w-4" />

                  <AlertDescription>
                    {t("uploading")}
                  </AlertDescription>
                </Alert>

                <Progress value={35} />
              </div>
            )}

            {status === "PROCESSING" && (
              <div className="space-y-3">
                <Alert>
                  <Loader2 className="h-4 w-4 animate-spin" />

                  <AlertDescription>
                    {processingMessage}
                  </AlertDescription>
                </Alert>

                <Progress value={75} />
              </div>
            )}

            {status === "SUCCESS" &&
              application && (
                <Alert>
                  <CheckCircle2 className="h-4 w-4" />

                  <AlertDescription>
                    {t("verificationCompleted")}:{" "}
                    <strong>
                      {statusLabel(language, application.status)}
                    </strong>
                  </AlertDescription>
                </Alert>
              )}

            {status === "ERROR" &&
              errorMessage && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />

                  <AlertDescription>
                    {errorMessage}
                  </AlertDescription>
                </Alert>
              )}
          </CardContent>
        </Card>

        {uploadedDocuments.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>
                {t("uploadedDocuments")}
              </CardTitle>
            </CardHeader>

            <CardContent>
              <div className="space-y-2">
                {uploadedDocuments.map(
                  (document) => (
                    <div
                      key={document.id}
                      className="flex items-center justify-between rounded-md border p-3"
                    >
                      <div>
                        <p className="text-sm font-medium">
                          {documentTypeLabel(language, document.document_type)}
                        </p>

                        <p className="text-xs text-muted-foreground">
                          {t("ocrStatus")}:{" "}
                          {ocrStatusLabel(language, document.ocr_status)}
                        </p>
                      </div>

                      <CheckCircle2 className="h-4 w-4" />
                    </div>
                  ),
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {application && (
          <Card>
            <CardHeader>
              <CardTitle>
                Verification result
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-5">
              <div className="flex flex-wrap items-center gap-3">
                <Badge
                  variant="outline"
                  className={statusBadgeClass(
                    application.status,
                  )}
                >
                  {
                    APPLICATION_STATUS_LABELS[
                      application.status
                    ]
                  }
                </Badge>

                <Badge variant="secondary">
                  {t("riskScore")}:{" "}
                  {application.risk_score ?? t("notAvailable")}
                </Badge>
              </div>

              <div>
                <p className="text-sm font-medium">{t("applicationId")}</p>

                <p className="mt-1 break-all font-mono text-xs text-muted-foreground">
                  {application.id}
                </p>
              </div>

              {validations.length > 0 && (
                <div>
                  <h3 className="mb-3 font-medium">
                    {t("validationScorecard")}
                  </h3>

                  <ValidationScorecard
                    validations={validations}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  );
}