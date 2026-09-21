import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const statistics = [
  {
    label: "Total applications",
    value: "1,248",
  },
  {
    label: "Processing",
    value: "326",
  },
  {
    label: "Approved",
    value: "714",
  },
  {
    label: "Deficient",
    value: "142",
  },
  {
    label: "Flagged for review",
    value: "66",
  },
];

export default function AdminDashboard() {
  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-7xl px-6 py-8">

        <header className="mb-8">
          <p className="text-sm font-medium text-muted-foreground">
            MoTA Scholarship Administration
          </p>

          <h1 className="mt-2 text-3xl font-semibold">
            Application dashboard
          </h1>

          <p className="mt-2 text-muted-foreground">
            Monitor applications, verification and review queues.
          </p>
        </header>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">

          {statistics.map((stat) => (
            <Card key={stat.label}>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
              </CardHeader>

              <CardContent>
                <p className="text-3xl font-semibold">
                  {stat.value}
                </p>
              </CardContent>
            </Card>
          ))}

        </div>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Application review</CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-sm text-muted-foreground">
              Review applications and inspect document-level AI validation.
            </p>

            <Link href="/admin/applications">
              <Button className="mt-4">
                View applications
                <ArrowRight />
              </Button>
            </Link>
          </CardContent>
        </Card>

      </div>
    </main>
  );
}