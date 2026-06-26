export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col items-center justify-center px-6 text-center">
        <p className="mb-4 rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-300">
          Verified aid requests • Volunteer verification • Donor fulfillment
        </p>

        <h1 className="max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl">
          AidFlow Verify
        </h1>

        <p className="mt-6 max-w-2xl text-lg text-slate-300">
          A full-stack platform where requesters submit essential aid requests,
          admins review them, volunteers verify them, and donors fulfill verified
          needs with proof tracking.
        </p>

        <div className="mt-8 flex flex-col gap-4 sm:flex-row">
          <a
            href="/register"
            className="rounded-lg bg-white px-6 py-3 font-semibold text-slate-950 hover:bg-slate-200"
          >
            Create Account
          </a>

          <a
            href="/login"
            className="rounded-lg border border-slate-600 px-6 py-3 font-semibold text-white hover:bg-slate-900"
          >
            Login
          </a>
        </div>
      </section>
    </main>
  );
}