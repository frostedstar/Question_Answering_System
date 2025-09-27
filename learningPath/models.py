from django.db import models

class LearningPath(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    graph = models.TextField()
    graph_time = models.DateTimeField()
    question_number = models.IntegerField()
    index = models.IntegerField()
    class Meta:
        db_table = 'learning_path'  