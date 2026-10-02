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
    def __init__(self):
        self.players: dict[str, Player] = {}
        self.max_apprentices = 10
        self.graduation_level = 50
        self.graduation_required_tasks = 5
        # 已出师（传承完成）的技能，解除关系时不回收: {mentor_id: {skill_id}}
        self.earned_skills: dict[str, set] = {}
        # 传承技能的来源徒弟: {(mentor_id, skill_id): apprentice_id}
        self.skill_source: dict[tuple, str] = {}

    def accept_apprentice(self, mentor_id: str, apprentice_id: str) -> bool:
        if not mentor_id or not apprentice_id or mentor_id == apprentice_id:
            return False

        mentor = self.players.get(mentor_id)
        apprentice = self.players.get(apprentice_id)

        # 徒弟已在拜师中 / 对方本身是师傅，不能再拜
        if apprentice is not None and (
            apprentice.mentor is not None or apprentice.role == "mentor"
        ):
            return False

        # 师傅当前徒弟数量上限（仅统计在籍徒弟，出师后已移出列表）
        current_count = len(mentor.apprentices) if mentor is not None else 0
        if current_count >= self.max_apprentices:
            return False

        if mentor is None:
            mentor = Player(mentor_id, role="mentor")
            self.players[mentor_id] = mentor
        elif mentor.role == "none":
            mentor.role = "mentor"

        if apprentice is None:
            apprentice = Player(apprentice_id, role="apprentice", mentor=mentor_id)
            self.players[apprentice_id] = apprentice
        else:
            apprentice.role = "apprentice"
            apprentice.mentor = mentor_id

        if apprentice_id not in mentor.apprentices:
            mentor.apprentices.append(apprentice_id)
        return True

    def grant_mentor_skill(
        self, mentor_id: str, skill_id: str, apprentice_id: str = None
    ) -> bool:
        # 同一传承技能只发放一次，不叠加
        mentor = self.players.get(mentor_id)
        if mentor is None:
            return False
        if skill_id in mentor.mentor_skills:
            return False
        mentor.mentor_skills[skill_id] = 1
        self.skill_source[(mentor_id, skill_id)] = apprentice_id
        return True

    def check_graduation(self, apprentice_id: str, level: int) -> bool:
        # 出师条件：等级达标且师徒任务完成度达标，且仍有在籍师徒关系
        apprentice = self.players.get(apprentice_id)
        if apprentice is None or apprentice.role != "apprentice":
            return False
        if apprentice.mentor is None:
            return False
        return (
            level >= self.graduation_level
            and apprentice.tasks_completed >= self.graduation_required_tasks
        )

    # 需求文档中的长方法名别名
    check_apprentice_graduation = check_graduation

    def graduate_apprentice(
        self, apprentice_id: str, level: int, skill_id: str = None
    ) -> bool:
        apprentice = self.players.get(apprentice_id)
        if apprentice is None or not self.check_graduation(apprentice_id, level):
            return False

        mentor_id = apprentice.mentor
        mentor = self.players.get(mentor_id)

        # 传承技能只发一次；出师后转为“已获得”，解除关系不再回收
        if skill_id is not None:
            self.grant_mentor_skill(mentor_id, skill_id, apprentice_id=apprentice_id)
            self.earned_skills.setdefault(mentor_id, set()).add(skill_id)

        # 出师即解除师徒关系
        if mentor is not None and apprentice_id in mentor.apprentices:
            mentor.apprentices.remove(apprentice_id)
        apprentice.mentor = None
        apprentice.role = "none"
        return True

    def update_task_progress(self, apprentice_id: str, mentor_id: str = None) -> None:
        # 徒弟任务进度 +1，并双向同步给师傅
        apprentice = self.players.get(apprentice_id)
        if apprentice is None:
            return
        apprentice.tasks_completed += 1

        if mentor_id is None:
            mentor_id = apprentice.mentor
        mentor = self.players.get(mentor_id) if mentor_id else None
        if mentor is not None:
            mentor.tasks_completed += 1

    # 需求文档中的长方法名别名
    update_mentor_task_progress = update_task_progress

    def dissolve_mentorship(self, mentor_id: str, apprentice_id: str) -> bool:
        apprentice = self.players.get(apprentice_id)
        if apprentice is None:
            return False

        mentor = self.players.get(mentor_id)
        graduated = apprentice.mentor is None
        earned = self.earned_skills.get(mentor_id, set())

        # 回收未完成出师的传承技能；已出师获得的技能保留
        if mentor is not None and not graduated:
            for sid in list(mentor.mentor_skills):
                if sid in earned:
                    continue
                source = self.skill_source.get((mentor_id, sid))
                if source == apprentice_id or source is None:
                    mentor.mentor_skills.pop(sid, None)
                    self.skill_source.pop((mentor_id, sid), None)

        if mentor is not None and apprentice_id in mentor.apprentices:
            mentor.apprentices.remove(apprentice_id)
        apprentice.mentor = None
        apprentice.role = "none"
        return True
