import { AnssiChecklist } from "./components/AnssiChecklist";
import { BreachResultCard } from "./components/BreachResultCard";
import { PasswordForm } from "./components/PasswordForm";
import { PrivacyExplainer } from "./components/PrivacyExplainer";
import { usePasswordAnalysis } from "./hooks/usePasswordAnalysis";

export default function App() {
  const { loading, error, result, analyze } = usePasswordAnalysis();

  return (
    <div className="min-h-screen bg-ink">
      <div className="mx-auto flex max-w-2xl flex-col gap-8 px-6 py-16">
        <header>
          <p className="mb-2 font-mono text-xs uppercase tracking-[0.2em] text-signal-soft">
            RockYou Checker
          </p>
          <h1 className="text-3xl font-bold tracking-tight text-slate-50 sm:text-4xl">
            Votre mot de passe est-il déjà compromis ?
          </h1>
          <p className="mt-3 text-slate-400">
            Vérifiez-le face au corpus de fuite RockYou et aux recommandations de
            l'ANSSI - sans jamais que votre mot de passe ne quitte votre navigateur.
          </p>
        </header>

        <PasswordForm onSubmit={analyze} loading={loading} />

        {error && (
          <div className="rounded-lg border border-alert/40 bg-alert/10 px-4 py-3 text-sm text-alert">
            {error}
          </div>
        )}

        {result && (
          <div className="flex flex-col gap-4">
            <BreachResultCard breach={result.breach} />
            <AnssiChecklist anssi={result.anssi} />
          </div>
        )}

        <PrivacyExplainer />

        <footer className="pt-4 text-center text-xs text-slate-600">
          Inspiré de{" "}
          <a
            href="https://haveibeenpwned.com/Passwords"
            target="_blank"
            rel="noreferrer"
            className="underline decoration-dotted hover:text-slate-400"
          >
            Have I Been Pwned
          </a>
          . Corpus : RockYou (2009).
        </footer>
      </div>
    </div>
  );
}
