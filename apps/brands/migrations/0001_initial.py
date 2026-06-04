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
            name="BrandProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("brand_name", models.CharField(max_length=255)),
                ("brand_voice", models.TextField()),
                ("banned_phrases", models.JSONField(blank=True, default=list)),
                ("preferred_tone", models.CharField(max_length=64)),
                ("example_copy", models.TextField(blank=True)),
                ("product_description", models.TextField()),
                ("target_audience", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="brand_profiles", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("brand_name", "created_at"), "unique_together": {("user", "brand_name")}},
        ),
        migrations.AddIndex(
            model_name="brandprofile",
            index=models.Index(fields=["user", "brand_name"], name="brands_bran_user_id_16cd67_idx"),
        ),
        migrations.AddIndex(
            model_name="brandprofile",
            index=models.Index(fields=["created_at"], name="brands_bran_created_18eeb0_idx"),
        ),
    ]

