import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthContext } from "@galvanize-inc/jwtdown-for-react";

export default function WorkoutPage() {
  const navigate = useNavigate();

  const [workouts, setWorkouts] = useState([]);
  const [userName, setUserName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { token } = useAuthContext();

  useEffect(() => {
    const fetchWorkouts = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/workouts");
        if (response.ok) {
          const data = await response.json();
          setWorkouts(data);
        } else {
          throw new Error("Failed to fetch workouts.");
        }
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkouts();
  }, []);

  async function handleCompleteWorkout(workoutId) {
    try {
      const response = await fetch(
        `http://localhost:8000/api/workouts/${workoutId}/complete`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          credentials: "include",
        }
      );
      if (response.ok) {
        setWorkouts((prevWorkouts) =>
          prevWorkouts.filter((workout) => workout.id !== workoutId)
        );
      } else {
        console.error("Failed to complete workout.");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }

  useEffect(() => {
    if (!token) {
      navigate("/Login");
      return;
    }

    const fetchUserData = async () => {
      setLoading(true);
      let id;
      try {
        const response = await fetch(`http://localhost:8000/token`, {
          method: "GET",
          headers: {
            Authorization: `Bearer${token}`,
          },
          credentials: "include",
        });
        if (response.ok) {
          const data = await response.json();
          id = data.account.id;
        } else {
          throw new Error("Failed to get token user data.");
        }
      } catch (err) {
        setError(err);
      }
      if (id) {
        console.log("HERE", id);
        try {
          const userResponse = await fetch(
            `http://localhost:8000/api/accounts/detail?account_id=${id}`
          );
          if (userResponse.ok) {
            const userData = await userResponse.json();
            setUserName(userData.first_name);
          } else {
            throw new Error("Failed to fetch user data.");
          }
        } catch (err) {
          setError(err);
        }
      }
    };
    fetchUserData();
  }, [navigate, token]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error loading workout: {error.message}</div>;

  return (
    <div className="form">
      <h1 className="form__header">{userName}'s Workouts</h1>
      <div className="workout">
        {workouts.map((workout) => (
          <div className="row" key={workout.id}>
            <div className="workout__header">
              <h2 className="heading-tertiary">Workout name: {workout.name}</h2>
              <p className="heading-tertiary">
                Difficulty level: {workout.difficulty}
              </p>
            </div>
            <div className="workout__header">
              <p className="heading-tertiary">
                Workout description: {workout.description}
              </p>
              <p className="heading-tertiary">Date: {workout.date}</p>
            </div>
            <div>
              {workout.exercises.map((exercise, index) => (
                <div className="workout__text-box" key={index}>
                  <p>Exercise Name: {exercise.name}</p>
                  <p>Exercise Type: {exercise.type}</p>
                  <p>Targeted Muscle Group:{exercise.muscle}</p>
                  <p>Equipment: {exercise.equipment}</p>
                  <p>Difficulty: {exercise.difficulty}</p>
                  <p>Instructions: {exercise.instructions}</p>
                </div>
              ))}
              <div className="form__button">
                <button
                  className="btn btn--register"
                  onClick={() => handleCompleteWorkout(workout.id, token)}
                >
                  Mark Workout Completed
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
