"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, Image as ImageIcon, RefreshCcw, TimerReset } from "lucide-react";

import { platformApi } from "@/lib/api";
import { cn } from "@/lib/utils";

export function JobInspector({ jobId }: { jobId: string }) {
  const queryClient = useQueryClient();
  const jobQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => platformApi.jobs.detail(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "queued" || status === "running" ? 4000 : false;
    }
  });

  const regenerateMutation = useMutation({
    mutationFn: () => platformApi.jobs.regenerate(jobId),
    onSuccess: async (payload) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["jobs"] }),
        queryClient.invalidateQueries({ queryKey: ["job", jobId] }),
        queryClient.invalidateQueries({ queryKey: ["job", payload.job_id] }),
        queryClient.invalidateQueries({ queryKey: ["usage"] })
      ]);
    }
  });

  if (jobQuery.isPending) {
    return <Shell>Loading job details...</Shell>;
  }

  if (jobQuery.isError || !jobQuery.data) {
    return <Shell>Unable to load this job. Confirm the guest session or token matches the owner.</Shell>;
  }

  const job = jobQuery.data;
  const variants = Array.isArray(job.output_payload?.variants)
    ? (job.output_payload.variants as Array<Record<string, unknown>>)
    : [];

  return (
    <div className="grid gap-6 xl:grid-cols-[0.72fr_0.28fr]">
      <div className="space-y-6">
        <section className="rounded-[2rem] border border-white/70 bg-white p-6 shadow-panel">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                Job id
              </p>
              <h2 className="mt-2 break-all text-2xl font-semibold text-slate-950">{job.id}</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              <StatusPill status={job.status} />
              {job.cache_hit ? <Flag text="Cache hit" /> : null}
              {job.include_image ? <Flag text="Image enabled" /> : null}
            </div>
          </div>

          <dl className="mt-6 grid gap-4 rounded-[1.5rem] bg-slate-50 p-5 text-sm sm:grid-cols-2">
            <Meta label="Model" value={job.model_name || "Pending"} />
            <Meta label="Completed" value={formatDateTime(job.completed_at)} />
            <Meta label="Created" value={formatDateTime(job.created_at)} />
            <Meta label="Updated" value={formatDateTime(job.updated_at)} />
          </dl>

          <div className="mt-6 flex flex-wrap items-center gap-4">
            <button
              type="button"
              onClick={() => jobQuery.refetch()}
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-950"
            >
              <RefreshCcw className="h-4 w-4" />
              Refresh status
            </button>
            <button
              type="button"
              onClick={() => regenerateMutation.mutate()}
              disabled={regenerateMutation.isPending}
              className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <TimerReset className="h-4 w-4" />
              {regenerateMutation.isPending ? "Submitting..." : "Regenerate"}
            </button>
            {regenerateMutation.data ? (
              <span className="text-sm text-teal-700">
                New job queued: <span className="font-semibold">{regenerateMutation.data.job_id}</span>
              </span>
            ) : null}
          </div>

          {job.error_message ? (
            <div className="mt-6 rounded-[1.3rem] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
              {job.error_message}
            </div>
          ) : null}
        </section>

        <section className="rounded-[2rem] border border-white/70 bg-white p-6 shadow-panel">
          <h3 className="text-lg font-semibold text-slate-950">Output payload</h3>
          <p className="mt-2 text-sm leading-7 text-slate-600">
            Raw backend payload, useful for tracing exact generation responses and downstream consumers.
          </p>
          <pre className="mt-4 max-h-[34rem] overflow-auto">{JSON.stringify(job.output_payload, null, 2)}</pre>
        </section>

        <section className="rounded-[2rem] border border-white/70 bg-white p-6 shadow-panel">
          <h3 className="text-lg font-semibold text-slate-950">Human-readable variants</h3>
          <div className="mt-5 space-y-4">
            {variants.length === 0 ? (
              <div className="rounded-[1.4rem] border border-dashed border-slate-300 bg-slate-50 px-6 py-8 text-sm text-slate-600">
                No normalized `variants` array was present in this job output. Use the raw payload above.
              </div>
            ) : (
              variants.map((variant, index) => (
                <article key={`${job.id}-${index}`} className="rounded-[1.4rem] border border-slate-200 bg-slate-50 p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Variant {index + 1}
                  </p>
                  <pre className="mt-3 overflow-auto">{JSON.stringify(variant, null, 2)}</pre>
                </article>
              ))
            )}
          </div>
        </section>
      </div>

      <div className="space-y-6">
        <section className="rounded-[2rem] border border-white/70 bg-white p-6 shadow-panel">
          <h3 className="text-lg font-semibold text-slate-950">Assets</h3>
          <div className="mt-5 space-y-4">
            {job.assets.length === 0 ? (
              <div className="rounded-[1.4rem] border border-dashed border-slate-300 bg-slate-50 px-5 py-8 text-sm text-slate-600">
                No assets attached to this job.
              </div>
            ) : (
              job.assets.map((asset) => (
                <div key={asset.id} className="rounded-[1.4rem] border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-start gap-3">
                    <div className="rounded-xl bg-white p-2 shadow-sm">
                      <ImageIcon className="h-4 w-4 text-slate-700" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-slate-950">{asset.asset_type}</p>
                      <p className="mt-1 break-all text-xs text-slate-500">{asset.mime_type}</p>
                    </div>
                  </div>
                  <a
                    href={asset.storage_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-4 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-950"
                  >
                    <Download className="h-4 w-4" />
                    Open asset
                  </a>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="rounded-[2rem] border border-white/70 bg-white p-6 shadow-panel">
          <h3 className="text-lg font-semibold text-slate-950">Request references</h3>
          <dl className="mt-5 grid gap-4 rounded-[1.5rem] bg-slate-50 p-5 text-sm">
            <Meta label="Brand profile" value={job.brand_profile_id} mono />
            <Meta label="Template" value={job.template_id ?? "No template"} mono />
          </dl>
        </section>
      </div>
    </div>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-[2rem] border border-white/70 bg-white p-6 shadow-panel text-sm text-slate-700">
      {children}
    </div>
  );
}

function Meta({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</dt>
      <dd className={cn("mt-1 text-sm text-slate-900", mono && "font-mono text-xs sm:text-sm")}>{value}</dd>
    </div>
  );
}

function StatusPill({ status }: { status: string }) {
  const tone =
    status === "succeeded"
      ? "bg-emerald-100 text-emerald-700"
      : status === "failed"
        ? "bg-rose-100 text-rose-700"
        : status === "running"
          ? "bg-amber-100 text-amber-700"
          : "bg-slate-100 text-slate-700";
  return <span className={cn("rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em]", tone)}>{status}</span>;
}

function Flag({ text }: { text: string }) {
  return <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-slate-700">{text}</span>;
}

function formatDateTime(value: string | null) {
  if (!value) {
    return "Unavailable";
  }
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
