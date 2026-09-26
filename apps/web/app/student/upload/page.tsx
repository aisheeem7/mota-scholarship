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
    if (!fileList) {
      return;
    }

    const files = Array.from(fileList);

    const oversizedFile = files.find((file) => file.size > MAX_FILE_SIZE);

    if (oversizedFile) {
      setSelectedFiles([]);
      setErrorMessage(
        `${oversizedFile.name} exceeds the 10 MB maximum file size.`,
      );
      setStatus("ERROR");
      return;
    }

    setErrorMessage(null);
    setSelectedFiles(files);
    setStatus("DEFAULT");
  }

  function clearSelection() {
    setSelectedFiles([]);
    setErrorMessage(null);
    setStatus("DEFAULT");
  }

  return (
    <main className="container mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">
          Upload documents
        </h1>
        <p className="mt-2 text-muted-foreground">
          Select a document category and upload a PDF, JPG, JPEG or PNG file.
          Maximum size: 10 MB per file.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Document upload</CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="rounded-lg border border-dashed p-8 text-center">
            <UploadCloud className="mx-auto h-10 w-10 text-muted-foreground" />

            <div className="mt-4">
              <p className="font-medium">Choose documents to upload</p>

              <span className="mt-1 block text-sm text-muted-foreground">
                Accepted formats: PDF, JPG, JPEG and PNG. Maximum size: 10 MB.
              </span>
            </div>

            <label
              htmlFor="document-upload"
              className="mt-6 inline-flex cursor-pointer"
            >
              <Button type="button" asChild>
                <span>Select files</span>
              </Button>

              <input
                id="document-upload"
                type="file"
                accept={ACCEPTED_TYPES}
                multiple
                className="sr-only"
                onChange={(event) => {
                  handleFileChange(event.target.files);
                  event.currentTarget.value = "";
                }}
              />
            </label>
          </div>

          {selectedFiles.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="font-medium">Selected files</h2>

                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={clearSelection}
                  disabled={status === "UPLOADING" || status === "PROCESSING"}
                >
                  Clear
                </Button>
              </div>

              <div className="space-y-2">
                {selectedFiles.map((file) => (
                  <div
                    key={`${file.name}-${file.lastModified}`}
                    className="flex items-center justify-between rounded-md border p-3"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">
                        {file.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {status === "ERROR" && errorMessage && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {status === "UPLOADING" && (
            <Alert>
              <UploadCloud className="h-4 w-4" />
              <AlertDescription>
                Uploading documents. Please keep this page open.
              </AlertDescription>
            </Alert>
          )}

          {status === "PROCESSING" && (
            <div className="space-y-3">
              <Alert>
                <UploadCloud className="h-4 w-4" />
                <AlertDescription>
                  Documents uploaded. Processing has started.
                </AlertDescription>
              </Alert>

              <Progress value={60} />
            </div>
          )}

          {status === "UNREADABLE" && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                A document could not be read. Please upload a clearer copy.
              </AlertDescription>
            </Alert>
          )}

          {status === "DEFAULT" && selectedFiles.length === 0 && (
            <Alert>
              <CheckCircle2 className="h-4 w-4" />
              <AlertDescription>
                Select a document category, then upload the file for
                verification.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </main>
  );
}