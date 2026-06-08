import Link from "next/link";

import { JobInspector } from "@/components/job-inspector";

export default async function JobDetailPage({
  params
}: {
  params: Promise<{ jobId: string }>;
}) {
  const { jobId } = await params;

  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,_#f8fafc_0%,_#edf7f5_100%)]">
      <div className="mx-auto max-w-6xl px-6 py-10 sm:px-8 lg:px-10">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-teal-700">
              Job inspector
            </p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-950">
              Generation job detail
            </h1>
          </div>
          <Link
            href="/workspace"
            className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-950"
          >
            Back to workspace
          </Link>
        </div>

        <JobInspector jobId={jobId} />
      </div>
    </main>
  );
}
