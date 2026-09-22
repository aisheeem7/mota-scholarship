import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getApplication } from "@/lib/api";
import {
  APPLICATION_STATUS_LABELS,
  SCHEME_LABELS,
} from "@/lib/types";

export default async function ApplicationDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let application;

  try {
    application = await getApplication(id);
  } catch {
    return (
      <main className="min-h-screen bg-muted/30">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <Card>
            <CardHeader>
              <CardTitle>Application unavailable</CardTitle>
            </CardHeader>

            <CardContent>
              <p className="text-sm text-muted-foreground">
                We could not load this application. Please try again.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        <header>
          <p className="text-sm font-medium text-muted-foreground">
            Application Review
          </p>

          <h1 className="mt-2 text-3xl font-semibold">
            {application.id}
          </h1>

          <p className="mt-2 text-muted-foreground">
            Review application information and verification status.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Application information</CardTitle>
          </CardHeader>

          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-muted-foreground">
                Student ID
              </p>

              <p className="mt-1 font-medium">
                {application.student_id}
              </p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">
                Scheme
              </p>

              <p className="mt-1 font-medium">
                {SCHEME_LABELS[application.scheme_id]}
              </p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">
                Application status
              </p>

              <div className="mt-1">
                <Badge variant="secondary">
                  {APPLICATION_STATUS_LABELS[application.status]}
                </Badge>
              </div>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">
                Risk score
              </p>

              <p className="mt-1 font-medium">
                {application.risk_score ?? "Not evaluated"}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}