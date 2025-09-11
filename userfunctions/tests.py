from django.test import TestCase
from userfunctions.models import User


class UserOperationsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 创建一些测试数据
        User.objects.create(
            user_id='001',
            user_name='张三',
            student_id='2023001',
            password='password123',
            type='student'
        )
        User.objects.create(
            user_id='002',
            user_name='李四',
            student_id='2023002',
            password='password456',
            type='teacher'
        )

    def test_create_user(self):
        """测试创建用户"""
        new_user = User.objects.create(
            user_id='003',
            user_name='王五',
            student_id='2023003',
            password='password789',
            type='student'
        )
        self.assertEqual(new_user.user_name, '王五')
        self.assertEqual(User.objects.count(), 3)

    def test_read_user(self):
        """测试读取用户"""
        user = User.objects.get(user_id='001')
        self.assertEqual(user.user_name, '张三')
        self.assertEqual(user.type, 'student')

    def test_update_user(self):
        """测试更新用户"""
        user = User.objects.get(user_id='002')
        user.user_name = '李四 Updated'
        user.save()
        updated_user = User.objects.get(user_id='002')
        self.assertEqual(updated_user.user_name, '李四 Updated')

    def test_delete_user(self):
        """测试删除用户"""
        user = User.objects.get(user_id='001')
        user.delete()
        self.assertEqual(User.objects.count(), 1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(user_id='001')

    def test_query_users(self):
        """测试查询用户"""
        # 获取所有用户
        all_users = User.objects.all()
        self.assertEqual(len(all_users), 2)
        
        # 条件查询
        students = User.objects.filter(type='student')
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].user_name, '张三')
        
        # 复杂查询
        users_start_with_li = User.objects.filter(user_name__startswith='李')
        self.assertEqual(len(users_start_with_li), 1)