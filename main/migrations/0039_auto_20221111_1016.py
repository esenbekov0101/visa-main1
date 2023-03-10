# Generated by Django 4.0.4 on 2022-11-11 04:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_pending_comment_pending_days_type'),
    ]

    operations = [
        migrations.RunSQL(
            '''
            DELETE FROM main_group
WHERE id IN
    (SELECT id
    FROM 
        (SELECT id,
         ROW_NUMBER() OVER( PARTITION BY days_type,
         start_time, current_teacher_id, archived
        ORDER BY  id ) AS row_num
        FROM main_group ) t
        WHERE t.row_num > 1 );
            '''
        )
    ]
