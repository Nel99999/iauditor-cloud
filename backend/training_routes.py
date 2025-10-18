from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from training_models import TrainingCourse, EmployeeTraining, TrainingCourseCreate, TrainingStats
from auth_utils import get_current_user

router = APIRouter(prefix="/training", tags=["Training"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: TrainingCourseCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create training course"""
    user = await get_current_user(request, db)
    
    course = TrainingCourse(
        organization_id=user["organization_id"],
        course_code=course_data.course_code,
        name=course_data.name,
        description=course_data.description,
        course_type=course_data.course_type,
        duration_hours=course_data.duration_hours,
        valid_for_years=course_data.valid_for_years,
        created_by=user["id"],
    )
    
    course_dict = course.model_dump()
    course_dict["created_at"] = course_dict["created_at"].isoformat()
    
    await db.training_courses.insert_one(course_dict.copy())
    return course_dict


@router.get("/courses")
async def list_courses(
    request: Request,
    course_type: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List training courses"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"], "is_active": True}
    if course_type:
        query["course_type"] = course_type
    
    courses = await db.training_courses.find(query, {"_id": 0}).to_list(1000)
    return courses


@router.post("/completions")
async def record_completion(
    completion_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Record training completion"""
    user = await get_current_user(request, db)
    
    course = await db.training_courses.find_one({"id": completion_data.get("course_id")})
    
    # Calculate expiry
    expires_at = None
    if course and course.get("valid_for_years"):
        expiry_date = datetime.now(timezone.utc) + timedelta(days=365 * course["valid_for_years"])
        expires_at = expiry_date.strftime("%Y-%m-%d")
    
    training = EmployeeTraining(
        employee_id=completion_data.get("employee_id"),
        employee_name=completion_data.get("employee_name"),
        course_id=completion_data.get("course_id"),
        course_name=course.get("name") if course else "",
        completed_at=completion_data.get("completed_at"),
        score=completion_data.get("score"),
        passed=completion_data.get("passed", True),
        expires_at=expires_at,
    )
    
    training_dict = training.model_dump()
    training_dict["created_at"] = training_dict["created_at"].isoformat()
    
    await db.employee_training.insert_one(training_dict.copy())
    return training_dict


@router.get("/employees/{employee_id}/transcript")
async def get_employee_transcript(
    employee_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get employee training history"""
    user = await get_current_user(request, db)
    
    trainings = await db.employee_training.find(
        {"employee_id": employee_id},
        {"_id": 0}
    ).sort("completed_at", -1).to_list(1000)
    
    return trainings


@router.get("/expired")
async def get_expired_certifications(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get expired certifications"""
    user = await get_current_user(request, db)
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    expired = await db.employee_training.find(
        {
            "expires_at": {"$ne": None, "$lt": today}
        },
        {"_id": 0}
    ).to_list(1000)
    
    return expired


@router.get("/stats")
async def get_training_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get training statistics"""
    user = await get_current_user(request, db)
    
    courses = await db.training_courses.find({"organization_id": user["organization_id"]}, {"_id": 0}).to_list(10000)
    trainings = await db.employee_training.find({}, {"_id": 0}).to_list(10000)
    
    month_start = datetime.now(timezone.utc).replace(day=1).isoformat()
    completed_month = len([t for t in trainings if t.get("completed_at") and t.get("completed_at") >= month_start])
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    expired = len([t for t in trainings if t.get("expires_at") and t.get("expires_at") < today])
    
    stats = TrainingStats(
        total_courses=len(courses),
        total_enrollments=len(trainings),
        completed_this_month=completed_month,
        expired_certifications=expired
    )
    
    return stats.model_dump()
