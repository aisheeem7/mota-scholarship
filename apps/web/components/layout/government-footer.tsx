import { useLanguage } from "@/components/layout/language-provider";

export function GovernmentFooter() {
  const { t } = useLanguage();

  return (
    <footer className="gov-footer">
      <div className="gov-container px-4 py-6 sm:px-6">
        <p className="text-sm font-semibold text-slate-800">{t("footerText")}</p>
        <p className="mt-1 text-xs leading-5 text-slate-600">{t("govInspired")}</p>
        <p className="mt-3 text-xs font-medium text-slate-500">{t("prototypeNotice")}</p>
      </div>
    </footer>
  );
}
