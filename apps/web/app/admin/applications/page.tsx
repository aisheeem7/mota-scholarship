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
import { getAdmin{t("applications")} } from "@/lib/api";
import { useLanguage } from "@/components/layout/language-provider";
import { schemeLabel, statusLabel, type TranslationKey } from "@/lib/i18n";
import {
  type Application,
} from "@/lib/types";

function ApplicationRows({
  applications,
  language,
  t,
}: {
  applications: Application[];
  language: "en" | "hi" | "bn";
  t: (key: TranslationKey) => string;
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
            {schemeLabel(language, application.scheme_id)}
          </td>
          <td className="px-4 py-4">
            <Badge variant="secondary">
              {statusLabel(language, application.status)}
            </Badge>
          </td>
          <td className="px-4 py-4">
            {application.risk_score === null
              ? t("notEvaluated")
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
  const { language, t } = useLanguage();
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
            : "{t("errorApplications")}",
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

  async function handle{t("retry")}() {
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
            {t("ministry")}
          </p>
          <h1 className="mt-2 text-3xl font-semibold">
            Applications
          </h1>
          <p className="mt-2 text-muted-foreground">
            {t("reviewApplicationsDescription")}
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>{t("applicationQueue")}</CardTitle>
          </CardHeader>

          <CardContent>
            {loading && (
              <div className="py-8 text-center text-sm text-muted-foreground">
                {t("loadingApplications")}
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
                {t("noApplications")}
              </p>
            )}

            {!loading && !error && applications.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-left text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-3">{t("applicationId")}</th>
                      <th className="px-4 py-3">{t("studentId")}</th>
                      <th className="px-4 py-3">{t("scheme")}</th>
                      <th className="px-4 py-3">{t("status")}</th>
                      <th className="px-4 py-3">{t("riskScore")}</th>
                      <th className="px-4 py-3">{t("review")}</th>
                    </tr>
                  </thead>
                  <ApplicationRows applications={applications} language={language} t={t} />
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
