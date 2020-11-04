
# Generated by Django 3.1.2 on 2020-11-03 23:46


from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InspectionRecords',
            fields=[
                ('restaurant_inspection_id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('restaurant_name', models.CharField(max_length=200)),
                ('postcode', models.CharField(max_length=200)),
                ('business_address', models.CharField(max_length=200)),
                ('is_roadway_compliant', models.CharField(max_length=200)),
                ('skipped_reason', models.CharField(max_length=200)),
                ('inspected_on', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='UserQuestionnaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant_business_id', models.CharField(max_length=200)),
                ('safety_level', models.CharField(max_length=1)),
                ('temperature_required', models.CharField(default='False', max_length=5)),
                ('contact_info_required', models.CharField(default='False', max_length=5)),
                ('employee_mask', models.CharField(default='False', max_length=5)),
                ('capacity_compliant', models.CharField(default='False', max_length=5)),
                ('distance_compliant', models.CharField(default='False', max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='YelpRestaurantDetails',
            fields=[
                ('business_id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('neighborhood', models.CharField(default=None, max_length=200, null=True)),
                ('category', models.CharField(default=None, max_length=200, null=True)),
                ('price', models.CharField(default=None, max_length=200, null=True)),
                ('rating', models.FloatField(blank=True, default=0.0, null=True)),
                ('img_url', models.CharField(default=None, max_length=200, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=14, default=0, max_digits=17)),
                ('longitude', models.DecimalField(blank=True, decimal_places=14, default=0, max_digits=17)),
            ],
        ),
        migrations.CreateModel(
            name='Zipcodes',
            fields=[
                ('zipcode', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('borough', models.CharField(default=None, max_length=200, null=True)),
                ('neighborhood', models.CharField(default=None, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant_name', models.CharField(max_length=200)),
                ('business_address', models.CharField(max_length=200)),
                ('postcode', models.CharField(max_length=200)),
                ('business_id', models.CharField(blank=True, default=None, max_length=200, null=True)),
            ],
            options={
                'unique_together': {('restaurant_name', 'business_address', 'postcode')},
            },
        ),
    ]
