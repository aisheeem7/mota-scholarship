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

type UploadState =
  | "DEFAULT"
  | "UPLOADING"
  | "PROCESSING"
  | "UNREADABLE"
  | "ERROR";

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ACCEPTED_TYPES = ".pdf,.jpg,.jpeg,.png";

export default function UploadPage() {
  const [status, setStatus] = useState<UploadState>("DEFAULT");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  function handleFileChange(fileList: FileList | null) {
    if (!fileList) return;

    const files = Array.from(fileList);
    const invalidFile = files.find((file) => file.size > MAX_FILE_SIZE);

    if (invalidFile) {
      setStatus("ERROR");
      setErrorMessage(
        "File \"" + invalidFile.name + "\" must be 10 MB or less.",
      );
      return;
    }

    setSelectedFiles(files);
    setStatus("DEFAULT");
    setErrorMessage(null);
  }

  function clearSelection() {
    setSelectedFiles([]);
    setStatus("DEFAULT");
    setErrorMessage(null);
  }

  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <header className="mb-8">
          <p className="text-sm font-medium text-muted-foreground">
            MoTA Scholarship Portal
          </p>
          <h1 className="mt-2 text-3xl font-semibold">Upload documents</h1>
          <p className="mt-2 text-muted-foreground">
            Select the documents you want to submit for verification.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Document upload</CardTitle>
            <p className="text-sm text-muted-foreground">
              Document categories are intentionally not hardcoded until the
              document_type contract is confirmed. Accepted formats: PDF, JPG,
              JPEG and PNG. Maximum size: 10 MB per file.
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            <label
              htmlFor="document-upload"
              className="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center transition-colors hover:bg-muted/50"
            >
              <UploadCloud className="mb-3 h-8 w-8" />
              <span className="font-medium">Choose document files</span>
              <span className="mt-1 text-sm text-muted-foreground">
                Multiple files can be selected.
              </span>
              <input
                id="document-upload"
                type="file"
                multiple
                accept={ACCEPTED_TYPES}
                className="sr-only"
                onChange={(event) => handleFileChange(event.target.files)}
              />
            </label>

            {selectedFiles.length > 0 && (
              <div className="space-y-3">
                <p className="text-sm font-medium">
                  Selected files ({selectedFiles.length})
                </p>
                <ul className="space-y-2">
                  {selectedFiles.map((file) => (
                    <li
                      key={file.name + "-" + file.size + "-" + file.lastModified}
                      className="rounded-md border px-3 py-2 text-sm"
                    >
                      {file.name}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {status === "ERROR" && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {errorMessage ?? "The selected file could not be accepted."}
                </AlertDescription>
              </Alert>
            )}

            {status === "UPLOADING" && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Uploading documents…</span>
                  <span>In progress</span>
                </div>
                <Progress value={50} />
              </div>
            )}

            {status === "PROCESSING" && (
              <Alert>
                <AlertDescription>
                  Documents uploaded. Processing is in progress.
                </AlertDescription>
              </Alert>
            )}

            {status === "UNREADABLE" && (
              <Alert variant="destructive">
                <AlertDescription>
                  A document could not be read. Please upload a clearer copy.
                </AlertDescription>
              </Alert>
            )}

            {status === "DEFAULT" && selectedFiles.length > 0 && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />
                <AlertDescription>
                  Files are ready for upload once the document upload contract
                  is connected.
                </AlertDescription>
              </Alert>
            )}

            {selectedFiles.length > 0 && (
              <Button variant="outline" onClick={clearSelection}>
                Clear selection
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
