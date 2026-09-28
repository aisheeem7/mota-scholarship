"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getAdminApplications } from "@/lib/api";
import {
  APPLICATION_STATUS_LABELS,
  SCHEME_LABELS,
  type Application,
} from "@/lib/types";

function ApplicationRows({
  applications,
}: {
  applications: Application[];
}) {
  return (
    <tbody>
      {applications.map((application) => (
        <tr
          key={application.id}
          className="border-b last:border-0"
        >
          <td className="px-4 py-4 font-medium">
            {application.id}
          </td>
          <td className="px-4 py-4">
            {application.student_id}
          </td>
          <td className="px-4 py-4">
            {SCHEME_LABELS[application.scheme_id]}
          </td>
          <td className="px-4 py-4">
            <Badge variant="secondary">
              {APPLICATION_STATUS_LABELS[application.status]}
            </Badge>
          </td>
          <td className="px-4 py-4">
            {application.risk_score === null
              ? "Not evaluated"
              : application.risk_score}
          </td>
          <td className="px-4 py-4">
            <Link href={`/admin/applications/${application.id}`}>
              <Button variant="outline" size="sm">
                Review
              </Button>
            </Link>
          </td>
        </tr>
      ))}
    </tbody>
  );
}

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadInitialApplications() {
      try {
        const data = await getAdminApplications();

        if (cancelled) {
          return;
        }

        setApplications(data);
      } catch (requestError) {
        if (cancelled) {
          return;
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Could not load applications.",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadInitialApplications();

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleRetry() {
    setLoading(true);
    setError(null);

    try {
      const data = await getAdminApplications();
      setApplications(data);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Could not load applications.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <header className="mb-8">
          <p className="text-sm font-medium text-muted-foreground">
            MoTA Scholarship Administration
          </p>
          <h1 className="mt-2 text-3xl font-semibold">
            Applications
          </h1>
          <p className="mt-2 text-muted-foreground">
            Review scholarship applications and verification status.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Application Queue</CardTitle>
          </CardHeader>

          <CardContent>
            {loading && (
              <div className="py-8 text-center text-sm text-muted-foreground">
                Loading applications…
              </div>
            )}

            {!loading && error && (
              <div className="flex flex-col items-center gap-3 py-8 text-center">
                <p className="text-sm text-destructive">
                  {error}
                </p>
                <Button
                  variant="outline"
                  onClick={() => void handleRetry()}
                >
                  Retry
                </Button>
              </div>
            )}

            {!loading && !error && applications.length === 0 && (
              <p className="py-8 text-center text-sm text-muted-foreground">
                No applications found.
              </p>
            )}

            {!loading && !error && applications.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-left text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-3">Application ID</th>
                      <th className="px-4 py-3">Student ID</th>
                      <th className="px-4 py-3">Scheme</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Risk score</th>
                      <th className="px-4 py-3">Review</th>
                    </tr>
                  </thead>
                  <ApplicationRows applications={applications} />
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
