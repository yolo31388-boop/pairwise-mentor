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

    def test_cannot_accept_already_apprenticed_player(self):
        ms = MentorSystem()
        ms.players["m1"] = Player("m1", role="mentor")
        ms.players["m2"] = Player("m2", role="mentor")
        ms.players["a1"] = Player("a1", role="apprentice", mentor="m1")
        ms.players["m1"].apprentices.append("a1")
        assert ms.accept_apprentice("m2", "a1") == False

    def test_graduated_slot_is_freed(self):
        ms = MentorSystem()
        ms.max_apprentices = 1
        assert ms.accept_apprentice("m1", "a1") == True
        ms.players["a1"].tasks_completed = 5
        assert ms.graduate_apprentice("a1", level=60, skill_id="s1") == True
        assert ms.accept_apprentice("m1", "a2") == True
        assert ms.players["m1"].apprentices == ["a2"]

class TestSkillNotStacked:
    def test_skill_granted_only_once(self):
        ms = MentorSystem()
        ms.players["m1"] = Player("m1", role="mentor")
        ms.grant_mentor_skill("m1", "skill1")
        ms.grant_mentor_skill("m1", "skill1")
        assert ms.players["m1"].mentor_skills["skill1"] == 1

    def test_grant_skill_unknown_mentor_fails(self):
        ms = MentorSystem()
        assert ms.grant_mentor_skill("ghost", "skill1") == False

    def test_earned_skill_kept_after_dissolve(self):
        ms = MentorSystem()
        ms.accept_apprentice("m1", "a1")
        ms.players["a1"].tasks_completed = 5
        assert ms.graduate_apprentice("a1", level=60, skill_id="s1") == True
        assert ms.dissolve_mentorship("m1", "a1") == True
        assert "s1" in ms.players["m1"].mentor_skills

class TestGraduationRequiresTasks:
    def test_graduation_requires_level_and_tasks(self):
        ms = MentorSystem()
        ms.players["a1"] = Player("a1", role="apprentice", tasks_completed=0)
        assert ms.check_graduation("a1", level=60) == False

    def test_graduation_also_requires_level(self):
        ms = MentorSystem()
        ms.players["a1"] = Player(
            "a1", role="apprentice", mentor="m1", tasks_completed=5
        )
        assert ms.check_graduation("a1", level=10) == False

    def test_graduation_unbinds_relationship(self):
        ms = MentorSystem()
        ms.accept_apprentice("m1", "a1")
        ms.players["a1"].tasks_completed = 5
        assert ms.graduate_apprentice("a1", level=60, skill_id="s1") == True
        assert ms.players["a1"].mentor is None
        assert ms.players["a1"].role == "none"
        assert "a1" not in ms.players["m1"].apprentices
        assert ms.check_graduation("a1", level=60) == False

class TestTaskSync:
    def test_task_progress_synced_to_mentor(self):
        ms = MentorSystem()
        ms.players["m1"] = Player("m1", role="mentor")
        ms.players["a1"] = Player("a1", role="apprentice", mentor="m1")
        ms.update_task_progress("a1", "m1")
        assert ms.players["m1"].tasks_completed == 1
        assert ms.players["a1"].tasks_completed == 1

class TestDissolveRecoversSkill:
    def test_dissolve_removes_unearned_skills(self):
        ms = MentorSystem()
        ms.players["m1"] = Player("m1", role="mentor", mentor_skills={"s1": 1})
        ms.players["a1"] = Player("a1", role="apprentice", mentor="m1")
        ms.dissolve_mentorship("m1", "a1")
        assert "s1" not in ms.players["m1"].mentor_skills

    def test_dissolve_unbinds_both_sides(self):
        ms = MentorSystem()
        ms.accept_apprentice("m1", "a1")
        ms.grant_mentor_skill("m1", "s1", apprentice_id="a1")
        assert ms.dissolve_mentorship("m1", "a1") == True
        assert ms.players["a1"].mentor is None
        assert ms.players["a1"].role == "none"
        assert "a1" not in ms.players["m1"].apprentices
        assert "s1" not in ms.players["m1"].mentor_skills
