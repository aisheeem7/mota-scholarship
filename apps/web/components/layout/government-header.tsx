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
        <div className="gov-container flex h-8 items-center justify-between gap-3 px-4 sm:px-6">
          <span className="min-w-0 truncate">{t("prototypeNotice")}</span>
          <div className="gov-language-switch" role="group" aria-label={t("language")}>
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
        <div className="gov-container flex items-center justify-between gap-6 px-4 py-2 sm:px-6">
          <Link href="/" className="gov-brand" aria-label="TRISETU home">
            <Image
              src="/trisetu-logo-mark.png"
              alt="TRISETU"
              width={1186}
              height={550}
              priority
              className="gov-brand-logo"
            />
            <span className="gov-brand-divider" aria-hidden="true" />
            <span className="gov-brand-text">
              <span className="gov-brand-ministry">{t("ministry")}</span>
              <span className="gov-brand-subtitle">{t("subtitle")}</span>
            </span>
          </Link>

          <div className="hidden shrink-0 lg:block">
            <span className="gov-masthead-badge">{t("prototype")}</span>
          </div>
        </div>
      </header>

      <nav className="gov-nav" aria-label="Primary navigation">
        <div className="gov-container flex items-center gap-0.5 overflow-x-auto px-2 sm:px-4">
          <Link className={"gov-nav-link " + (pathname === "/" ? "gov-nav-active" : "")} href="/">{t("home")}</Link>
          <Link className={"gov-nav-link " + (pathname.startsWith("/student") ? "gov-nav-active" : "")} href="/student/upload">{t("studentPortal")}</Link>
          <Link className={"gov-nav-link " + (pathname === "/admin" ? "gov-nav-active" : "")} href="/admin">{t("adminPortal")}</Link>
          <Link className={"gov-nav-link " + (pathname.startsWith("/admin/applications") ? "gov-nav-active" : "")} href="/admin/applications">{t("applications")}</Link>
        </div>
      </nav>
    </>
  );
}
