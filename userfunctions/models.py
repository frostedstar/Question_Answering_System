from django.db import models

class BaseUserInfo(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.TextField()
    student_id = models.TextField()
    password = models.TextField()
    type = models.TextField()
    email = models.TextField()
    approved=models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.user_name


class Userinfo(BaseUserInfo):
    class Meta:
        db_table = '"User_info"'  # 指定数据库表名
        managed = False   # 告诉Django不要管理此表的创建和修改



class ReadUserInfo(BaseUserInfo):
    user_id = models.IntegerField()

    class Meta:
        db_table = '"User_info"'  # 指定数据库表名
        managed = False   # 告诉Django不要管理此表的创建和修改


