export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl items-center px-6 py-16">
      <section className="space-y-5">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-teal-700">
          MediTag
        </p>
        <h1 className="text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
          Emergency information when it matters.
        </h1>
        <p className="max-w-2xl text-lg leading-8 text-slate-600">
          The web foundation is ready. Public tag pages, citizen tools, and
          verified-doctor access will be added in later sessions.
        </p>
      </section>
    </main>
  );
}
