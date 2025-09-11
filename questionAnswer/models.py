from django.db import models


class QuestionRecord(models.Model):
    """
    问题记录数据模型
    对应数据库表字段：
    - id: 主键
    - user_id: 用户ID（文本类型）
    - user_name: 用户名
    - student_id: 学号
    - question_content: 问题内容
    - system_answer: 系统回答
    - question_time: 提问时间（不带时区的时间戳）
    - response_duration: 响应时长（毫秒）
    - question_tag: 问题标签
    - hit_knowledge_graph: 是否命中知识图谱
    - answer_validity: 回答有效性评分
    """

    id = models.AutoField(primary_key=True, verbose_name='主键ID')
    user_id = models.IntegerField(verbose_name='用户ID')
    user_name = models.TextField(verbose_name='用户名')
    student_id = models.TextField(default=None, verbose_name='学号')
    question_content = models.TextField(verbose_name='问题内容')
    system_answer = models.TextField(default=None, verbose_name='系统回答')
    question_time = models.DateTimeField(verbose_name='提问时间')
    response_duration = models.IntegerField(default=None, verbose_name='响应时长(毫秒)')
    question_tags = models.TextField(default=None, verbose_name='问题标签')
    hit_knowledge_graph = models.BooleanField(default=False, verbose_name='命中知识图谱')
    answer_validity = models.IntegerField(default=1, verbose_name='回答有效性')

    class Meta:
        db_table = 'question_records'  # 显式指定数据库表名
        # managed = False
        '''
        verbose_name = '问题记录'
        verbose_name_plural = '问题记录'
        indexes = [
            models.Index(fields=['user_id'], name='idx_user_id'),
            models.Index(fields=['question_time'], name='idx_question_time'),
            models.Index(fields=['question_tag'], name='idx_question_tag'),
        ]
        ordering = ['-question_time']  # 默认按提问时间降序排列
        '''

    # def __str__(self):
    #     return f"{self.user_name}的提问记录(ID:{self.id})"


class StudyReport(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    study_report = models.TextField()
    study_report_time = models.DateTimeField()

    class Meta:
        db_table = 'study_report'  # 请替换为实际的表名