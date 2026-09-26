"use client";

import { useState } from "react";
import { AlertCircle, CheckCircle2, UploadCloud } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
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
  uploadApplicationDocument,
} from "@/lib/api";

import type {
  Application,
  Document,
  DocumentType,
  SchemeId,
} from "@/lib/types";

type UploadState =
  | "DEFAULT"
  | "CREATING_APPLICATION"
  | "UPLOADING"
  | "PROCESSING"
  | "ERROR"
  | "SUCCESS";

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ACCEPTED_TYPES = ".pdf,.jpg,.jpeg,.png";

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

export default function UploadPage() {
  const [status, setStatus] = useState<UploadState>("DEFAULT");

  const [selectedScheme, setSelectedScheme] =
    useState<SchemeId>("PRE_MATRIC");

  const [selectedDocumentType, setSelectedDocumentType] =
    useState<DocumentType>("INCOME_CERTIFICATE");

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const [application, setApplication] =
    useState<Application | null>(null);

  const [uploadedDocuments, setUploadedDocuments] =
    useState<Document[]>([]);

  const [errorMessage, setErrorMessage] =
    useState<string | null>(null);

  const demoStudentId =
    process.env.NEXT_PUBLIC_DEMO_STUDENT_ID;

  function handleFileChange(fileList: FileList | null) {
    if (!fileList) {
      return;
    }

    const files = Array.from(fileList);

    const invalidFile = files.find((file) => {
      const extension = `.${file.name.split(".").pop()?.toLowerCase()}`;

      return (
        ![".pdf", ".jpg", ".jpeg", ".png"].includes(extension) ||
        file.size === 0 ||
        file.size > MAX_FILE_SIZE
      );
    });

    if (invalidFile) {
      setSelectedFiles([]);
      setErrorMessage(
        `${invalidFile.name} is invalid. Use a non-empty PDF, JPG, JPEG or PNG file up to 10 MB.`,
      );
      setStatus("ERROR");
      return;
    }

    setErrorMessage(null);
    setSelectedFiles(files);
    setStatus("DEFAULT");
  }

  async function handleCreateApplication() {
    if (!demoStudentId) {
      setErrorMessage(
        "Demo Mode is not configured. NEXT_PUBLIC_DEMO_STUDENT_ID is missing.",
      );
      setStatus("ERROR");
      return;
    }

    setErrorMessage(null);
    setStatus("CREATING_APPLICATION");

    try {
      const createdApplication = await createApplication({
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

  async function handleUpload() {
    if (!application) {
      setErrorMessage(
        "Create the application before uploading documents.",
      );
      setStatus("ERROR");
      return;
    }

    if (selectedFiles.length === 0) {
      setErrorMessage("Select at least one document to upload.");
      setStatus("ERROR");
      return;
    }

    setErrorMessage(null);
    setStatus("UPLOADING");

    try {
      const uploaded: Document[] = [];

      for (const file of selectedFiles) {
        const document = await uploadApplicationDocument(
          application.id,
          selectedDocumentType,
          file,
        );

        uploaded.push(document);
      }

      setUploadedDocuments((current) => [
        ...current,
        ...uploaded,
      ]);

      setSelectedFiles([]);
      setStatus("SUCCESS");
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Document upload failed.",
      );
      setStatus("ERROR");
    }
  }

  return (
    <main className="container mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">
          Upload documents
        </h1>

        <p className="mt-2 text-muted-foreground">
          Demo Mode — create an application and upload documents
          for verification.
        </p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>1. Select scheme</CardTitle>
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
                  {scheme.label}
                </option>
              ))}
            </select>

            {!application && (
              <Button
                type="button"
                onClick={handleCreateApplication}
                disabled={
                  status === "CREATING_APPLICATION"
                }
              >
                {status === "CREATING_APPLICATION"
                  ? "Creating application..."
                  : "Create application"}
              </Button>
            )}

            {application && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />

                <AlertDescription>
                  Application created successfully.
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
            <CardTitle>2. Upload document</CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            <div>
              <label
                htmlFor="document-type"
                className="mb-2 block text-sm font-medium"
              >
                Document category
              </label>

              <select
                id="document-type"
                value={selectedDocumentType}
                onChange={(event) =>
                  setSelectedDocumentType(
                    event.target.value as DocumentType,
                  )
                }
                disabled={!application}
                className="w-full rounded-md border bg-background px-3 py-2 text-sm"
              >
                {DOCUMENT_TYPES.map((documentType) => (
                  <option
                    key={documentType.value}
                    value={documentType.value}
                  >
                    {documentType.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="rounded-lg border border-dashed p-8 text-center">
              <UploadCloud className="mx-auto h-10 w-10 text-muted-foreground" />

              <div className="mt-4">
                <p className="font-medium">
                  Choose documents to upload
                </p>

                <span className="mt-1 block text-sm text-muted-foreground">
                  Accepted formats: PDF, JPG, JPEG and PNG.
                  Maximum size: 10 MB.
                </span>
              </div>
              <div className="mt-6">
                <label
                  htmlFor="document-upload"
                  className={`inline-flex cursor-pointer items-center justify-center rounded-md border px-4 py-2 text-sm font-medium transition-colors ${application
                      ? "hover:bg-accent hover:text-accent-foreground"
                      : "pointer-events-none opacity-50"
                    }`}
                >
                  Select files
                </label>

                <input
                  id="document-upload"
                  type="file"
                  accept={ACCEPTED_TYPES}
                  multiple
                  disabled={!application}
                  className="sr-only"
                  onChange={(event) => {
                    handleFileChange(event.target.files);
                    event.currentTarget.value = "";
                  }}
                />
              </div>


            </div>

            {selectedFiles.length > 0 && (
              <div className="space-y-3">
                <h2 className="font-medium">
                  Selected files
                </h2>

                <div className="space-y-2">
                  {selectedFiles.map((file) => (
                    <div
                      key={`${file.name}-${file.lastModified}`}
                      className="rounded-md border p-3"
                    >
                      <p className="truncate text-sm font-medium">
                        {file.name}
                      </p>

                      <p className="text-xs text-muted-foreground">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  ))}
                </div>

                <Button
                  type="button"
                  onClick={handleUpload}
                  disabled={
                    !application ||
                    status === "UPLOADING"
                  }
                >
                  {status === "UPLOADING"
                    ? "Uploading..."
                    : "Upload documents"}
                </Button>
              </div>
            )}

            {status === "UPLOADING" && (
              <div className="space-y-3">
                <Alert>
                  <UploadCloud className="h-4 w-4" />

                  <AlertDescription>
                    Uploading documents. Please keep this
                    page open.
                  </AlertDescription>
                </Alert>

                <Progress value={50} />
              </div>
            )}

            {status === "SUCCESS" && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />

                <AlertDescription>
                  Document upload completed successfully.
                  The backend has accepted the uploaded
                  document.
                </AlertDescription>
              </Alert>
            )}

            {status === "ERROR" && errorMessage && (
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
              <CardTitle>Uploaded documents</CardTitle>
            </CardHeader>

            <CardContent>
              <div className="space-y-2">
                {uploadedDocuments.map((document) => (
                  <div
                    key={document.id}
                    className="flex items-center justify-between rounded-md border p-3"
                  >
                    <div>
                      <p className="text-sm font-medium">
                        {document.document_type}
                      </p>

                      <p className="text-xs text-muted-foreground">
                        OCR status: {document.ocr_status}
                      </p>
                    </div>

                    <CheckCircle2 className="h-4 w-4" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  );
}