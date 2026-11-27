import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Link,
} from "react-router-dom";

import "./styles.css";


const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


function Workout({ user }) {

  // =====================================================
  // REFS
  // =====================================================

  const videoRef =
    useRef(null);

  const canvasRef =
    useRef(null);

  const streamRef =
    useRef(null);

  const analysisIntervalRef =
    useRef(null);

  const analysisSessionRef =
    useRef(null);

  const analysisInFlightRef =
    useRef(false);


  // =====================================================
  // STATE
  // =====================================================

  const [exercise, setExercise] =
    useState("Squat");

  const [cameraStarted, setCameraStarted] =
    useState(false);

  const [error, setError] =
    useState("");

  const [reps, setReps] =
    useState(0);

  const [correctReps, setCorrectReps] =
    useState(0);

  const [incorrectReps, setIncorrectReps] =
    useState(0);

  const [kneeAngle, setKneeAngle] =
    useState(null);

  const [state, setState] =
    useState("UP");

  const [techniqueScore, setTechniqueScore] =
    useState(0);

  const [feedback, setFeedback] =
    useState("");

  const [detectedExercise, setDetectedExercise] =
    useState("Analyzing movement");

  const [exerciseConfidence, setExerciseConfidence] =
    useState(0);

  const [bodyDetected, setBodyDetected] =
    useState(false);

  const [analyzing, setAnalyzing] =
    useState(false);

  // IMPORTANT:
  // Controls whether fullscreen overlays are visible.
  const [isFullscreen, setIsFullscreen] =
    useState(false);


  // =====================================================
  // RESET WORKOUT STATS
  // =====================================================

  const resetStats = () => {

    setReps(0);

    setCorrectReps(0);

    setIncorrectReps(0);

    setKneeAngle(null);

    setState("UP");

    setTechniqueScore(0);

    setFeedback("");

    setDetectedExercise("Analyzing movement");

    setExerciseConfidence(0);

    setBodyDetected(false);

    setAnalyzing(false);
  };

  const createAnalysisSessionId = () => {
    if (window.crypto?.randomUUID) {
      return window.crypto.randomUUID();
    }

    return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  };

  const resetBackendAnalysis = async (sessionId, selectedExercise) => {
    const data = new FormData();
    data.append("session_id", sessionId);
    data.append("exercise", selectedExercise);

    const response = await fetch(`${API_URL}/analysis/reset`, {
      method: "POST",
      body: data,
    });

    if (!response.ok) {
      throw new Error("Could not initialize the workout analysis session.");
    }
  };


  // =====================================================
  // REQUEST CAMERA
  // =====================================================

  const startCamera = async () => {

    try {

      setError("");

      console.log(
        "Requesting camera..."
      );


      if (!navigator.mediaDevices) {

        throw new Error(
          "Camera API is not available in this browser."
        );

      }


      const stream =
        await navigator.mediaDevices.getUserMedia({

          video: {

            width: {
              ideal: 1280,
            },

            height: {
              ideal: 720,
            },

            facingMode: "user",

          },

          audio: false,

        });


      console.log(
        "Camera permission granted."
      );


      console.log(
        "Stream:",
        stream
      );


      const tracks =
        stream.getVideoTracks();


      console.log(
        "Video tracks:",
        tracks
      );


      if (tracks.length === 0) {

        throw new Error(
          "No camera was found."
        );

      }


      console.log(
        "Camera device:",
        tracks[0].label
      );


      streamRef.current =
        stream;


      // Reset workout statistics
      resetStats();

      const sessionId = createAnalysisSessionId();
      analysisSessionRef.current = sessionId;
      await resetBackendAnalysis(sessionId, exercise);

      // Camera is not fullscreen when first opened
      setIsFullscreen(false);

      // Show camera UI
      setCameraStarted(true);

    }

    catch (err) {

      console.error(
        "Camera error:",
        err
      );


      setError(
        err.message ||
        "Could not open the camera."
      );

    }

  };


  // =====================================================
  // ATTACH CAMERA STREAM
  // =====================================================

  useEffect(() => {

    if (
      !cameraStarted ||
      !videoRef.current ||
      !streamRef.current
    ) {

      return;

    }


    const video =
      videoRef.current;

    const stream =
      streamRef.current;


    console.log(
      "Attaching camera stream to video..."
    );


    video.srcObject =
      stream;


    const startVideo =
      async () => {

        try {

          await video.play();


          console.log(
            "VIDEO PLAYING"
          );


          console.log(
            "Video width:",
            video.videoWidth
          );


          console.log(
            "Video height:",
            video.videoHeight
          );

        }

        catch (err) {

          console.error(
            "Video play error:",
            err
          );


          setError(
            "Camera opened, but video could not start."
          );

        }

      };


    if (
      video.readyState >= 2
    ) {

      startVideo();

    }

    else {

      video.onloadedmetadata =
        startVideo;

    }


    return () => {

      video.onloadedmetadata =
        null;

    };

  }, [cameraStarted]);


  // =====================================================
  // FULLSCREEN CHANGE LISTENER
  // =====================================================

  useEffect(() => {

    const handleFullscreenChange =
      () => {

        const fullscreen =
          document.fullscreenElement !== null;

        setIsFullscreen(fullscreen);

      };


    document.addEventListener(
      "fullscreenchange",
      handleFullscreenChange
    );


    return () => {

      document.removeEventListener(
        "fullscreenchange",
        handleFullscreenChange
      );

    };

  }, []);


  // =====================================================
  // ANALYZE CURRENT CAMERA FRAME
  // =====================================================

  const analyzeFrame =
    async () => {

      if (analysisInFlightRef.current) {
        return;
      }

      const video =
        videoRef.current;

      const canvas =
        canvasRef.current;


      if (
        !video ||
        !canvas
      ) {

        return;

      }


      if (
        video.readyState < 2 ||
        video.videoWidth === 0 ||
        video.videoHeight === 0
      ) {

        return;

      }


      try {

        analysisInFlightRef.current = true;

        setAnalyzing(true);


        // -------------------------------------------------
        // Canvas dimensions
        // -------------------------------------------------

        canvas.width =
          video.videoWidth;

        canvas.height =
          video.videoHeight;


        const context =
          canvas.getContext("2d");


        if (!context) {

          return;

        }


        // -------------------------------------------------
        // Draw camera frame
        // -------------------------------------------------

        context.drawImage(

          video,

          0,

          0,

          canvas.width,

          canvas.height

        );


        // -------------------------------------------------
        // Convert frame to JPEG
        // -------------------------------------------------

        const blob =
          await new Promise(
            (resolve) => {

              canvas.toBlob(

                resolve,

                "image/jpeg",

                0.7

              );

            }
          );


        if (!blob) {

          return;

        }


        // -------------------------------------------------
        // FormData
        // -------------------------------------------------

        const formData =
          new FormData();


        formData.append(

          "file",

          blob,

          "frame.jpg"

        );


        // IMPORTANT:
        // Send selected exercise
        // to backend.

        formData.append(

          "exercise",

          exercise

        );

        formData.append(
          "session_id",
          analysisSessionRef.current
        );


        // -------------------------------------------------
        // API REQUEST
        // -------------------------------------------------

        const response =
          await fetch(

            `${API_URL}/analysis/pose`,

            {

              method: "POST",

              body: formData,

            }

          );


        if (!response.ok) {

          throw new Error(

            `Analysis API returned ${response.status}`

          );

        }


        // -------------------------------------------------
        // Response
        // -------------------------------------------------

        const data =
          await response.json();


        console.log(
          "Pose result:",
          data
        );


        // -------------------------------------------------
        // Body detection
        // -------------------------------------------------

        setBodyDetected(
          data.detected === true
        );


        // -------------------------------------------------
        // Analysis data
        // -------------------------------------------------

        if (
          data.detected
        ) {

          const angle =
            data.angle ??
            data.knee_angle;


          setKneeAngle(
            angle ?? null
          );


          setReps(
            data.reps ?? 0
          );


          setCorrectReps(
            data.correct_reps ?? 0
          );


          setIncorrectReps(
            data.incorrect_reps ?? 0
          );


          setState(
            data.state ?? "UP"
          );


          setTechniqueScore(
            data.technique_score ?? 0
          );


          setFeedback(
            data.feedback ?? ""
          );

          setDetectedExercise(
            data.detected_exercise ?? "Analyzing movement"
          );

          setExerciseConfidence(
            data.exercise_confidence ?? 0
          );

        }

        else {

          setFeedback(
            data.feedback ||
            "Move your full body into view."
          );

        }

      }

      catch (err) {

        console.error(
          "Frame analysis error:",
          err
        );

      }

      finally {

        setAnalyzing(false);
        analysisInFlightRef.current = false;

      }

    };


  // =====================================================
  // START LIVE ANALYSIS
  // =====================================================

  useEffect(() => {

    if (!cameraStarted) {

      return;

    }


    analysisIntervalRef.current =
      setInterval(

        analyzeFrame,

        250

      );


    return () => {

      if (
        analysisIntervalRef.current
      ) {

        clearInterval(
          analysisIntervalRef.current
        )   ;


        analysisIntervalRef.current =
          null;

      }

    };

  }, [
    cameraStarted,
    exercise,
  ]);


  // =====================================================
  // FULLSCREEN CAMERA
  // =====================================================

  const toggleFullscreen =
    async () => {

      const camera =
        document.getElementById(
          "workout-camera"
        );


      if (!camera) {

        return;

      }


      try {

        if (
          !document.fullscreenElement
        ) {

          await camera.requestFullscreen();

        }

        else {

          await document.exitFullscreen();

        }

      }

      catch (err) {

        console.error(
          "Fullscreen error:",
          err
        );

      }

    };


  // =====================================================
  // STOP CAMERA
  // =====================================================

  const stopCamera =
    () => {

      console.log(
        "Stopping camera..."
      );


      // Stop analysis timer

      if (
        analysisIntervalRef.current
      ) {

        clearInterval(
          analysisIntervalRef.current
        );


        analysisIntervalRef.current =
          null;

      }


      // Exit fullscreen if active

      if (
        document.fullscreenElement
      ) {

        document.exitFullscreen()
          .catch(() => {});

      }


      // Make sure overlay disappears

      setIsFullscreen(false);


      // Stop camera tracks

      if (
        streamRef.current
      ) {

        streamRef.current
          .getTracks()
          .forEach(
            (track) => {

              track.stop();

            }
          );


        streamRef.current =
          null;

      }


      // Remove video stream

      if (
        videoRef.current
      ) {

        videoRef.current.srcObject =
          null;

      }


      // Reset UI

      setCameraStarted(
        false
      );


      resetStats();

      analysisSessionRef.current = null;
      analysisInFlightRef.current = false;


      setError("");

    };


  // =====================================================
  // CLEANUP
  // =====================================================

  useEffect(() => {

    return () => {

      if (
        analysisIntervalRef.current
      ) {

        clearInterval(
          analysisIntervalRef.current
        );

      }


      if (
        streamRef.current
      ) {

        streamRef.current
          .getTracks()
          .forEach(
            (track) => {

              track.stop();

            }
          );

      }

    };

  }, []);


  // =====================================================
  // UI
  // =====================================================

  return (

    <main className="app-shell">


      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside>


        {/* BRAND */}

        <Link
          className="brand"
          to="/dashboard"
        >

          <span className="brand-mark">
            F
          </span>

          FitMotion

        </Link>


        {/* SECTION TITLE */}

        <div className="side-label">
          OVERVIEW
        </div>


        {/* DASHBOARD */}

        <Link
          to="/dashboard"
        >
          ⌂ Dashboard
        </Link>


        {/* AI WORKOUT */}

        <Link
          className="nav-active"
          to="/workout"
        >
          ◌ AI Workout
        </Link>


        {/* VIDEO ANALYSIS */}

        <Link
          to="/video-analysis"
        >
          ◉ Video Analysis
        </Link>


        {/* PROGRESS

        <a
          className="nav-disabled"
        >

          ↗ Progress

          <small>
            Coming soon
          </small>

        </a>
        */}


      </aside>


      {/* =================================================
          WORKOUT CONTENT
      ================================================= */}

      <section className="workout-page">


        <div className="workout-content">


          {/* =================================================
              HEADER
          ================================================= */}

          <div className="workout-header">


            <p className="eyebrow">
              AI WORKOUT
            </p>


            <h1>
              Ready,{" "}
              {user?.full_name
                ?.split(" ")[0] ||
                "Athlete"}?
            </h1>


            <p className="muted">
              Choose an exercise and start
              your session.
            </p>


          </div>


          {/* =================================================
              BEFORE CAMERA
          ================================================= */}

          {!cameraStarted && (

            <section className="empty-card">


              <p className="eyebrow">
                SELECT EXERCISE
              </p>


              <h2>
                Start your workout
              </h2>


              <select
                className="exercise-select"
                value={exercise}
                onChange={(e) => {

                  setExercise(
                    e.target.value
                  );

                  resetStats();

                  analysisSessionRef.current =
                    createAnalysisSessionId();

                  setError("");

                }}
              >

                <option value="Squat">
                  Squat
                </option>


                <option value="Lunge">
                  Lunge
                </option>


                <option value="Bicep Curl">
                  Bicep Curl
                </option>


                <option value="Push Up">
                  Push Up
                </option>


                <option value="Running">
                  Running
                </option>

              </select>


              <p className="selected-exercise">

                Selected exercise:

                {" "}

                <strong>
                  {exercise}
                </strong>

              </p>


              <div className="workout-controls">

                <button
                  className="button"
                  onClick={startCamera}
                >
                  Start Workout →
                </button>

              </div>


              {error && (

                <p className="error">
                  {error}
                </p>

              )}


            </section>

          )}


          {/* =================================================
              LIVE CAMERA
          ================================================= */}

          {cameraStarted && (

            <section className="empty-card">


              <p className="eyebrow">
                LIVE WORKOUT
              </p>


              <h2>
                {exercise}
              </h2>

              <p className="selected-exercise">
                Detected: <strong>{detectedExercise}</strong>
                {exerciseConfidence > 0 && ` (${Math.round(exerciseConfidence)}%)`}
              </p>


              {/* =================================================
                  CAMERA
              ================================================= */}

              <div
                className="camera-container"
                id="workout-camera"
              >


                {/* CAMERA VIDEO */}

                <video
                  ref={videoRef}
                  className="workout-video"
                  autoPlay
                  playsInline
                  muted
                />


                {/* =================================================
                    FULLSCREEN-ONLY OVERLAYS

                    These are rendered ONLY when fullscreen.
                ================================================= */}

                {isFullscreen && (

                  <>

                    {/* =========================================
                        REP COUNTER
                    ========================================= */}

                    <div className="camera-rep-overlay">

                      <span className="camera-stat-label">
                        REPS
                      </span>


                      <span className="camera-rep-number">
                        {reps}
                      </span>


                      <div className="camera-correct-reps">

                        <span>
                          ✓
                        </span>

                        {correctReps} correct

                      </div>

                    </div>


                    {/* =========================================
                        EXERCISE + SCORE
                    ========================================= */}

                    <div className="camera-info-overlay">


                      <div className="camera-exercise">

                        <span className="camera-live-dot"></span>

                        LIVE

                        <strong>
                          {exercise}
                        </strong>

                      </div>


                      <div className="camera-score">

                        <span>
                          SCORE
                        </span>

                        <strong>
                          {techniqueScore}
                        </strong>

                      </div>


                    </div>


                    {/* =========================================
                        AI FEEDBACK
                    ========================================= */}

                    {feedback && (

                      <div className="camera-feedback">

                        {feedback}

                      </div>

                    )}

                  </>

                )}


                {/* =================================================
                    FULLSCREEN BUTTON

                    This stays visible in both modes.
                ================================================= */}

                <button
                  type="button"
                  className="camera-fullscreen-btn"
                  onClick={toggleFullscreen}
                  title={
                    isFullscreen
                      ? "Exit full screen"
                      : "Full screen camera"
                  }
                  aria-label={
                    isFullscreen
                      ? "Exit full screen"
                      : "Full screen camera"
                  }
                >

                  {isFullscreen
                    ? "⛶"
                    : "⛶"}

                </button>


              </div>


              {/* =================================================
                  HIDDEN CANVAS
              ================================================= */}

              <canvas
                ref={canvasRef}
                style={{
                  display: "none",
                }}
              />


              {/* =================================================
                  NORMAL MODE STATS

                  These remain below the camera.
                  They are NOT the fullscreen overlay.
              ================================================= */}

              <div className="workout-stats">


                {/* REPS */}

                <div className="stat-card">

                  <span>
                    REPS
                  </span>

                  <strong>
                    {reps}
                  </strong>

                </div>


                {/* ANGLE */}

                <div className="stat-card">

                  <span>
                    ANGLE
                  </span>

                  <strong>

                    {kneeAngle !== null
                      ? `${kneeAngle}°`
                      : "--"}

                  </strong>

                </div>


                {/* STATE */}

                <div className="stat-card">

                  <span>
                    STATE
                  </span>

                  <strong>
                    {state}
                  </strong>

                </div>


              </div>


              {/* =================================================
                  WORKOUT INFORMATION
              ================================================= */}

              <div className="workout-info">


                <p>

                  <strong>
                    Athlete:
                  </strong>

                  {" "}

                  {user?.full_name ||
                    "Athlete"}

                </p>


                <p>

                  <strong>
                    Body:
                  </strong>

                  {" "}

                  {bodyDetected
                    ? "Detected"
                    : "Searching..."}

                </p>


                <p>

                  <strong>
                    AI:
                  </strong>

                  {" "}

                  {analyzing
                    ? "Analyzing..."
                    : "Ready"}

                </p>


              </div>


              {/* =================================================
                  STOP BUTTON
              ================================================= */}

              <div className="workout-controls">

                <button
                  className="button"
                  onClick={stopCamera}
                >
                  Stop Workout
                </button>

              </div>


            </section>

          )}


        </div>

      </section>

    </main>

  );

}


export default Workout;
