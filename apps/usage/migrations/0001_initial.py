import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UsageEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_type", models.CharField(choices=[("generate_text", "Generate Text"), ("generate_image", "Generate Image"), ("cache_hit", "Cache Hit"), ("cache_miss", "Cache Miss"), ("login", "Login")], max_length=32)),
                ("tokens_in", models.PositiveIntegerField(default=0)),
                ("tokens_out", models.PositiveIntegerField(default=0)),
                ("latency_ms", models.PositiveIntegerField(default=0)),
                ("cache_hit", models.BooleanField(default=False)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="usage_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.AddIndex(
            model_name="usageevent",
            index=models.Index(fields=["user", "event_type"], name="usage_usage_user_id_95423d_idx"),
        ),
        migrations.AddIndex(
            model_name="usageevent",
            index=models.Index(fields=["created_at"], name="usage_usage_created_1eb8c8_idx"),
        ),
    ]
