import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/components/layout/language-provider";



export default function AdminDashboard() {
  const { t } = useLanguage();
  const statistics = [
    { label: t("totalApplications"), value: "1,248" },
    { label: t("processing"), value: "326" },
    { label: t("approved"), value: "714" },
    { label: t("deficient"), value: "142" },
    { label: t("flaggedForReview"), value: "66" },
  ];

  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-7xl px-6 py-8">

        <header className="mb-8">
          <p className="text-sm font-medium text-muted-foreground">
            {t("ministry")}
          </p>

          <h1 className="mt-2 text-3xl font-semibold">
            {t("applicationDashboard")}
          </h1>

          <p className="mt-2 text-muted-foreground">
            {t("dashboardDescription")}
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
            <CardTitle>{t("applicationReview")}</CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-sm text-muted-foreground">
              {t("reviewDescription")}
            </p>

            <Link href="/admin/applications">
              <Button className="mt-4">
                {t("viewApplications")}
                <ArrowRight />
              </Button>
            </Link>
          </CardContent>
        </Card>

      </div>
    </main>
  );
}