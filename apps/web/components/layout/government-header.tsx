"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { LANGUAGE_LABELS, useLanguage } from "@/components/layout/language-provider";
import type { Language } from "@/lib/i18n";

export function GovernmentHeader() {
  const pathname = usePathname();
  const { language, setLanguage, t } = useLanguage();

  return (
    <>
      <a href="#main-content" className="skip-link">{t("skipToContent")}</a>
      <div className="gov-topbar">
        <div className="gov-container flex min-h-9 items-center justify-between gap-3 px-4 text-xs sm:px-6">
          <span>{t("prototype")}</span>
          <div className="flex items-center gap-1" aria-label={t("language")}>
            {(Object.keys(LANGUAGE_LABELS) as Language[]).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setLanguage(item)}
                aria-pressed={language === item}
                className={"gov-language-button " + (language === item ? "gov-language-active" : "")}
              >
                {LANGUAGE_LABELS[item]}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="gov-tricolor" aria-hidden="true" />

      <header className="gov-masthead">
        <div className="gov-container flex min-h-24 items-center justify-between gap-6 px-4 py-4 sm:px-6">
          <Link href="/" className="flex min-w-0 items-center gap-3" aria-label="TRISETU home">
            <Image
              src="/trisetu-logo.svg"
              alt="TRISETU"
              width={78}
              height={78}
              priority
              className="h-16 w-[150px] object-contain object-left sm:h-[72px] sm:w-[170px]"
            />
            <div className="min-w-0">
              <p className="text-xl font-bold tracking-tight text-[#183b73] sm:text-2xl">{t("title")}</p>
              <p className="mt-0.5 max-w-2xl text-xs leading-5 text-slate-600 sm:text-sm">{t("subtitle")}</p>
            </div>
          </Link>

          <div className="hidden text-right sm:block">
            <p className="text-sm font-semibold text-slate-700">{t("ministry")}</p>
            <p className="mt-1 text-xs text-slate-500">{t("prototypeNotice")}</p>
          </div>
        </div>
      </header>

      <nav className="gov-nav" aria-label="Primary navigation">
        <div className="gov-container flex min-h-11 items-center gap-1 overflow-x-auto px-4 sm:px-6">
          <Link className={"gov-nav-link " + (pathname === "/" ? "gov-nav-active" : "")} href="/">{t("home")}</Link>
          <Link className={"gov-nav-link " + (pathname.startsWith("/student") ? "gov-nav-active" : "")} href="/student/upload">{t("studentPortal")}</Link>
          <Link className={"gov-nav-link " + (pathname === "/admin" ? "gov-nav-active" : "")} href="/admin">{t("adminPortal")}</Link>
          <Link className={"gov-nav-link " + (pathname.startsWith("/admin/applications") ? "gov-nav-active" : "")} href="/admin/applications">{t("applications")}</Link>
        </div>
      </nav>
    </>
  );
}
