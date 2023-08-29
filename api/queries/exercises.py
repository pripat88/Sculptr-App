from pydantic import BaseModel
from typing import Union, List
from queries.pool import pool


class Error(BaseModel):
    message: str


class ExerciseIn(BaseModel):
    name: str
    type: str
    muscle: str
    equipment: str
    difficulty: str
    instructions: str


class ExerciseOut(BaseModel):
    id: int
    name: str
    type: str
    muscle: str
    equipment: str
    difficulty: str
    instructions: str


class ExerciseRepository:
    def create(self, exercise: ExerciseIn) -> Union[ExerciseOut, Error]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                            INSERT INTO exercises
                                (name, type, muscle, equipment, difficulty, instructions)
                            VALUES
                                (%s, %s, %s, %s, %s, %s)
                            RETURNING id;
                            """,
                        [
                            exercise.name,
                            exercise.type,
                            exercise.muscle,
                            exercise.equipment,
                            exercise.difficulty,
                            exercise.instructions,
                        ],
                    )
                    id = result.fetchone()[0]

                    return self.exercise_in_to_out(id, exercise)

        except Exception as e:
            print(e)
            return False

    def get_all(self) -> Union[Error, List[ExerciseOut]]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT * FROM exercises;
                        """
                    )
                    return [
                        self.record_to_exercise_out(record)
                        for record in result
                    ]
        except Exception as e:
            print(e)
            return {"message": "Could not get all exercises"}

    def get_all_by_difficulty(self, difficulty: str) -> List[ExerciseOut]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT id, name, type, muscle, equipment, difficulty, instructions
                        FROM exercises
                        WHERE difficulty = %s
                        """,
                        [difficulty],
                    )
                    records = result.fetchall()
                    return [
                        self.record_to_exercise_out(record)
                        for record in records
                    ]
        except Exception as e:
            print(e)
            return {"message": "Could not get the exercises by difficulty"}

    def get_all_by_muscle(self, muscle: str) -> List[ExerciseOut]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT id, name, type, muscle, equipment, difficulty, instructions
                        FROM exercises
                        WHERE muscle = %s
                        """,
                        [muscle],
                    )
                    records = result.fetchall()
                    return [
                        self.record_to_exercise_out(record)
                        for record in records
                    ]
        except Exception as e:
            print(e)
            return {"message": "Could not get the exercises by muscle"}

    def get_all_by_type(self, type: str) -> List[ExerciseOut]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT id, name, type, muscle, equipment, difficulty, instructions
                        FROM exercises
                        WHERE type = %s
                        """,
                        [type],
                    )
                    records = result.fetchall()
                    return [
                        self.record_to_exercise_out(record)
                        for record in records
                    ]
        except Exception as e:
            print(e)
            return {"message": "Could not get the exercises by type"}

    def get_by_name(self, name: str) -> Union[ExerciseOut, Error]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT id, name, type, muscle, equipment, difficulty, instructions
                        FROM exercises
                        WHERE name = %s
                        """,
                        [name],
                    )
                    record = result.fetchone()
                    if record:
                        return self.record_to_exercise_out(record)
                    else:
                        return {"message": "Could not find that exercise"}
        except Exception as e:
            print(e)
            return {"message": "Could not get the exercise by name"}

    def exercise_in_to_out(self, id: int, exercise: ExerciseIn):
        old_data = exercise.dict()
        return ExerciseIn(id=id, **old_data)

    def record_to_exercise_out(self, record):
        return ExerciseOut(
            id=record[0],
            name=record[1],
            type=record[2],
            muscle=record[3],
            equipment=record[4],
            difficulty=record[5],
            instructions=record[6],
        )
