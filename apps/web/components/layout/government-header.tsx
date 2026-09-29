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
        <div className="gov-container flex h-full items-center justify-between gap-6 px-4 sm:px-6">
          <Link
            href="/"
            className="flex min-w-0 max-w-[42rem] flex-col items-start gap-1.5"
            aria-label="TRISETU home"
          >
            <Image
              src="/trisetu-logo.png"
              alt="TRISETU"
              width={220}
              height={110}
              priority
              className="h-auto w-[135px] max-w-full object-contain object-left sm:w-[155px]"
            />
            <p className="max-w-[32rem] break-words text-[11px] font-medium leading-4 text-slate-600 sm:text-xs sm:leading-4">
              {t("subtitle")}
            </p>
          </Link>

          <div className="hidden max-w-[23rem] text-right sm:block">
            <p className="text-xs font-semibold leading-4 text-slate-700 sm:text-sm">{t("ministry")}</p>
            <p className="mt-0.5 text-[10px] leading-4 text-slate-500 sm:text-xs">{t("prototypeNotice")}</p>
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
