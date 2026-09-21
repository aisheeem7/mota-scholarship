import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default async function ApplicationDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-6xl space-y-6 px-6 py-8">

        <header>
          <p className="text-sm font-medium text-muted-foreground">
            Application Review
          </p>

          <h1 className="mt-2 text-3xl font-semibold">
            {id}
          </h1>

          <p className="mt-2 text-muted-foreground">
            Review student information, documents and AI validation.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Student information</CardTitle>
          </CardHeader>

          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-muted-foreground">
                Student
              </p>

              <p className="mt-1 font-medium">
                Student One
              </p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">
                Scheme
              </p>

              <p className="mt-1 font-medium">
                Post-Matric Scholarship
              </p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">
                Application status
              </p>

              <div className="mt-1">
                <Badge variant="secondary">
                  Processing
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI validation</CardTitle>

            <p className="text-sm text-muted-foreground">
              Rule-level evidence and reasoning.
            </p>
          </CardHeader>

          <CardContent>
            <div className="rounded-lg border p-5">

              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="font-medium">
                    Income eligibility
                  </p>

                  <p className="mt-1 text-sm text-muted-foreground">
                    Rule ID: INCOME_LIMIT
                  </p>
                </div>

                <Badge>
                  PASS
                </Badge>
              </div>

              <div className="mt-6 grid gap-4 sm:grid-cols-3">

                <div>
                  <p className="text-xs text-muted-foreground">
                    Evidence
                  </p>

                  <p className="mt-1 font-medium">
                    ₹1,80,000
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted-foreground">
                    Expected
                  </p>

                  <p className="mt-1 font-medium">
                    ≤ ₹2,50,000
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted-foreground">
                    Severity
                  </p>

                  <p className="mt-1 font-medium">
                    None
                  </p>
                </div>

              </div>

              <div className="mt-6 border-t pt-4">
                <p className="text-xs text-muted-foreground">
                  Reasoning
                </p>

                <p className="mt-1 text-sm leading-6">
                  The extracted annual family income is within the
                  configured eligibility threshold for this scheme.
                </p>
              </div>

            </div>
          </CardContent>
        </Card>

      </div>
    </main>
  );
}