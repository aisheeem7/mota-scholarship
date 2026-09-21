"use client";

import { useState } from "react";
import { CheckCircle2, UploadCloud } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const documents = [
  {
    id: "caste",
    name: "Caste Certificate",
    description: "Valid ST certificate issued by the competent authority.",
  },
  {
    id: "income",
    name: "Income Certificate",
    description: "Current annual family income certificate.",
  },
  {
    id: "academic",
    name: "Academic Certificate",
    description: "Latest marksheet or academic certificate.",
  },
  {
    id: "identity",
    name: "Identity Document",
    description: "Accepted government identity document.",
  },
];

type UploadState =
  | "DEFAULT"
  | "UPLOADING"
  | "PROCESSING"
  | "SUCCESS"
  | "ERROR";

export default function UploadPage() {
  const [status, setStatus] = useState<UploadState>("DEFAULT");
  const [selectedFiles, setSelectedFiles] = useState<
    Record<string, string>
  >({});

  function handleFileChange(
    id: string,
    file: File | undefined
  ) {
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      setStatus("ERROR");
      return;
    }

    setSelectedFiles((previous) => ({
      ...previous,
      [id]: file.name,
    }));

    setStatus("DEFAULT");
  }

  function handleSubmit() {
    setStatus("UPLOADING");

    setTimeout(() => {
      setStatus("PROCESSING");

      setTimeout(() => {
        setStatus("SUCCESS");
      }, 1500);
    }, 1000);
  }

  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-3xl px-6 py-8">

        <header className="mb-8">
          <p className="text-sm font-medium text-muted-foreground">
            MoTA Scholarship Portal
          </p>

          <h1 className="mt-2 text-3xl font-semibold">
            Upload documents
          </h1>

          <p className="mt-2 text-muted-foreground">
            Upload clear copies of the documents required for verification.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Required documents</CardTitle>

            <p className="text-sm text-muted-foreground">
              Accepted formats: PDF, JPG, JPEG and PNG. Maximum size:
              10 MB per file.
            </p>
          </CardHeader>

          <CardContent className="space-y-6">

            {documents.map((document) => (
              <div
                key={document.id}
                className="rounded-lg border p-4"
              >
                <div className="flex items-start gap-3">
                  <UploadCloud className="mt-1 h-5 w-5 shrink-0" />

                  <div className="min-w-0 flex-1">
                    <p className="font-medium">
                      {document.name}
                    </p>

                    <p className="mt-1 text-sm text-muted-foreground">
                      {document.description}
                    </p>

                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      className="mt-4 block w-full text-sm"
                      onChange={(event) =>
                        handleFileChange(
                          document.id,
                          event.target.files?.[0]
                        )
                      }
                    />

                    {selectedFiles[document.id] && (
                      <p className="mt-2 text-xs text-muted-foreground">
                        Selected: {selectedFiles[document.id]}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {status === "ERROR" && (
              <Alert variant="destructive">
                <AlertDescription>
                  File size must be 10 MB or less.
                </AlertDescription>
              </Alert>
            )}

            {status === "UPLOADING" && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Uploading documents...</span>
                  <span>50%</span>
                </div>

                <Progress value={50} />
              </div>
            )}

            {status === "PROCESSING" && (
              <Alert>
                <AlertDescription>
                  Documents uploaded. AI verification is being prepared.
                </AlertDescription>
              </Alert>
            )}

            {status === "SUCCESS" && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />

                <AlertDescription>
                  Documents submitted successfully.
                </AlertDescription>
              </Alert>
            )}

            <Button
              onClick={handleSubmit}
              disabled={
                status === "UPLOADING" ||
                status === "PROCESSING"
              }
            >
              {status === "UPLOADING"
                ? "Uploading..."
                : status === "PROCESSING"
                ? "Processing..."
                : status === "SUCCESS"
                ? "Submitted"
                : "Submit documents"}
            </Button>

          </CardContent>
        </Card>

      </div>
    </main>
  );
}