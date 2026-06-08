"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BarChart3, Bot, Boxes, DatabaseZap, Fingerprint, Gauge, History, Radar, RefreshCcw, Send, ShieldCheck, Sparkles } from "lucide-react";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { guestApi, platformApi } from "@/lib/api";
import { STORAGE_KEYS } from "@/lib/config";
import { useAppStore } from "@/lib/store";
import { cn } from "@/lib/utils";

const brandSchema = z.object({
  brand_name: z.string().min(2).max(255),
  preferred_tone: z.string().min(2).max(64),
  brand_voice: z.string().min(20),
  product_description: z.string().min(20),
  target_audience: z.string().min(10),
  example_copy: z.string().max(5000).default(""),
  banned_phrases_text: z.string().default("")
});

const templateSchema = z.object({
  name: z.string().min(2).max(255),
  channel: z.enum(["social", "ads", "email", "landing_page", "campaign"]),
  objective: z.enum(["lead_generation", "awareness", "conversion", "retention", "product_launch"]),
  prompt_template: z.string().min(20)
});

const generationSchema = z.object({
  brand_profile_id: z.string().uuid(),
  template_id: z.string().uuid().optional().or(z.literal("")),
  channel: z.enum(["linkedin", "x", "instagram", "facebook", "email", "landing_page", "ad"]),
  objective: z.string().min(2).max(100),
  tone: z.string().min(2).max(100),
  audience: z.string().min(5).max(200),
  product_description: z.string().min(20).max(2000),
  key_points_text: z.string().min(5),
  cta: z.string().min(2).max(200),
  output_count: z.coerce.number().min(1).max(10),
  include_image: z.boolean().default(false),
  length: z.enum(["short", "medium", "long"])
});

type BrandFormValues = z.infer<typeof brandSchema>;
type TemplateFormValues = z.infer<typeof templateSchema>;
type GenerationFormValues = z.infer<typeof generationSchema>;

const generationChannels = [
  ["linkedin", "LinkedIn"],
  ["x", "X"],
  ["instagram", "Instagram"],
  ["facebook", "Facebook"],
  ["email", "Email"],
  ["landing_page", "Landing Page"],
  ["ad", "Ad"]
] as const;

const templateChannels = [
  ["social", "Social"],
  ["ads", "Ads"],
  ["email", "Email"],
  ["landing_page", "Landing Page"],
  ["campaign", "Campaign"]
] as const;

const templateObjectives = [
  ["lead_generation", "Lead generation"],
  ["awareness", "Awareness"],
  ["conversion", "Conversion"],
  ["retention", "Retention"],
  ["product_launch", "Product launch"]
] as const;

