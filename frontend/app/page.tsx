import Link from "next/link";

import { Orbit, Radar, Sparkles, Waypoints } from "lucide-react";

const highlights = [
  {
    title: "Guest-first demos",
    body: "Bootstrap an anonymous session and use the real generation APIs without signing up.",
    icon: Orbit
  },
  {
    title: "Observable workflows",
    body: "Inspect request payloads, responses, cache hits, jobs, and usage events from one workspace.",
    icon: Radar
  },
  {
    title: "Recruiter-friendly UX",
    body: "Everything important is reachable in one flow: brand setup, templates, generation, and analytics.",
    icon: Sparkles
  },
  {
    title: "Backend-grounded scope",
    body: "This frontend exposes the actual capabilities in the repo instead of pretending unsupported RAG systems exist.",
    icon: Waypoints
  }
];

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden bg-white">
      <section className="grid-sheen relative isolate">
        <div className="mx-auto flex max-w-7xl flex-col gap-12 px-6 py-16 sm:px-8 lg:px-10 lg:py-24">
          <div className="flex items-center justify-between gap-6">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-signal">
                ContentGen Demo Surface
              </p>
              <h1 className="mt-4 max-w-4xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-6xl">
                Guest-first AI content generation, exposed as a real integration platform.
              </h1>
            </div>
            <div className="hidden rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-sm font-medium text-slate-600 shadow-panel lg:block">
              Django API + Next.js demo frontend
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="rounded-[2rem] bg-slate-950 p-8 text-slate-50 shadow-panel">
              <p className="max-w-2xl text-lg leading-8 text-slate-300">
                This repo started as a backend-only content generation service. The new frontend turns it
                into a proper recruiter and developer demo surface, centered on guest bootstrap,
                generation workflows, and operational visibility.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <Link
                  href="/workspace"
                  className="rounded-full bg-signal px-6 py-3 text-sm font-semibold text-white transition hover:bg-teal-700"
                >
                  Open Workspace
                </Link>
                <a
                  href="http://localhost:8000/health/"
                  className="rounded-full border border-slate-700 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-500"
                >
                  Inspect Health API
                </a>
              </div>
            </div>

            <div className="rounded-[2rem] bg-slate-100 p-8 shadow-panel">
              <h2 className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                Routes
              </h2>
              <ul className="mt-6 space-y-4 text-sm text-slate-700">
                <li>
                  <span className="font-semibold text-slate-950">/workspace</span>
                  <div>Guest session bootstrap, brands, templates, generation lab, jobs, usage charts.</div>
                </li>
                <li>
                  <span className="font-semibold text-slate-950">/jobs/[jobId]</span>
                  <div>Focused inspection page for output payloads, assets, and regeneration.</div>
                </li>
                <li>
                  <span className="font-semibold text-slate-950">/admin</span>
                  <div>Django admin for operational visibility.</div>
                </li>
              </ul>
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {highlights.map(({ title, body, icon: Icon }) => (
              <div
                key={title}
                className="rounded-[1.75rem] border border-slate-200 bg-white p-6 shadow-panel"
              >
                <Icon className="h-5 w-5 text-signal" />
                <h2 className="mt-4 text-lg font-semibold text-slate-950">{title}</h2>
                <p className="mt-3 text-sm leading-7 text-slate-600">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
