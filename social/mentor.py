"""师徒传承"""
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
    REQUIRED_LEVEL = 50   # 出师等级要求
    REQUIRED_TASKS = 5    # 出师师徒任务完成度要求

    def __init__(self):
        self.players: dict[str, Player] = {}
        self.max_apprentices = 100
        # mentor_id -> 已通过出师正式获得的传承技能(解除关系时不回收)
        self._earned_skills: dict[str, set] = {}

    def accept_apprentice(self, mentor_id: str, apprentice_id: str) -> bool:
        if mentor_id not in self.players:
            self.players[mentor_id] = Player(mentor_id, role="mentor")
        mentor = self.players[mentor_id]
        # fix1: 检查师傅当前徒弟数量上限
        if len(mentor.apprentices) >= self.max_apprentices:
            return False
        if apprentice_id in mentor.apprentices:
            return False
        apprentice = self.players.get(apprentice_id)
        if apprentice is not None and apprentice.mentor is not None:
            return False  # 已有师傅
        if apprentice is None:
            apprentice = Player(apprentice_id)
            self.players[apprentice_id] = apprentice
        apprentice.role = "apprentice"
        apprentice.mentor = mentor_id
        mentor.role = "mentor"
        mentor.apprentices.append(apprentice_id)
        return True

    def grant_mentor_skill(self, mentor_id: str, skill_id: str) -> bool:
        if mentor_id not in self.players:
            return False
        skills = self.players[mentor_id].mentor_skills
        # fix2: 传承技能只授予一次，不叠加
        if skill_id in skills:
            return False
        skills[skill_id] = 1
        return True

    def check_graduation(self, apprentice_id: str, level: int) -> bool:
        # fix3: 出师需同时满足等级和师徒任务完成度
        if apprentice_id not in self.players:
            return False
        apprentice = self.players[apprentice_id]
        return (level >= self.REQUIRED_LEVEL
                and apprentice.tasks_completed >= self.REQUIRED_TASKS)

    def graduate_apprentice(self, apprentice_id: str, level: int) -> bool:
        """出师：校验条件 -> 授予传承技能(仅一次) -> 解除师徒关系"""
        if not self.check_graduation(apprentice_id, level):
            return False
        apprentice = self.players[apprentice_id]
        mentor_id = apprentice.mentor
        if mentor_id is None:
            return False
        skill_id = f"inherit_{apprentice_id}"
        if self.grant_mentor_skill(mentor_id, skill_id):
            self._earned_skills.setdefault(mentor_id, set()).add(skill_id)
        # 出师后解除师徒关系
        self._detach(mentor_id, apprentice_id)
        return True

    def update_task_progress(self, apprentice_id: str, mentor_id: str = None) -> None:
        apprentice = self.players.get(apprentice_id)
        if apprentice is None:
            return
        apprentice.tasks_completed += 1
        # fix4: 任务进度双向同步给师傅
        mentor_id = apprentice.mentor or mentor_id
        mentor = self.players.get(mentor_id) if mentor_id else None
        if mentor is not None:
            mentor.tasks_completed += 1

    def dissolve_mentorship(self, mentor_id: str, apprentice_id: str) -> bool:
        if mentor_id not in self.players or apprentice_id not in self.players:
            return False
        mentor = self.players[mentor_id]
        apprentice = self.players[apprentice_id]
        if apprentice.mentor != mentor_id:
            return False
        # fix5: 回收未通过出师获得的传承技能，防止白嫖
        earned = self._earned_skills.get(mentor_id, set())
        for skill_id in list(mentor.mentor_skills):
            if skill_id not in earned:
                del mentor.mentor_skills[skill_id]
        self._detach(mentor_id, apprentice_id)
        return True

    def _detach(self, mentor_id: str, apprentice_id: str) -> None:
        mentor = self.players.get(mentor_id)
        apprentice = self.players.get(apprentice_id)
        if mentor is not None and apprentice_id in mentor.apprentices:
            mentor.apprentices.remove(apprentice_id)
        if apprentice is not None:
            apprentice.mentor = None
            apprentice.role = "none"
