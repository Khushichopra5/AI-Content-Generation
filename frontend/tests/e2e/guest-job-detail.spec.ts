import { execFileSync } from "node:child_process";
import path from "node:path";

import { expect, test } from "@playwright/test";

const repoRoot = path.resolve(__dirname, "../../..");
const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL ?? "http://127.0.0.1:8010";

function seedGuestOwnedJob(guestSessionJson: string) {
  const command = `
import base64
import json
import os
from pathlib import Path

from apps.brands.models import BrandProfile
from apps.generation.models import Asset, GenerationJob
from apps.guests.models import GuestSession

payload = json.loads(os.environ["GUEST_SESSION_JSON"])
session = GuestSession.objects.select_related("backing_user").get(
    guest_id=payload["session"]["guest_id"],
    session_id=payload["session"]["session_id"],
    device_id=payload["session"]["device_id"],
)
user = session.backing_user
suffix = payload["session"]["session_id"][-6:]
brand = BrandProfile.objects.create(
    user=user,
    brand_name=f"Seeded Brand {suffix}",
    brand_voice="Detailed, technical, and direct without sounding robotic.",
    banned_phrases=["synergy"],
    preferred_tone="Calm and precise",
    example_copy="Ship reliable UI without runtime overlays.",
    product_description="A seeded brand used for frontend route regression tests.",
    target_audience="Engineers validating browser flows.",
)
job = GenerationJob.objects.create(
    user=user,
    brand_profile=brand,
    template=None,
    input_payload={
        "channel": "linkedin",
        "objective": "Verify hydrated job detail page",
        "cta": "Open the seeded job detail view",
    },
    prompt_hash="seeded-job-detail-route-check",
    status="succeeded",
    model_name="test-seeded-model",
    output_payload={
        "variants": [
            {
                "headline": "Seeded output variant",
                "body": "This payload was seeded to verify job detail hydration and asset rendering.",
            }
        ]
    },
    include_image=True,
)
media_dir = Path("media/generated")
media_dir.mkdir(parents=True, exist_ok=True)
filename = f"seeded-{job.id}.png"
file_path = media_dir / filename
file_path.write_bytes(
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9sX0nS8AAAAASUVORK5CYII="
    )
)
Asset.objects.create(
    generation_job=job,
    asset_type="image",
    storage_url=f"${apiBaseUrl}/media/generated/{filename}",
    mime_type="image/png",
    metadata={"seeded": True},
)
print(json.dumps({"job_id": str(job.id)}))
`;

  const stdout = execFileSync(path.join(repoRoot, ".venv/bin/python"), ["manage.py", "shell", "-c", command], {
    cwd: repoRoot,
    env: {
      ...process.env,
      DJANGO_SETTINGS_MODULE: "config.settings.test",
      GUEST_SESSION_JSON: guestSessionJson,
    },
    encoding: "utf-8",
  });

  const jsonLine = stdout
    .trim()
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .at(-1);

  if (!jsonLine) {
    throw new Error(`No JSON output from seeded job helper: ${stdout}`);
  }

  return JSON.parse(jsonLine) as { job_id: string };
}

test("workspace loads for a bootstrapped guest session", async ({ page, request }) => {
  const bootstrapResponse = await request.post(`${apiBaseUrl}/api/v1/guest/bootstrap/`, {
    data: {},
  });
  expect(bootstrapResponse.ok()).toBeTruthy();
  const guestSession = await bootstrapResponse.json();
  const guestSessionJson = JSON.stringify(guestSession);

  await page.addInitScript((storedSession) => {
    window.localStorage.setItem("contentgen.guest-session", storedSession);
  }, guestSessionJson);

  await page.goto("/workspace");
  await expect(page.getByText("Guest-first workspace")).toBeVisible();
  await expect(page.getByText("Session and limits")).toBeVisible();
  await expect(page.getByText(guestSession.session.guest_id).first()).toBeVisible();
});

test("guest session can open a seeded asset job detail without runtime errors", async ({ page, request }) => {
  const errors: string[] = [];

  page.on("console", (message) => {
    if (message.type() === "error") {
      errors.push(message.text());
    }
  });

  page.on("pageerror", (error) => {
    errors.push(String(error));
  });

  page.on("response", (response) => {
    const url = response.url();
    if (
      response.status() >= 400 &&
      !url.includes("__nextjs_original-stack-frame") &&
      !url.includes("hot-update")
    ) {
      errors.push(`HTTP ${response.status()} ${url}`);
    }
  });

  const bootstrapResponse = await request.post(`${apiBaseUrl}/api/v1/guest/bootstrap/`, {
    data: {},
  });
  expect(bootstrapResponse.ok()).toBeTruthy();
  const guestSession = await bootstrapResponse.json();
  const guestSessionJson = JSON.stringify(guestSession);

  await page.addInitScript((storedSession) => {
    window.localStorage.setItem("contentgen.guest-session", storedSession);
  }, guestSessionJson);

  const seeded = seedGuestOwnedJob(guestSessionJson);

  await page.goto(`/jobs/${seeded.job_id}`);
  await expect(page).toHaveURL(new RegExp(`/jobs/${seeded.job_id}$`));
  await expect(page.getByText("Generation job detail")).toBeVisible();
  await expect(page.getByText("Output payload")).toBeVisible();
  await expect(page.getByText("Human-readable variants")).toBeVisible();
  await expect(page.getByText("Loading job details...")).not.toBeVisible();
  await expect(page.getByText("Unable to load this job")).not.toBeVisible();
  await expect(page.getByText("Runtime TypeError")).not.toBeVisible();
  await expect(page.getByText("Seeded output variant").first()).toBeVisible();
  const assetLink = page.getByRole("link", { name: "Open asset" });
  await expect(assetLink).toBeVisible();
  await expect(assetLink).toHaveAttribute(
    "href",
    new RegExp(`seeded-${seeded.job_id}\\.png$`),
  );

  const relevantErrors = errors.filter(
    (entry) =>
      !entry.includes("favicon") &&
      !entry.includes("Extension context invalidated"),
  );

  expect(relevantErrors).toEqual([]);
});