export function WorkspaceShell() {
  const queryClient = useQueryClient();
  const { guest, setGuest, lastRequest, lastResponse } = useAppStore();
  const bootstrapStarted = useRef(false);

  const bootstrapMutation = useMutation({
    mutationFn: async () => {
      if (typeof window === "undefined") {
        return guestApi.bootstrap();
      }
      const stored = window.localStorage.getItem(STORAGE_KEYS.guestSession);
      if (stored) {
        const parsed = JSON.parse(stored) as { session: { guest_id: string; session_id: string; device_id: string } };
        return guestApi.bootstrap(parsed.session);
      }
      return guestApi.bootstrap();
    },
    onSuccess: (payload) => {
      setGuest(payload);
      if (typeof window !== "undefined") {
        window.localStorage.setItem(STORAGE_KEYS.guestSession, JSON.stringify(payload));
      }
    },
    onError: () => {
      bootstrapStarted.current = false;
    }
  });

  useEffect(() => {
    if (!guest && !bootstrapStarted.current && bootstrapMutation.status === "idle") {
      bootstrapStarted.current = true;
      bootstrapMutation.mutate();
    }
  }, [guest, bootstrapMutation]);

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: platformApi.health
  });

  const brandsQuery = useQuery({
    queryKey: ["brands"],
    queryFn: platformApi.brands.list,
    enabled: Boolean(guest)
  });

  const templatesQuery = useQuery({
    queryKey: ["templates"],
    queryFn: platformApi.templates.list,
    enabled: Boolean(guest)
  });

  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: platformApi.jobs.list,
    enabled: Boolean(guest),
    refetchInterval: 8000
  });

  const usageQuery = useQuery({
    queryKey: ["usage"],
    queryFn: platformApi.usage.list,
    enabled: Boolean(guest)
  });

  const brandForm = useForm<BrandFormValues>({
    resolver: zodResolver(brandSchema),
    defaultValues: {
      brand_name: "Northstar AI",
      preferred_tone: "Confident and clear",
      brand_voice: "Technical, strategic, and pragmatic without sounding dry.",
      product_description: "A content operations platform for marketers shipping campaigns with AI assistance.",
      target_audience: "B2B marketing leaders and growth teams.",
      example_copy: "Launch sharper campaigns without endless revision loops.",
      banned_phrases_text: "synergy, disrupt"
    }
  });

  const templateForm = useForm<TemplateFormValues>({
    resolver: zodResolver(templateSchema),
    defaultValues: {
      name: "Launch Email Sequence",
      channel: "email",
      objective: "product_launch",
      prompt_template: "Create persuasive launch copy with a clear CTA, concise structure, and credible proof points."
    }
  });

  const generationForm = useForm<GenerationFormValues>({
    resolver: zodResolver(generationSchema),
    defaultValues: {
      brand_profile_id: "",
      template_id: "",
      channel: "linkedin",
      objective: "Drive demo requests",
      tone: "Crisp and ambitious",
      audience: "Demand generation managers at mid-market SaaS companies",
      product_description: "An AI workspace that centralizes brand context, template management, and async generation jobs.",
      key_points_text: "Guest-first demo flow\nOperational visibility\nBrand-aware generation",
      cta: "Book a product walkthrough",
      output_count: 3,
      include_image: false,
      length: "medium"
    }
  });

  useEffect(() => {
    const firstBrand = brandsQuery.data?.results[0];
    if (firstBrand && !generationForm.getValues("brand_profile_id")) {
      generationForm.setValue("brand_profile_id", firstBrand.id, {
        shouldDirty: false,
        shouldTouch: false
      });
    }
  }, [brandsQuery.data, generationForm]);

  useEffect(() => {
    const firstTemplate = templatesQuery.data?.results[0];
    if (firstTemplate && !generationForm.getValues("template_id")) {
      generationForm.setValue("template_id", firstTemplate.id, {
        shouldDirty: false,
        shouldTouch: false
      });
    }
  }, [templatesQuery.data, generationForm]);

  const createBrandMutation = useMutation({
    mutationFn: (values: BrandFormValues) =>
      platformApi.brands.create({
        brand_name: values.brand_name,
        preferred_tone: values.preferred_tone,
        brand_voice: values.brand_voice,
        product_description: values.product_description,
        target_audience: values.target_audience,
        example_copy: values.example_copy,
        banned_phrases: values.banned_phrases_text
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean)
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["brands"] });
      brandForm.reset(brandForm.getValues());
    }
  });

  const createTemplateMutation = useMutation({
    mutationFn: platformApi.templates.create,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["templates"] });
      templateForm.reset(templateForm.getValues());
    }
  });

  const generateMutation = useMutation({
    mutationFn: (values: GenerationFormValues) =>
      platformApi.generate({
        brand_profile_id: values.brand_profile_id,
        template_id: values.template_id || null,
        channel: values.channel,
        objective: values.objective,
        tone: values.tone,
        audience: values.audience,
        product_description: values.product_description,
        key_points: values.key_points_text
          .split("\n")
          .map((item) => item.trim())
          .filter(Boolean),
        cta: values.cta,
        output_count: values.output_count,
        include_image: values.include_image,
        length: values.length
      }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["jobs"] }),
        queryClient.invalidateQueries({ queryKey: ["usage"] })
      ]);
    }
  });

  const usageChartData =
    usageQuery.data?.results
      ?.slice()
      .reverse()
      .map((event, index) => ({
        name: `#${index + 1}`,
        tokens: event.tokens_in + event.tokens_out,
        latency: event.latency_ms
      })) ?? [];

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(20,184,166,0.14),_transparent_28%),linear-gradient(180deg,_#f8fafc_0%,_#eef6f6_100%)]">
      <div className="mx-auto max-w-7xl px-6 py-10 sm:px-8 lg:px-10">
        <section className="rounded-[2rem] border border-white/70 bg-slate-950 px-8 py-8 text-slate-50 shadow-panel">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-teal-300">
                Guest-first workspace
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                Use the actual platform without a login wall.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-8 text-slate-300">
                This dashboard is intentionally scoped to the real backend in this repo: anonymous
                session bootstrap, brand context, reusable templates, queued jobs, generation
                outputs, and usage telemetry.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <StatusBadge
                label="Health"
                value={healthQuery.data?.status ?? (healthQuery.isPending ? "checking" : "unknown")}
                tone={healthQuery.data?.status === "ok" ? "good" : "warn"}
                icon={ShieldCheck}
              />
              <StatusBadge
                label="Guest Session"
                value={guest?.session.guest_id ?? (bootstrapMutation.isPending ? "bootstrapping" : "pending")}
                tone={guest ? "good" : "warn"}
                icon={Fingerprint}
              />
            </div>
          </div>
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <div className="space-y-6">
            <Panel
              title="Session and limits"
              icon={DatabaseZap}
              subtitle="Guest identity is persisted in browser storage and refreshed against the backend on each visit."
            >
              <div className="grid gap-4 md:grid-cols-3">
                <MetricCard label="Brands" value={`${guest?.limits.brands_used ?? 0} / ${guest?.limits.brands_soft_limit ?? "-"}`} />
                <MetricCard label="Templates" value={`${guest?.limits.templates_used ?? 0} / ${guest?.limits.templates_soft_limit ?? "-"}`} />
                <MetricCard label="Generations" value={`${guest?.limits.generations_used ?? 0} / ${guest?.limits.generations_soft_limit ?? "-"}`} />
              </div>
              {guest ? (
                <dl className="mt-6 grid gap-3 rounded-[1.5rem] bg-slate-100 p-5 text-sm text-slate-700 sm:grid-cols-2">
                  <Detail label="Guest ID" value={guest.session.guest_id} mono />
                  <Detail label="Session ID" value={guest.session.session_id} mono />
                  <Detail label="Device ID" value={guest.session.device_id} mono />
                  <Detail label="Expires" value={formatDateTime(guest.session.expires_at)} />
                </dl>
              ) : null}
            </Panel>

            <Panel
              title="Generation lab"
              icon={Sparkles}
              subtitle="Submit real content generation requests against the backend queue with optional template guidance."
            >
              <form
                className="grid gap-4"
                onSubmit={generationForm.handleSubmit((values) => generateMutation.mutate(values))}
              >
                <div className="grid gap-4 md:grid-cols-2">
                  <SelectField
                    label="Brand profile"
                    error={generationForm.formState.errors.brand_profile_id?.message}
                    {...generationForm.register("brand_profile_id")}
                  >
                    <option value="">Select a brand</option>
                    {(brandsQuery.data?.results ?? []).map((brand) => (
                      <option key={brand.id} value={brand.id}>
                        {brand.brand_name}
                      </option>
                    ))}
                  </SelectField>

                  <SelectField
                    label="Template"
                    error={generationForm.formState.errors.template_id?.message}
                    {...generationForm.register("template_id")}
                  >
                    <option value="">No template</option>
                    {(templatesQuery.data?.results ?? []).map((template) => (
                      <option key={template.id} value={template.id}>
                        {template.name}
                      </option>
                    ))}
                  </SelectField>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <SelectField
                    label="Delivery channel"
                    error={generationForm.formState.errors.channel?.message}
                    {...generationForm.register("channel")}
                  >
                    {generationChannels.map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </SelectField>
                  <FormField
                    label="Objective"
                    error={generationForm.formState.errors.objective?.message}
                    {...generationForm.register("objective")}
                  />
                  <FormField
                    label="Tone"
                    error={generationForm.formState.errors.tone?.message}
                    {...generationForm.register("tone")}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <FormField
                    label="Audience"
                    error={generationForm.formState.errors.audience?.message}
                    {...generationForm.register("audience")}
                  />
                  <FormField
                    label="Call to action"
                    error={generationForm.formState.errors.cta?.message}
                    {...generationForm.register("cta")}
                  />
                </div>

                <TextAreaField
                  label="Product description"
                  error={generationForm.formState.errors.product_description?.message}
                  rows={4}
                  {...generationForm.register("product_description")}
                />

                <TextAreaField
                  label="Key points"
                  hint="Use one point per line."
                  error={generationForm.formState.errors.key_points_text?.message}
                  rows={4}
                  {...generationForm.register("key_points_text")}
                />

                <div className="grid gap-4 md:grid-cols-3">
                  <FormField
                    label="Output count"
                    type="number"
                    min="1"
                    max="10"
                    error={generationForm.formState.errors.output_count?.message}
                    {...generationForm.register("output_count")}
                  />
                  <SelectField
                    label="Length"
                    error={generationForm.formState.errors.length?.message}
                    {...generationForm.register("length")}
                  >
                    <option value="short">Short</option>
                    <option value="medium">Medium</option>
                    <option value="long">Long</option>
                  </SelectField>
                  <Controller
                    name="include_image"
                    control={generationForm.control}
                    render={({ field }) => (
                      <label className="flex items-center justify-between rounded-[1.25rem] border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                        <span className="font-medium text-slate-900">Also generate image</span>
                        <input
                          type="checkbox"
                          checked={field.value}
                          onChange={(event) => field.onChange(event.target.checked)}
                          className="h-4 w-4 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                        />
                      </label>
                    )}
                  />
                </div>

                <div className="flex flex-wrap items-center gap-4">
                  <button
                    type="submit"
                    disabled={generateMutation.isPending}
                    className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    <Send className="h-4 w-4" />
                    {generateMutation.isPending ? "Submitting..." : "Queue generation"}
                  </button>
                  {generateMutation.data ? (
                    <Link
                      href={`/jobs/${generateMutation.data.job_id}`}
                      className="text-sm font-semibold text-teal-700 transition hover:text-teal-800"
                    >
                      Inspect latest job
                    </Link>
                  ) : null}
                  {generateMutation.isSuccess && generateMutation.data ? (
                    <span className="rounded-full bg-teal-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-teal-700">
                      {generateMutation.data.deduplicated ? "Deduplicated" : generateMutation.data.cache_hit ? "Cache hit" : "Queued"}
                    </span>
                  ) : null}
                </div>

                {generateMutation.error ? <ErrorText message={String(generateMutation.error.message)} /> : null}
              </form>
            </Panel>

            <Panel
              title="Jobs timeline"
              icon={History}
              subtitle="Inspect real queued, running, failed, and completed jobs produced by this guest session."
            >
              <div className="space-y-3">
                {(jobsQuery.data?.results ?? []).length === 0 ? (
                  <EmptyState title="No jobs yet" body="Submit a generation request to see outputs, status transitions, and assets." />
                ) : (
                  jobsQuery.data?.results.map((job) => (
                    <Link
                      key={job.id}
                      href={`/jobs/${job.id}`}
                      className="block rounded-[1.4rem] border border-slate-200 bg-white p-5 transition hover:-translate-y-0.5 hover:border-teal-300 hover:shadow-panel"
                    >
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                            {job.model_name || "Pending model selection"}
                          </p>
                          <h3 className="mt-2 text-base font-semibold text-slate-950">{job.id}</h3>
                          <p className="mt-2 text-sm text-slate-600">
                            Created {formatDateTime(job.created_at)} · {job.include_image ? "Text + image" : "Text only"}
                          </p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <JobPill status={job.status} />
                          {job.cache_hit ? <FlagPill text="Cache hit" /> : null}
                          {job.assets.length > 0 ? <FlagPill text={`${job.assets.length} asset`} /> : null}
                        </div>
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </Panel>
          </div>

          <div className="space-y-6">
            <Panel
              title="Brand library"
              icon={Boxes}
              subtitle="Brand inputs are reusable across jobs and migrate automatically if the guest later registers."
            >
              <form
                className="grid gap-3"
                onSubmit={brandForm.handleSubmit((values) => createBrandMutation.mutate(values))}
              >
                <FormField label="Brand name" error={brandForm.formState.errors.brand_name?.message} {...brandForm.register("brand_name")} />
                <div className="grid gap-3 md:grid-cols-2">
                  <FormField label="Preferred tone" error={brandForm.formState.errors.preferred_tone?.message} {...brandForm.register("preferred_tone")} />
                  <FormField label="Audience" error={brandForm.formState.errors.target_audience?.message} {...brandForm.register("target_audience")} />
                </div>
                <TextAreaField label="Brand voice" error={brandForm.formState.errors.brand_voice?.message} rows={3} {...brandForm.register("brand_voice")} />
                <TextAreaField label="Product description" error={brandForm.formState.errors.product_description?.message} rows={3} {...brandForm.register("product_description")} />
                <TextAreaField label="Example copy" error={brandForm.formState.errors.example_copy?.message} rows={3} {...brandForm.register("example_copy")} />
                <FormField
                  label="Banned phrases"
                  hint="Comma-separated"
                  error={brandForm.formState.errors.banned_phrases_text?.message}
                  {...brandForm.register("banned_phrases_text")}
                />
                <button
                  type="submit"
                  disabled={createBrandMutation.isPending}
                  className="rounded-full bg-teal-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {createBrandMutation.isPending ? "Saving..." : "Create brand"}
                </button>
                {createBrandMutation.error ? <ErrorText message={String(createBrandMutation.error.message)} /> : null}
              </form>

              <div className="mt-6 space-y-3">
                {(brandsQuery.data?.results ?? []).map((brand) => (
                  <div key={brand.id} className="rounded-[1.3rem] border border-slate-200 bg-slate-50 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-sm font-semibold text-slate-950">{brand.brand_name}</h3>
                        <p className="mt-1 text-sm text-slate-600">{brand.preferred_tone}</p>
                      </div>
                      <span className="text-xs text-slate-500">{formatDateTime(brand.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel
              title="Template library"
              icon={Bot}
              subtitle="Templates encode reusable prompt scaffolds by channel and objective."
            >
              <form
                className="grid gap-3"
                onSubmit={templateForm.handleSubmit((values) => createTemplateMutation.mutate(values))}
              >
                <FormField label="Template name" error={templateForm.formState.errors.name?.message} {...templateForm.register("name")} />
                <div className="grid gap-3 md:grid-cols-2">
                  <SelectField label="Channel" error={templateForm.formState.errors.channel?.message} {...templateForm.register("channel")}>
                    {templateChannels.map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </SelectField>
                  <SelectField label="Objective" error={templateForm.formState.errors.objective?.message} {...templateForm.register("objective")}>
                    {templateObjectives.map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </SelectField>
                </div>
                <TextAreaField
                  label="Prompt template"
                  error={templateForm.formState.errors.prompt_template?.message}
                  rows={4}
                  {...templateForm.register("prompt_template")}
                />
                <button
                  type="submit"
                  disabled={createTemplateMutation.isPending}
                  className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {createTemplateMutation.isPending ? "Saving..." : "Create template"}
                </button>
                {createTemplateMutation.error ? <ErrorText message={String(createTemplateMutation.error.message)} /> : null}
              </form>

              <div className="mt-6 space-y-3">
                {(templatesQuery.data?.results ?? []).map((template) => (
                  <div key={template.id} className="rounded-[1.3rem] border border-slate-200 bg-slate-50 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <h3 className="text-sm font-semibold text-slate-950">{template.name}</h3>
                        <p className="mt-1 text-sm text-slate-600">
                          {template.channel} · {template.objective}
                        </p>
                      </div>
                      <span className="text-xs text-slate-500">{formatDateTime(template.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel
              title="Usage telemetry"
              icon={Gauge}
              subtitle="The chart and inspector below reflect the real request history generated through this guest session."
            >
              <div className="h-64 rounded-[1.5rem] bg-slate-50 p-4">
                {usageChartData.length === 0 ? (
                  <EmptyState title="No usage events yet" body="Once requests complete, token counts and latency will appear here." />
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={usageChartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="tokens" x1="0" x2="0" y1="0" y2="1">
                          <stop offset="5%" stopColor="#0f766e" stopOpacity={0.5} />
                          <stop offset="95%" stopColor="#0f766e" stopOpacity={0.05} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
                      <XAxis dataKey="name" tickLine={false} axisLine={false} />
                      <YAxis tickLine={false} axisLine={false} />
                      <Tooltip />
                      <Area type="monotone" dataKey="tokens" stroke="#0f766e" fill="url(#tokens)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>

              <div className="mt-6 grid gap-4 lg:grid-cols-2">
                <InspectorCard title="Last request" icon={Radar} entry={lastRequest} />
                <InspectorCard title="Last response" icon={BarChart3} entry={lastResponse} />
              </div>
            </Panel>
          </div>
        </section>
      </div>
    </main>
  );
}

function Panel({
  title,
  subtitle,
  icon: Icon,
  children
}: {
  title: string;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-[2rem] border border-white/70 bg-white/90 p-6 shadow-panel backdrop-blur">
      <div className="flex items-start gap-4">
        <div className="rounded-2xl bg-teal-50 p-3">
          <Icon className="h-5 w-5 text-teal-700" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-slate-950">{title}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-slate-600">{subtitle}</p>
        </div>
      </div>
      <div className="mt-6">{children}</div>
    </section>
  );
}

function FormField({
  label,
  hint,
  error,
  className,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  hint?: string;
  error?: string;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-slate-800">{label}</span>
      <input
        {...props}
        className={cn(
          "w-full rounded-[1.1rem] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-teal-400 focus:ring-4 focus:ring-teal-100",
          className
        )}
      />
      {hint ? <span className="mt-2 block text-xs text-slate-500">{hint}</span> : null}
      {error ? <ErrorText message={error} /> : null}
    </label>
  );
}

function TextAreaField({
  label,
  hint,
  error,
  className,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label: string;
  hint?: string;
  error?: string;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-slate-800">{label}</span>
      <textarea
        {...props}
        className={cn(
          "w-full rounded-[1.1rem] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-teal-400 focus:ring-4 focus:ring-teal-100",
          className
        )}
      />
      {hint ? <span className="mt-2 block text-xs text-slate-500">{hint}</span> : null}
      {error ? <ErrorText message={error} /> : null}
    </label>
  );
}

function SelectField({
  label,
  error,
  className,
  children,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-slate-800">{label}</span>
      <select
        {...props}
        className={cn(
          "w-full rounded-[1.1rem] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-teal-400 focus:ring-4 focus:ring-teal-100",
          className
        )}
      >
        {children}
      </select>
      {error ? <ErrorText message={error} /> : null}
    </label>
  );
}

function ErrorText({ message }: { message: string }) {
  return <p className="mt-2 text-sm text-rose-600">{message}</p>;
}

function Detail({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</dt>
      <dd className={cn("mt-1 text-sm text-slate-900", mono && "font-mono text-xs sm:text-sm")}>{value}</dd>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[1.4rem] border border-slate-200 bg-slate-50 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function StatusBadge({
  label,
  value,
  tone,
  icon: Icon
}: {
  label: string;
  value: string;
  tone: "good" | "warn";
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="rounded-[1.25rem] border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
      <div className="flex items-center gap-3">
        <div className={cn("rounded-xl p-2", tone === "good" ? "bg-teal-400/15 text-teal-300" : "bg-amber-400/15 text-amber-300")}>
          <Icon className="h-4 w-4" />
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{label}</p>
          <p className="mt-1 text-sm font-medium text-white">{value}</p>
        </div>
      </div>
    </div>
  );
}

function JobPill({ status }: { status: string }) {
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

function FlagPill({ text }: { text: string }) {
  return <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-slate-700">{text}</span>;
}

function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-[1.5rem] border border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center">
      <p className="text-base font-semibold text-slate-900">{title}</p>
      <p className="mt-2 text-sm leading-7 text-slate-600">{body}</p>
    </div>
  );
}

function InspectorCard({
  title,
  icon: Icon,
  entry
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  entry: { label: string; payload: unknown } | null;
}) {
  return (
    <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-white p-2 shadow-sm">
          <Icon className="h-4 w-4 text-slate-700" />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-950">{title}</p>
          <p className="text-xs text-slate-500">{entry?.label ?? "No requests yet"}</p>
        </div>
      </div>
      <pre className="mt-4 max-h-80 overflow-auto">{JSON.stringify(entry?.payload ?? {}, null, 2)}</pre>
    </div>
  );
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
