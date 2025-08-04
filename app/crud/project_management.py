from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models.project_management import (
    PMProject, Task, Bug, ProjectCollaborator, ProjectMetrics, 
    UserActivity, Feedback, Release, CodeReview
)
from models.user import User
from schemas.project_management import (
    ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate,
    BugCreate, BugUpdate, FeedbackCreate, FeedbackUpdate,
    ReleaseCreate, ReleaseUpdate, CodeReviewCreate, CodeReviewUpdate
)


class ProjectCRUD:
    def create(self, db: Session, project_data: ProjectCreate, owner_id: int) -> PMProject:
        db_project = PMProject(
            **project_data.dict(),
            owner_id=owner_id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    def get(self, db: Session, project_id: int) -> Optional[PMProject]:
        return db.query(PMProject).options(
            joinedload(PMProject.owner),
            joinedload(PMProject.collaborators).joinedload(ProjectCollaborator.user),
            joinedload(PMProject.tasks),
            joinedload(PMProject.bugs),
            joinedload(PMProject.metrics)
        ).filter(PMProject.id == project_id).first()

    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[PMProject]:
        return db.query(PMProject).options(
            joinedload(PMProject.owner),
            joinedload(PMProject.collaborators)
        ).filter(
            or_(
                PMProject.owner_id == user_id,
                PMProject.collaborators.any(ProjectCollaborator.user_id == user_id)
            )
        ).offset(skip).limit(limit).all()

    def update(self, db: Session, project_id: int, project_data: ProjectUpdate) -> Optional[PMProject]:
        db_project = self.get(db, project_id)
        if db_project:
            update_data = project_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_project, field, value)
            db.commit()
            db.refresh(db_project)
        return db_project

    def delete(self, db: Session, project_id: int) -> bool:
        db_project = self.get(db, project_id)
        if db_project:
            db.delete(db_project)
            db.commit()
            return True
        return False

    def get_dashboard_metrics(self, db: Session, user_id: int) -> Dict[str, Any]:
        # Get user's projects
        user_projects = self.get_by_user(db, user_id)
        project_ids = [p.id for p in user_projects]

        if not project_ids:
            return {
                "total_projects": 0,
                "active_projects": 0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "total_bugs": 0,
                "open_bugs": 0,
                "critical_bugs": 0,
                "average_response_time": 0.0,
                "test_coverage_avg": 0.0,
                "code_quality_avg": 0.0
            }

        # Calculate metrics
        total_projects = len(user_projects)
        active_projects = len([p for p in user_projects if p.status.value in ["in_progress", "review", "testing"]])

        # Task metrics
        task_stats = db.query(
            func.count(Task.id).label("total"),
            func.count(Task.id).filter(Task.status == "done").label("completed")
        ).filter(Task.project_id.in_(project_ids)).first()

        # Bug metrics
        bug_stats = db.query(
            func.count(Bug.id).label("total"),
            func.count(Bug.id).filter(Bug.status != "done").label("open"),
            func.count(Bug.id).filter(Bug.severity == "critical").label("critical")
        ).filter(Bug.project_id.in_(project_ids)).first()

        # Performance metrics (average of latest metrics)
        latest_metrics = db.query(ProjectMetrics).filter(
            ProjectMetrics.project_id.in_(project_ids)
        ).order_by(desc(ProjectMetrics.date)).limit(len(project_ids)).all()

        avg_response_time = 0.0
        avg_test_coverage = 0.0
        avg_code_quality = 0.0

        if latest_metrics:
            avg_response_time = sum(m.api_response_time_avg for m in latest_metrics) / len(latest_metrics)
            avg_test_coverage = sum(m.test_coverage for m in latest_metrics) / len(latest_metrics)
            avg_code_quality = sum(m.code_quality_score for m in latest_metrics) / len(latest_metrics)

        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "total_tasks": task_stats.total if task_stats else 0,
            "completed_tasks": task_stats.completed if task_stats else 0,
            "total_bugs": bug_stats.total if bug_stats else 0,
            "open_bugs": bug_stats.open if bug_stats else 0,
            "critical_bugs": bug_stats.critical if bug_stats else 0,
            "average_response_time": avg_response_time,
            "test_coverage_avg": avg_test_coverage,
            "code_quality_avg": avg_code_quality
        }

    def get_project_progress(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        user_projects = self.get_by_user(db, user_id)
        progress_data = []

        for project in user_projects:
            # Get task counts
            task_stats = db.query(
                func.count(Task.id).label("total"),
                func.count(Task.id).filter(Task.status == "done").label("completed")
            ).filter(Task.project_id == project.id).first()

            # Get bug counts
            bug_stats = db.query(
                func.count(Bug.id).filter(Bug.status != "done").label("open"),
                func.count(Bug.id).filter(Bug.status == "done").label("resolved")
            ).filter(Bug.project_id == project.id).first()

            progress_data.append({
                "project_id": project.id,
                "project_name": project.name,
                "progress": project.progress,
                "status": project.status,
                "due_date": project.due_date,
                "tasks_completed": task_stats.completed if task_stats else 0,
                "tasks_total": task_stats.total if task_stats else 0,
                "bugs_open": bug_stats.open if bug_stats else 0,
                "bugs_resolved": bug_stats.resolved if bug_stats else 0
            })

        return progress_data


class TaskCRUD:
    def create(self, db: Session, task_data: TaskCreate, created_by: int) -> Task:
        db_task = Task(
            **task_data.dict(),
            created_by=created_by
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    def get(self, db: Session, task_id: int) -> Optional[Task]:
        return db.query(Task).options(
            joinedload(Task.project),
            joinedload(Task.assigned_user),
            joinedload(Task.creator)
        ).filter(Task.id == task_id).first()

    def get_by_project(self, db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(Task).options(
            joinedload(Task.assigned_user),
            joinedload(Task.creator)
        ).filter(Task.project_id == project_id).offset(skip).limit(limit).all()

    def get_kanban_board(self, db: Session, project_id: int) -> Dict[str, List[Task]]:
        tasks = self.get_by_project(db, project_id)
        columns = {
            "todo": [],
            "in_progress": [],
            "review": [],
            "testing": [],
            "done": [],
            "blocked": []
        }
        
        for task in tasks:
            columns[task.status.value].append(task)
        
        return columns

    def update(self, db: Session, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        db_task = self.get(db, task_id)
        if db_task:
            update_data = task_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)
            db.commit()
            db.refresh(db_task)
        return db_task

    def delete(self, db: Session, task_id: int) -> bool:
        db_task = self.get(db, task_id)
        if db_task:
            db.delete(db_task)
            db.commit()
            return True
        return False


class BugCRUD:
    def create(self, db: Session, bug_data: BugCreate, reported_by: int) -> Bug:
        db_bug = Bug(
            **bug_data.dict(),
            reported_by=reported_by
        )
        db.add(db_bug)
        db.commit()
        db.refresh(db_bug)
        return db_bug

    def get(self, db: Session, bug_id: int) -> Optional[Bug]:
        return db.query(Bug).options(
            joinedload(Bug.project),
            joinedload(Bug.reporter),
            joinedload(Bug.assigned_user)
        ).filter(Bug.id == bug_id).first()

    def get_by_project(self, db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[Bug]:
        return db.query(Bug).options(
            joinedload(Bug.reporter),
            joinedload(Bug.assigned_user)
        ).filter(Bug.project_id == project_id).offset(skip).limit(limit).all()

    def update(self, db: Session, bug_id: int, bug_data: BugUpdate) -> Optional[Bug]:
        db_bug = self.get(db, bug_id)
        if db_bug:
            update_data = bug_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_bug, field, value)
            db.commit()
            db.refresh(db_bug)
        return db_bug

    def delete(self, db: Session, bug_id: int) -> bool:
        db_bug = self.get(db, bug_id)
        if db_bug:
            db.delete(db_bug)
            db.commit()
            return True
        return False


class FeedbackCRUD:
    def create(self, db: Session, feedback_data: FeedbackCreate, user_id: int) -> Feedback:
        db_feedback = Feedback(
            **feedback_data.dict(),
            user_id=user_id
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return db_feedback

    def get(self, db: Session, feedback_id: int) -> Optional[Feedback]:
        return db.query(Feedback).options(
            joinedload(Feedback.user),
            joinedload(Feedback.project)
        ).filter(Feedback.id == feedback_id).first()

    def get_by_project(self, db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[Feedback]:
        return db.query(Feedback).options(
            joinedload(Feedback.user)
        ).filter(Feedback.project_id == project_id).offset(skip).limit(limit).all()

    def update(self, db: Session, feedback_id: int, feedback_data: FeedbackUpdate) -> Optional[Feedback]:
        db_feedback = self.get(db, feedback_id)
        if db_feedback:
            update_data = feedback_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_feedback, field, value)
            db.commit()
            db.refresh(db_feedback)
        return db_feedback

    def delete(self, db: Session, feedback_id: int) -> bool:
        db_feedback = self.get(db, feedback_id)
        if db_feedback:
            db.delete(db_feedback)
            db.commit()
            return True
        return False


class ReleaseCRUD:
    def create(self, db: Session, release_data: ReleaseCreate, created_by: int) -> Release:
        db_release = Release(
            **release_data.dict(),
            created_by=created_by
        )
        db.add(db_release)
        db.commit()
        db.refresh(db_release)
        return db_release

    def get(self, db: Session, release_id: int) -> Optional[Release]:
        return db.query(Release).options(
            joinedload(Release.project),
            joinedload(Release.creator)
        ).filter(Release.id == release_id).first()

    def get_by_project(self, db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[Release]:
        return db.query(Release).options(
            joinedload(Release.creator)
        ).filter(Release.project_id == project_id).offset(skip).limit(limit).all()

    def update(self, db: Session, release_id: int, release_data: ReleaseUpdate) -> Optional[Release]:
        db_release = self.get(db, release_id)
        if db_release:
            update_data = release_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_release, field, value)
            db.commit()
            db.refresh(db_release)
        return db_release

    def delete(self, db: Session, release_id: int) -> bool:
        db_release = self.get(db, release_id)
        if db_release:
            db.delete(db_release)
            db.commit()
            return True
        return False


class CodeReviewCRUD:
    def create(self, db: Session, review_data: CodeReviewCreate) -> CodeReview:
        db_review = CodeReview(**review_data.dict())
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review

    def get(self, db: Session, review_id: int) -> Optional[CodeReview]:
        return db.query(CodeReview).options(
            joinedload(CodeReview.project),
            joinedload(CodeReview.reviewer),
            joinedload(CodeReview.author)
        ).filter(CodeReview.id == review_id).first()

    def get_by_project(self, db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[CodeReview]:
        return db.query(CodeReview).options(
            joinedload(CodeReview.reviewer),
            joinedload(CodeReview.author)
        ).filter(CodeReview.project_id == project_id).offset(skip).limit(limit).all()

    def update(self, db: Session, review_id: int, review_data: CodeReviewUpdate) -> Optional[CodeReview]:
        db_review = self.get(db, review_id)
        if db_review:
            update_data = review_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_review, field, value)
            db.commit()
            db.refresh(db_review)
        return db_review

    def delete(self, db: Session, review_id: int) -> bool:
        db_review = self.get(db, review_id)
        if db_review:
            db.delete(db_review)
            db.commit()
            return True
        return False


class ProjectMetricsCRUD:
    def create(self, db: Session, project_id: int, metrics_data: Dict[str, Any]) -> ProjectMetrics:
        db_metrics = ProjectMetrics(
            project_id=project_id,
            **metrics_data
        )
        db.add(db_metrics)
        db.commit()
        db.refresh(db_metrics)
        return db_metrics

    def get_latest(self, db: Session, project_id: int) -> Optional[ProjectMetrics]:
        return db.query(ProjectMetrics).filter(
            ProjectMetrics.project_id == project_id
        ).order_by(desc(ProjectMetrics.date)).first()

    def get_by_date_range(self, db: Session, project_id: int, start_date: datetime, end_date: datetime) -> List[ProjectMetrics]:
        return db.query(ProjectMetrics).filter(
            and_(
                ProjectMetrics.project_id == project_id,
                ProjectMetrics.date >= start_date,
                ProjectMetrics.date <= end_date
            )
        ).order_by(asc(ProjectMetrics.date)).all()


class UserActivityCRUD:
    def create(self, db: Session, user_id: int, project_id: int, activity_type: str, 
               activity_data: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None) -> UserActivity:
        db_activity = UserActivity(
            user_id=user_id,
            project_id=project_id,
            activity_type=activity_type,
            activity_data=activity_data,
            session_id=session_id
        )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity

    def get_recent_activities(self, db: Session, project_id: int, limit: int = 50) -> List[UserActivity]:
        return db.query(UserActivity).options(
            joinedload(UserActivity.user)
        ).filter(
            UserActivity.project_id == project_id
        ).order_by(desc(UserActivity.timestamp)).limit(limit).all()

    def get_user_activities(self, db: Session, user_id: int, project_id: int, limit: int = 100) -> List[UserActivity]:
        return db.query(UserActivity).filter(
            and_(
                UserActivity.user_id == user_id,
                UserActivity.project_id == project_id
            )
        ).order_by(desc(UserActivity.timestamp)).limit(limit).all()


# Initialize CRUD instances
project_crud = ProjectCRUD()
task_crud = TaskCRUD()
bug_crud = BugCRUD()
feedback_crud = FeedbackCRUD()
release_crud = ReleaseCRUD()
code_review_crud = CodeReviewCRUD()
project_metrics_crud = ProjectMetricsCRUD()
user_activity_crud = UserActivityCRUD() 