from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Union
from queries.workouts import (
    Error,
    WorkoutIn,
    WorkoutRepository,
    WorkoutOut,
    WorkoutToDB,
)

from queries.exercises import ExerciseRepository

# from random import sample


router = APIRouter()


@router.post("/create", response_model=Union[WorkoutOut, Error])
async def create_workout(
    workout: WorkoutIn,
    workout_repo: WorkoutRepository = Depends(),
    exercise_repo: ExerciseRepository = Depends(),
):
    try:
        exercise_id_list = []
        exercises = workout.exercises
        # print("Exercises:", exercises)
        for exercise in exercises:
            # print(exercise)
            entry = exercise_repo.get_one_exercise(exercise.name)
            # print("At the endpoint:", entry)
            if entry:
                exercise_id_list.append(entry[0])
            else:
                entry = exercise_repo.create(exercise)
                exercise_id_list.append(entry.id)
        # print("Exercise ID List:", exercise_id_list)

        new_workout = WorkoutToDB(
            name=workout.name,
            difficulty=workout.difficulty,
            description=workout.description,
            date=workout.date,
        )
        # print("+++++++++++ NEW WORKOUT++++++:", new_workout)
        workout_id = workout_repo.create(new_workout)
        # print("^^^^^WORKOUT ID:", workout_id)

        for exercise_id in exercise_id_list:
            workout_repo.link_exercise_to_workout(workout_id, exercise_id)

        # query the join table to get the exercises with the workout_id
        for exercise in workout_repo.get_all():
            # build a WorkoutOut object
            workout_out = WorkoutOut(
                id=workout_id,
                name=workout.name,
                difficulty=workout.difficulty,
                description=workout.description,
                date=workout.date,
                exercises=exercises,
            )
        return workout_out

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.get("/", response_model=Union[list, Error])
async def get_all(
    workout_repo: WorkoutRepository = Depends(),
):
    try:
        return workout_repo.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.put("/{workout_id}", response_model=Union[WorkoutOut, Error])
def update_workout(
    workout_id: int,
    workout: WorkoutIn,
    workout_repo: WorkoutRepository = Depends(),
) -> Union[Error, WorkoutOut]:
    try:
        return workout_repo.update(workout_id, workout)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.delete("/{workout_id}", response_model=bool)
def delete_workout(
    workout_id: int,
    workout_repo: WorkoutRepository = Depends(),
) -> bool:
    try:
        return workout_repo.delete(workout_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.get("/{workout_id}", response_model=WorkoutOut)
def get_one_workout(
    workout_id: int,
    workout_repo: WorkoutRepository = Depends(),
) -> WorkoutOut:
    workout = workout_repo.get_one(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.get("/get_join_table", response_model=WorkoutToDB)
def get_join_table(
    workout_id: int,
    workout_repo: WorkoutRepository = Depends(),
) -> WorkoutToDB:
    workout = workout_repo.link_exercise_to_workout(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout
