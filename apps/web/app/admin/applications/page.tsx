import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const applications = [
  {
    id: "ST-001",
    name: "Student One",
    scheme: "Post-Matric",
    status: "PROCESSING",
    risk: 21,
  },
  {
    id: "ST-002",
    name: "Student Two",
    scheme: "Pre-Matric",
    status: "APPROVED",
    risk: 8,
  },
  {
    id: "ST-003",
    name: "Student Three",
    scheme: "Top Class",
    status: "FLAGGED_FOR_REVIEW",
    risk: 76,
  },
];

export default function ApplicationsPage() {
  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-7xl px-6 py-8">

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
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3">Application</th>
                    <th className="px-4 py-3">Student</th>
                    <th className="px-4 py-3">Scheme</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Risk</th>
                    <th className="px-4 py-3">Action</th>
                  </tr>
                </thead>

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
                        {application.name}
                      </td>

                      <td className="px-4 py-4">
                        {application.scheme}
                      </td>

                      <td className="px-4 py-4">
                        <Badge variant="secondary">
                          {application.status}
                        </Badge>
                      </td>

                      <td className="px-4 py-4">
                        {application.risk}%
                      </td>

                      <td className="px-4 py-4">
                        <Link
                          href={`/admin/applications/${application.id}`}
                        >
                          <Button variant="outline" size="sm">
                            Review
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

      </div>
    </main>
  );
}