"""师徒传承 - 含5个bug"""
from dataclasses import dataclass, field

@dataclass
class Player:
    pid: str
    role: str = "none"  # mentor/apprentice/none
    mentor: str = None
    apprentices: list = field(default_factory=list)
    mentor_skills: dict = field(default_factory=dict)
    tasks_completed: int = 0

class MentorSystem:
    def __init__(self):
        self.players: dict[str, Player] = {}
        self.max_apprentices = 100  # bug1: 无上限

    def accept_apprentice(self, mentor_id: str, apprentice_id: str) -> bool:
        # bug1: 不检查徒弟数量
        if mentor_id not in self.players:
            self.players[mentor_id] = Player(mentor_id, role="mentor")
        if apprentice_id not in self.players:
            self.players[apprentice_id] = Player(apprentice_id, role="apprentice", mentor=mentor_id)
        self.players[mentor_id].apprentices.append(apprentice_id)
        return True

    def grant_mentor_skill(self, mentor_id: str, skill_id: str) -> bool:
        # bug2: 重复叠加
        if mentor_id not in self.players:
            return False
        current = self.players[mentor_id].mentor_skills.get(skill_id, 0)
        self.players[mentor_id].mentor_skills[skill_id] = current + 1
        return True

    def check_graduation(self, apprentice_id: str, level: int) -> bool:
        # bug3: 只看等级不看任务
        return level >= 50

    def update_task_progress(self, apprentice_id: str, mentor_id: str) -> None:
        # bug4: 不同步给师傅
        if apprentice_id in self.players:
            self.players[apprentice_id].tasks_completed += 1

    def dissolve_mentorship(self, mentor_id: str, apprentice_id: str) -> bool:
        # bug5: 不回收技能
        if apprentice_id in self.players:
            self.players[apprentice_id].mentor = None
            self.players[apprentice_id].role = "none"
        return True
