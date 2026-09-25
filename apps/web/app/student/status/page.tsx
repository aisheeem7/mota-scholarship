import {
  CheckCircle2,
  Circle,
  Clock3,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const steps = [
  {
    title: "Application submitted",
    description: "Your application was successfully submitted.",
    complete: true,
  },
  {
    title: "Documents processing",
    description: "Uploaded documents are being processed.",
    complete: true,
  },
  {
    title: "Verification",
    description: "Eligibility and documents are being verified.",
    current: true,
  },
  {
    title: "Decision",
    description: "Final scholarship decision.",
  },
  {
    title: "DBT",
    description: "Scholarship amount transferred through DBT.",
  },
];

export default function StatusPage() {
  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-4xl px-6 py-8">

        <header className="mb-8">
          <p className="text-sm font-medium text-muted-foreground">
            MoTA Scholarship Portal
          </p>

          <h1 className="mt-2 text-3xl font-semibold">
            Application status
          </h1>
        </header>

        <Card>
          <CardHeader className="flex flex-row items-start justify-between">
            <div>
              <CardTitle>Application ST-001</CardTitle>

              <p className="mt-1 text-sm text-muted-foreground">
                Post-Matric Scholarship
              </p>
            </div>

            <Badge variant="secondary">
              Processing
            </Badge>
          </CardHeader>

          <CardContent>
            <div className="space-y-8">

              {steps.map((step, index) => (
                <div
                  key={step.title}
                  className="flex gap-4"
                >
                  <div className="flex flex-col items-center">

                    {step.complete ? (
                      <CheckCircle2 className="h-6 w-6" />
                    ) : step.current ? (
                      <Clock3 className="h-6 w-6" />
                    ) : (
                      <Circle className="h-6 w-6 text-muted-foreground" />
                    )}

                    {index !== steps.length - 1 && (
                      <div className="mt-2 h-10 w-px bg-border" />
                    )}

                  </div>

                  <div>
                    <p className="font-medium">
                      {step.title}
                    </p>

                    <p className="mt-1 text-sm text-muted-foreground">
                      {step.description}
                    </p>

                    {step.current && (
                      <p className="mt-2 text-sm font-medium">
                        Currently in progress
                      </p>
                    )}
                  </div>
                </div>
              ))}

            </div>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Why is my application being checked?</CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-sm leading-6 text-muted-foreground">
              Your documents are checked against the eligibility rules
              configured for your scholarship scheme. If something is
              unclear or does not match, you will see the reason and the
              required next step.
            </p>
          </CardContent>
        </Card>

      </div>
    </main>
  );
}