# Generated migration for GameScreenshot model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameScreenshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='games/screenshots/%Y/%m/', verbose_name='截图')),
                ('title', models.CharField(blank=True, default='', max_length=200, verbose_name='标题')),
                ('description', models.TextField(blank=True, default='', verbose_name='描述')),
                ('order', models.IntegerField(default=0, help_text='显示顺序，数字越小越靠前', verbose_name='排序')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='screenshots', to='games.game', verbose_name='游戏')),
            ],
            options={
                'verbose_name': '游戏截图',
                'verbose_name_plural': '游戏截图',
                'db_table': 'game_screenshots',
                'ordering': ['game', 'order', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='gamescreenshot',
            index=models.Index(fields=['game', 'order'], name='game_screen_game_id_5e8f2c_idx'),
        ),
    ]

