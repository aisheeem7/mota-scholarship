import Link from "next/link";
import {
  ArrowRight,
  FileCheck2,
  HelpCircle,
  Clock3,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function StudentDashboard() {
  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-6xl px-6 py-8">

        {/* Header */}
        <header className="mb-8">
          <p className="text-sm font-medium text-muted-foreground">
            MoTA Scholarship Portal
          </p>

          <h1 className="mt-2 text-3xl font-semibold tracking-tight">
            Welcome back
          </h1>

          <p className="mt-2 text-muted-foreground">
            Track your scholarship application and complete any pending
            requirements.
          </p>
        </header>

        {/* Current application */}
        <Card className="mb-6">
          <CardHeader className="flex flex-row items-start justify-between gap-4">
            <div>
              <CardTitle>Current Application</CardTitle>

              <p className="mt-1 text-sm text-muted-foreground">
                Post-Matric Scholarship
              </p>
            </div>

            <Badge variant="secondary">
              Processing
            </Badge>
          </CardHeader>

          <CardContent>

            {/* Progress */}
            <div className="grid grid-cols-4 gap-2">

              <div>
                <div className="mb-2 h-2 rounded-full bg-foreground" />
                <p className="text-xs font-medium">
                  Submitted
                </p>
              </div>

              <div>
                <div className="mb-2 h-2 rounded-full bg-foreground" />
                <p className="text-xs font-medium">
                  Documents
                </p>
              </div>

              <div>
                <div className="mb-2 h-2 rounded-full bg-muted" />
                <p className="text-xs text-muted-foreground">
                  Verification
                </p>
              </div>

              <div>
                <div className="mb-2 h-2 rounded-full bg-muted" />
                <p className="text-xs text-muted-foreground">
                  Decision
                </p>
              </div>

            </div>

            <div className="mt-6 flex items-start gap-3 rounded-lg border bg-muted/30 p-4">
              <Clock3 className="mt-0.5 h-5 w-5 shrink-0" />

              <div>
                <p className="font-medium">
                  Your documents are being verified.
                </p>

                <p className="mt-1 text-sm text-muted-foreground">
                  You will be notified if any document needs correction
                  or resubmission.
                </p>
              </div>
            </div>

          </CardContent>
        </Card>

        {/* Quick actions */}
        <div className="grid gap-4 md:grid-cols-3">

          <Card>
            <CardHeader>
              <FileCheck2 className="mb-2 h-5 w-5" />

              <CardTitle className="text-base">
                Documents
              </CardTitle>
            </CardHeader>

            <CardContent>
              <p className="text-sm text-muted-foreground">
                3 of 4 required documents uploaded.
              </p>

              <Link href="/student/upload">
                <Button className="mt-4" variant="outline">
                  Review documents
                  <ArrowRight />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Clock3 className="mb-2 h-5 w-5" />

              <CardTitle className="text-base">
                Application status
              </CardTitle>
            </CardHeader>

            <CardContent>
              <p className="text-sm text-muted-foreground">
                View the complete verification timeline.
              </p>

              <Link href="/student/status">
                <Button className="mt-4" variant="outline">
                  View status
                  <ArrowRight />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <HelpCircle className="mb-2 h-5 w-5" />

              <CardTitle className="text-base">
                Need help?
              </CardTitle>
            </CardHeader>

            <CardContent>
              <p className="text-sm text-muted-foreground">
                Get simple explanations about eligibility and documents.
              </p>

              <Button className="mt-4" variant="outline">
                Ask Scholarship AI
              </Button>
            </CardContent>
          </Card>

        </div>

      </div>
    </main>
  );
}