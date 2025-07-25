"""
简单确认系统的测试
"""

import pytest
import os
import tempfile
import shutil
from src.spark.chatbot.simple_confirmation import SimpleConfirmationManager
from src.spark.models import UserIdea, StoryOutline, CharacterProfile


class TestSimpleConfirmationManager:
    """测试简单确认管理器"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SimpleConfirmationManager()
        self.manager.storage_path = self.temp_dir
        
        # 创建测试数据
        self.user_idea = UserIdea(
            theme="冒险",
            genre="奇幻",
            target_audience="青少年",
            duration_preference=120,
            basic_characters=["英雄", "导师"],
            plot_points=["开始旅程", "面临挑战", "获得胜利"],
            visual_style="电影风格",
            mood="史诗"
        )
        
        self.story_outline = StoryOutline(
            title="魔法冒险",
            summary="一个年轻英雄的成长故事",
            narrative_text="从前，有一个年轻的英雄踏上了拯救王国的旅程...",
            estimated_duration=120
        )
        
        self.character_profiles = [
            CharacterProfile(
                name="英雄",
                role="主角",
                appearance="年轻勇敢的战士",
                personality="勇敢坚定",
                backstory="在小村庄长大",
                motivations=["拯救王国"],
                relationships={},
                image_url="http://example.com/hero.jpg",
                visual_consistency_tags=["年轻", "战士"]
            ),
            CharacterProfile(
                name="导师",
                role="指导者",
                appearance="智慧的老法师",
                personality="耐心睿智",
                backstory="前英雄转为导师",
                motivations=["指导英雄"],
                relationships={},
                image_url="http://example.com/mentor.jpg",
                visual_consistency_tags=["老者", "法师"]
            )
        ]
    
    def teardown_method(self):
        """清理测试环境"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_approved_content_success(self):
        """测试成功保存确认内容"""
        result = self.manager.save_approved_content(
            self.user_idea, self.story_outline, self.character_profiles, "测试项目"
        )
        
        assert result["status"] == "success"
        assert "project_id" in result
        assert result["project_name"] == "测试项目"
        assert len(result["files_created"]) == 3
        
        # 验证文件是否创建
        project_dir = result["project_path"]
        assert os.path.exists(os.path.join(project_dir, "approved_content.json"))
        assert os.path.exists(os.path.join(project_dir, "story_outline.json"))
        assert os.path.exists(os.path.join(project_dir, "characters.json"))
    
    def test_save_approved_content_auto_name(self):
        """测试自动生成项目名称"""
        result = self.manager.save_approved_content(
            self.user_idea, self.story_outline, self.character_profiles
        )
        
        assert result["status"] == "success"
        assert result["project_name"] == "魔法冒险"  # 使用story title
    
    def test_load_approved_content_success(self):
        """测试成功加载确认内容"""
        # 先保存
        save_result = self.manager.save_approved_content(
            self.user_idea, self.story_outline, self.character_profiles
        )
        project_id = save_result["project_id"]
        
        # 再加载
        loaded_data = self.manager.load_approved_content(project_id)
        
        assert loaded_data is not None
        assert loaded_data["project_id"] == project_id
        assert loaded_data["user_confirmed"] is True
        assert loaded_data["status"] == "approved"
        assert len(loaded_data["character_profiles"]) == 2
    
    def test_load_approved_content_not_found(self):
        """测试加载不存在的项目"""
        result = self.manager.load_approved_content("non_existent_id")
        assert result is None
    
    def test_list_projects(self):
        """测试列出项目"""
        # 创建几个项目
        self.manager.save_approved_content(
            self.user_idea, self.story_outline, self.character_profiles, "项目1"
        )
        self.manager.save_approved_content(
            self.user_idea, self.story_outline, self.character_profiles, "项目2"
        )
        
        projects = self.manager.list_projects()
        
        assert len(projects) == 2
        assert all("project_id" in p for p in projects)
        assert all("project_name" in p for p in projects)
        assert all("created_at" in p for p in projects)
        assert all("character_count" in p for p in projects)
        
        # 验证角色数量
        assert all(p["character_count"] == 2 for p in projects)
    
    def test_delete_project_success(self):
        """测试成功删除项目"""
        # 先创建项目
        save_result = self.manager.save_approved_content(
            self.user_idea, self.story_outline, self.character_profiles
        )
        project_id = save_result["project_id"]
        
        # 验证项目存在
        assert self.manager.load_approved_content(project_id) is not None
        
        # 删除项目
        delete_result = self.manager.delete_project(project_id)
        
        assert delete_result["status"] == "success"
        
        # 验证项目已删除
        assert self.manager.load_approved_content(project_id) is None
    
    def test_delete_project_not_found(self):
        """测试删除不存在的项目"""
        result = self.manager.delete_project("non_existent_id")
        
        assert result["status"] == "error"
        assert "不存在" in result["message"]
    
    def test_regenerate_character_image_success(self):
        """测试角色图片重新生成请求"""
        # 先创建项目
        save_result = self.manager.save_approved_content(
            self.user_idea, self.story_outline, self.character_profiles
        )
        project_id = save_result["project_id"]
        
        # 请求重新生成角色图片
        regen_result = self.manager.regenerate_character_image(
            project_id, "英雄", "让他看起来更年轻一些"
        )
        
        assert regen_result["status"] == "success"
        assert regen_result["character_name"] == "英雄"
        assert regen_result["feedback"] == "让他看起来更年轻一些"
    
    def test_regenerate_character_image_project_not_found(self):
        """测试项目不存在时的角色图片重新生成"""
        result = self.manager.regenerate_character_image(
            "non_existent_id", "英雄", "反馈"
        )
        
        assert result["status"] == "error"
        assert "不存在" in result["message"]
    
    def test_regenerate_character_image_character_not_found(self):
        """测试角色不存在时的图片重新生成"""
        # 先创建项目
        save_result = self.manager.save_approved_content(
            self.user_idea, self.story_outline, self.character_profiles
        )
        project_id = save_result["project_id"]
        
        # 请求重新生成不存在的角色
        result = self.manager.regenerate_character_image(
            project_id, "不存在的角色", "反馈"
        )
        
        assert result["status"] == "error"
        assert "不存在" in result["message"]
    
    def test_ensure_storage_directory(self):
        """测试确保存储目录存在"""
        # 删除目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # 重新创建管理器
        manager = SimpleConfirmationManager()
        manager.storage_path = self.temp_dir
        manager.ensure_storage_directory()
        
        # 验证目录已创建
        assert os.path.exists(self.temp_dir)
        assert os.path.isdir(self.temp_dir)