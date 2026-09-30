"""师徒传承 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from social.mentor import MentorSystem, Player

class TestApprenticeLimit:
    def test_mentor_has_max_apprentices(self):
        ms = MentorSystem()
        ms.players["m1"] = Player("m1", role="mentor", apprentices=["a1","a2","a3"])
        ms.max_apprentices = 3
        assert ms.accept_apprentice("m1", "a4") == False

class TestSkillNotStacked:
    def test_skill_granted_only_once(self):
        ms = MentorSystem()
        ms.players["m1"] = Player("m1", role="mentor")
        ms.grant_mentor_skill("m1", "skill1")
        ms.grant_mentor_skill("m1", "skill1")
        assert ms.players["m1"].mentor_skills["skill1"] == 1

class TestGraduationRequiresTasks:
    def test_graduation_requires_level_and_tasks(self):
        ms = MentorSystem()
        ms.players["a1"] = Player("a1", role="apprentice", tasks_completed=0)
        assert ms.check_graduation("a1", level=60) == False

class TestTaskSync:
    def test_task_progress_synced_to_mentor(self):
        ms = MentorSystem()
        ms.players["m1"] = Player("m1", role="mentor")
        ms.players["a1"] = Player("a1", role="apprentice", mentor="m1")
        ms.update_task_progress("a1", "m1")
        assert ms.players["m1"].tasks_completed == 1

class TestDissolveRecoversSkill:
    def test_dissolve_removes_unearned_skills(self):
        ms = MentorSystem()
        ms.players["m1"] = Player("m1", role="mentor", mentor_skills={"s1": 1})
        ms.players["a1"] = Player("a1", role="apprentice", mentor="m1")
        ms.dissolve_mentorship("m1", "a1")
        assert "s1" not in ms.players["m1"].mentor_skills
