import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "./services/api";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


function VideoAnalysis({ token }) {

  // ==========================================
  // STATE
  // ==========================================

  const [exercise, setExercise] = useState("");

  const [selectedFile, setSelectedFile] =
    useState(null);

  const [analyzing, setAnalyzing] =
    useState(false);

  const [result, setResult] =
    useState(null);

  const [error, setError] =
    useState("");

  const [saved, setSaved] =
    useState(false);

  const [saving, setSaving] =
    useState(false);


  // ==========================================
  // EXERCISES
  // ==========================================

  const exercises = [
    "Squat",
    "Lunge",
    "Bicep Curl",
    "Push Up",
    "Running",
  ];


  // ==========================================
  // FILE SELECT
  // ==========================================

  const handleFileChange = (event) => {

    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);
    setResult(null);
    setSaved(false);
    setError("");
  };


  // ==========================================
  // ANALYZE VIDEO
  // ==========================================

  const analyzeVideo = async () => {

    if (!exercise) {

      setError(
        "Please select an exercise first."
      );

      return;
    }

    if (!selectedFile) {

      setError(
        "Please choose a workout video."
      );

      return;
    }


    try {

      setAnalyzing(true);
      setError("");
      setResult(null);


      const formData =
        new FormData();

      formData.append(
        "file",
        selectedFile
      );

      /*
       * The backend currently accepts
       * the video file.
       *
       * We also send the selected
       * exercise so the backend can
       * use exercise-specific rules.
       */

      formData.append(
        "exercise",
        exercise
      );


      const response =
        await fetch(
          `${API_URL}/analysis/video`,
          {
            method: "POST",
            body: formData,
          }
        );


      if (!response.ok) {

        let message =
          `Analysis failed (${response.status})`;

        try {

          const errorData =
            await response.json();

          if (errorData.detail) {
            message =
              errorData.detail;
          }

        } catch {
          // Ignore JSON parsing error
        }

        throw new Error(message);
      }


      const data =
        await response.json();

      console.log(
        "Video analysis result:",
        data
      );


      setResult(data);
      setSaved(false);

    } catch (err) {

      console.error(
        "Video analysis error:",
        err
      );

      setError(
        err.message ||
        "Could not analyze the video."
      );

    } finally {

      setAnalyzing(false);
    }
  };

  const saveWorkout = async () => {
    if (!result || saved) return;

    try {
      setSaving(true);
      await api.saveWorkout(token, {
        exercise: result.exercise || exercise,
        total_reps: result.reps || 0,
        correct_reps: result.correct_reps || 0,
        incorrect_reps: result.incorrect_reps || 0,
        technique_score: result.technique_score ?? null,
        duration_seconds: Math.round(result.duration_seconds || 0),
        analysis_video_url: result.analyzed_video || null,
      });
      setSaved(true);
    } catch (err) {
      setError(err.message || "Could not save this workout.");
    } finally {
      setSaving(false);
    }
  };


  // ==========================================
  // FORMAT NUMBER
  // ==========================================

  const formatNumber = (
    value,
    digits = 2
  ) => {

    if (
      value === null ||
      value === undefined
    ) {
      return "—";
    }

    const number =
      Number(value);

    if (Number.isNaN(number)) {
      return "—";
    }

    return number.toFixed(digits);
  };


  // ==========================================
  // RENDER
  // ==========================================

  return (

    <main className="app-shell">


      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside>

        <Link
          className="brand"
          to="/dashboard"
        >

          <span className="brand-mark">
            F
          </span>

          FitMotion

        </Link>


        <div className="side-label">
          OVERVIEW
        </div>


        <Link
          to="/dashboard"
        >
          ⌂ Dashboard
        </Link>


        <Link
          to="/workout"
        >
          ◌ AI Workout
        </Link>


        <Link
          className="nav-active"
          to="/video-analysis"
        >
          ◉ Video Analysis
        </Link>

      {/*
        <a className="nav-disabled">

          ↗ Progress

          <small>
            Coming soon
          </small>

        </a>*/}

      </aside>



      {/* =================================================
          MAIN CONTENT
      ================================================= */}

      <section
        className="video-analysis-page"
      >


        {/* =================================================
            HEADER
        ================================================= */}

        <div
          className="video-analysis-header"
        >

          <p className="eyebrow">
            AI MOVEMENT ANALYSIS
          </p>


          <h1>
            Analyze Your Workout
          </h1>


          <p>
            Select your exercise and upload
            your workout video. FitMotion will
            analyze your repetitions, joint
            angles and technique.
          </p>

        </div>



        {/* =================================================
            UPLOAD CARD
        ================================================= */}

        <section
          className="video-upload-card"
        >


          {/* EXERCISE */}

          <div>

            <p className="eyebrow">
              SELECT EXERCISE
            </p>


            <select
              className="exercise-select"
              value={exercise}
              onChange={(event) => {

                setExercise(
                  event.target.value
                );

                setResult(null);
                setError("");

              }}
            >

              <option value="">
                Choose an exercise
              </option>


              {exercises.map(
                (item) => (

                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>

                )
              )}

            </select>

          </div>



          {/* =================================================
              FILE UPLOAD
          ================================================= */}

          <label
            className="upload-box"
          >

            <input
              type="file"
              accept=".mp4,.avi,.mov,.webm,.mkv,video/*"
              onChange={handleFileChange}
            />


            <div className="upload-title">

              {selectedFile
                ? selectedFile.name
                : "Choose a workout video"}

            </div>


            <div className="upload-subtitle">

              {selectedFile
                ? `${(
                    selectedFile.size /
                    (1024 * 1024)
                  ).toFixed(2)} MB`
                : "MP4, AVI, MOV, WEBM or MKV"}

            </div>

          </label>



          {/* =================================================
              SELECTED EXERCISE INFO
          ================================================= */}

          {exercise && (

            <div className="workout-info">

              <p>
                Exercise:
                {" "}
                <strong>
                  {exercise}
                </strong>
              </p>

            </div>

          )}



          {/* =================================================
              ANALYZE BUTTON
          ================================================= */}

          <button
            type="button"
            className="primary-button"
            onClick={analyzeVideo}
            disabled={
              analyzing ||
              !selectedFile ||
              !exercise
            }
          >

            {analyzing
              ? "Analyzing video..."
              : "Analyze Video →"}

          </button>



          {/* =================================================
              ERROR
          ================================================= */}

          {error && (

            <div
              className="analysis-error"
            >
              {error}
            </div>

          )}



          {/* =================================================
              LOADING
          ================================================= */}

          {analyzing && (

            <div
              className="analysis-loading"
            >

              <div
                className="loading-spinner"
              />

              <h3>
                Analyzing your workout
              </h3>

              <p>
                Detecting pose landmarks,
                calculating movement and
                analyzing technique.
              </p>

              <span>
                This may take a little while
                for longer videos.
              </span>

            </div>

          )}

        </section>



        {/* =================================================
            RESULTS
        ================================================= */}

        {result && (

          <section
            className="analyzed-video-section"
          >


            {/* RESULTS HEADER */}

            <div
              className="results-heading"
            >

              <p className="eyebrow">
                ANALYSIS COMPLETE
              </p>


              <h2>
                Your Workout Results
              </h2>


              <p>
                {result.exercise ||
                  exercise}
              </p>

              <button
                className="button small"
                onClick={saveWorkout}
                disabled={saving || saved}
              >
                {saved ? "Saved to dashboard" : saving ? "Saving…" : "Save workout"}
              </button>

            </div>



            {/* =================================================
                ANALYZED VIDEO
            ================================================= */}

            {result.analyzed_video && (

              <div
                className="analyzed-video-container"
              >

                <video
                  className="analyzed-video"
                  controls
                  playsInline
                  preload="metadata"
                >

                  <source
                    src={
                      `${API_URL}${result.analyzed_video}`
                    }
                    type="video/mp4"
                  />

                  Your browser does not
                  support video playback.

                </video>

              </div>

            )}



            {/* =================================================
                RESULT CARDS
            ================================================= */}

            <div
              className="analysis-results"
            >

              <div
                className="result-grid"
              >


                {/* REPS */}

                <article
                  className="result-card"
                >

                  <span>
                    REPS
                  </span>

                  <strong>
                    {result.reps ?? "—"}
                  </strong>

                </article>



                {/* TECHNIQUE SCORE */}

                <article
                  className="result-card"
                >

                  <span>
                    TECHNIQUE
                  </span>

                  <strong>
                    {result.technique_score ??
                      "—"}
                    {result.technique_score !==
                      undefined &&
                      result.technique_score !==
                      null
                      ? "%"
                      : ""}
                  </strong>

                </article>



                {/* AVERAGE ANGLE */}

                <article
                  className="result-card"
                >

                  <span>
                    AVERAGE ANGLE
                  </span>

                  <strong>
                    {formatNumber(
                      result.average_knee_angle
                    )}

                    {result.average_knee_angle !==
                      undefined &&
                      result.average_knee_angle !==
                      null
                      ? "°"
                      : ""}
                  </strong>

                </article>



                {/* STATE */}

                <article
                  className="result-card"
                >

                  <span>
                    FINAL STATE
                  </span>

                  <strong>
                    {result.final_state ||
                      result.state ||
                      "—"}
                  </strong>

                </article>

              </div>



              {/* =================================================
                  EXTRA RESULT INFORMATION
              ================================================= */}

              <div
                className="workout-info"
              >

                <p>
                  Correct reps:
                  {" "}
                  <strong>
                    {result.correct_reps ??
                      "—"}
                  </strong>
                </p>


                <p>
                  Incorrect reps:
                  {" "}
                  <strong>
                    {result.incorrect_reps ??
                      "—"}
                  </strong>
                </p>


                <p>
                  Minimum angle:
                  {" "}
                  <strong>
                    {formatNumber(
                      result.minimum_knee_angle
                    )}

                    {result.minimum_knee_angle !==
                      undefined &&
                      result.minimum_knee_angle !==
                      null
                      ? "°"
                      : ""}
                  </strong>
                </p>


                <p>
                  Maximum angle:
                  {" "}
                  <strong>
                    {formatNumber(
                      result.maximum_knee_angle
                    )}

                    {result.maximum_knee_angle !==
                      undefined &&
                      result.maximum_knee_angle !==
                      null
                      ? "°"
                      : ""}
                  </strong>
                </p>

              </div>



              {/* =================================================
                  FEEDBACK
              ================================================= */}

              {result.feedback && (

                <div
                  className="workout-info"
                >

                  <p>
                    Feedback:
                    {" "}
                    <strong>
                      {result.feedback}
                    </strong>
                  </p>

                </div>

              )}

            </div>

          </section>

        )}

      </section>

    </main>
  );
}


export default VideoAnalysis;
