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
            name="ContentTemplate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("channel", models.CharField(choices=[("social", "Social"), ("ads", "Ads"), ("email", "Email"), ("landing_page", "Landing Page"), ("campaign", "Campaign")], max_length=32)),
                ("objective", models.CharField(choices=[("lead_generation", "Lead Generation"), ("awareness", "Awareness"), ("conversion", "Conversion"), ("retention", "Retention"), ("product_launch", "Product Launch")], max_length=32)),
                ("prompt_template", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="content_templates", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("name", "created_at"), "unique_together": {("user", "name")}},
        ),
        migrations.AddIndex(
            model_name="contenttemplate",
            index=models.Index(fields=["user", "channel"], name="templates_c_user_id_ef9fc8_idx"),
        ),
        migrations.AddIndex(
            model_name="contenttemplate",
            index=models.Index(fields=["user", "objective"], name="templates_c_user_id_742e64_idx"),
        ),
    ]

