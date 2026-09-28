"use client";

import Link from "next/link";
import { ArrowRight, FileCheck2, ShieldCheck } from "lucide-react";

import { useLanguage } from "@/components/layout/language-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  const { t } = useLanguage();

  return (
    <main className="min-h-screen bg-muted/30">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:py-14">
        <section className="rounded-md border bg-white p-6 shadow-sm sm:p-10">
          <p className="text-sm font-semibold uppercase tracking-wide text-[#b45f13]">
            {t("prototype")}
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-[#183b73] sm:text-4xl">
            {t("title")}
          </h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">
            {t("subtitle")}
          </p>

          <div className="mt-7 flex flex-wrap gap-3">
            <Link href="/student/upload">
              <Button>
                {t("studentPortal")}
                <ArrowRight />
              </Button>
            </Link>
            <Link href="/admin">
              <Button variant="outline">{t("adminPortal")}</Button>
            </Link>
          </div>
        </section>

        <section className="mt-6 grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileCheck2 className="h-5 w-5 text-[#183b73]" />
                {t("applicationVerification")}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm leading-6 text-muted-foreground">
              {t("reviewDescription")}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-[#183b73]" />
                {t("humanReview")}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm leading-6 text-muted-foreground">
              {t("flaggedReview")}
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}
