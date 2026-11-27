import { useEffect, useState } from "react";
import { Link, Navigate, Route, Routes, useNavigate,}
from "react-router-dom";
import { api } from "./services/api";
import Workout from "./Workout";
import VideoAnalysis from "./VideoAnalysis";
import CustomCursor from "./CustomCursor";

const initialSignup = {
  full_name: "",
  email: "",
  password: "",
  confirm_password: "",
  age: "",
  gender: "",
  height_cm: "",
  weight_kg: "",
  sport: "Gym/Fitness",
  fitness_level: "beginner",
  fitness_goal: "improve_fitness",
};


/* =========================
   BRAND
========================= */

function Brand() {
  return (
    <Link className="brand" to="/">
      <span className="brand-mark">F</span>
      FitMotion
    </Link>
  );
}


/* =========================
   HEADER
========================= */

function Header() {
  return (
    <header>
      <Brand />

      <nav>
        <a href="#features">How it works</a>

        <a href="#science">Our approach</a>

        <Link className="text-link" to="/login">
          Log in
        </Link>

        <Link className="button small" to="/signup">
          Start free
        </Link>
      </nav>
    </header>
  );
}


/* =========================
   LANDING PAGE
========================= */

function Landing() {
  return (
    <main>
      <Header />

      <section className="hero">
        <div className="eyebrow">
          AI-POWERED MOVEMENT COACHING
        </div>

        <h1>
          Move well.
          <br />
          <em>Feel stronger.</em>
        </h1>

        <p>
          FitMotion helps you understand your movement,
          build consistent habits, and train with more confidence.
        </p>

        <div className="hero-actions">
          <Link className="button" to="/signup">
            Start your journey
            <span>→</span>
          </Link>

          <Link className="button ghost" to="/login">
            I have an account
          </Link>
        </div>

        <div className="hero-proof">
          <span>◉</span>
          Built for everyday fitness and sport
        </div>
      </section>


      <section id="features" className="features">
        <article>
          <b>01</b>

          <h2>
            Understand your form
          </h2>

          <p>
            Camera-based movement analysis designed to
            surface simple, useful coaching cues.
          </p>
        </article>

        <article>
          <b>02</b>

          <h2>
            Build your rhythm
          </h2>

          <p>
            Track sessions and reps in one calm,
            focused training space.
          </p>
        </article>

        <article>
          <b>03</b>

          <h2>
            See your progress
          </h2>

          <p>
            Review your personal data over time—not
            someone else’s benchmark.
          </p>
        </article>
      </section>


      <section id="science" className="statement">
        <p>
          Good training starts with <em>better awareness.</em>
        </p>

        <Link to="/signup">
          Create your athlete profile →
        </Link>
      </section>
    </main>
  );
}


/* =========================
   AUTH LAYOUT
========================= */

function AuthLayout({
  children,
  title,
  subtitle,
}) {
  return (
    <main className="auth-shell">

      <Link className="brand" to="/">
        <span className="brand-mark">F</span>
        FitMotion
      </Link>

      <section className="auth-card">

        <p className="eyebrow">
          WELCOME TO FITMOTION
        </p>

        <h1>
          {title}
        </h1>

        <p className="muted">
          {subtitle}
        </p>

        {children}

      </section>

    </main>
  );
}


/* =========================
   LOGIN
========================= */

function Login({ onAuth }) {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);


  async function submit(e) {
    e.preventDefault();

    setBusy(true);
    setError("");

    try {
      const result = await api.login({
        email,
        password,
      });

      onAuth(result);

      navigate("/dashboard");

    } catch (err) {
      setError(err.message);

    } finally {
      setBusy(false);
    }
  }


  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Your next good session starts here."
    >

      <form onSubmit={submit}>

        <label>
          Email

          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>


        <label>
          Password

          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>


        {error && (
          <p className="error">
            {error}
          </p>
        )}


        <button
          className="button full"
          disabled={busy}
        >
          {busy ? "Logging in…" : "Log in"}
        </button>


        <p className="form-footer">
          New to FitMotion?{" "}

          <Link to="/signup">
            Create an account
          </Link>
        </p>

      </form>

    </AuthLayout>
  );
}


/* =========================
   SIGNUP
========================= */

function Signup({ onAuth }) {
  const navigate = useNavigate();

  const [step, setStep] = useState(1);

  const [form, setForm] = useState(initialSignup);

  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);


  const set = (key) => (e) => {
    setForm({
      ...form,
      [key]: e.target.value,
    });
  };


  const next = () => {
    setError("");

    if (
      step === 1 &&
      (
        !form.full_name ||
        !form.email ||
        !form.age
      )
    ) {
      return setError(
        "Please complete your personal details."
      );
    }


    if (
      step === 2 &&
      (
        !form.height_cm ||
        !form.weight_kg ||
        !form.sport
      )
    ) {
      return setError(
        "Please complete your training details."
      );
    }


    setStep(step + 1);
  };


  async function submit(e) {
    e.preventDefault();

    if (
      form.password !== form.confirm_password
    ) {
      setError("Passwords do not match.");
      return;
    }


    setBusy(true);
    setError("");

    try {

      const payload = {
        ...form,

        age: Number(form.age),

        height_cm: Number(form.height_cm),

        weight_kg: Number(form.weight_kg),

        gender: form.gender || null,
      };


      const result = await api.register(payload);

      onAuth(result);

      navigate("/dashboard");

    } catch (err) {

      setError(err.message);

    } finally {

      setBusy(false);
    }
  }


  return (
    <AuthLayout
      title="Create your profile"
      subtitle="A few details help personalize FitMotion for you."
    >

      <div className="steps">

        {[
          "You",
          "Training",
          "Goals",
          "Account",
        ].map((label, index) => (

          <span
            className={
              step >= index + 1
                ? "active"
                : ""
            }
            key={label}
          >

            {index + 1}

            <small>
              {label}
            </small>

          </span>
        ))}

      </div>


      <form onSubmit={submit}>

        {/* STEP 1 */}

        {step === 1 && (
          <>

            <label>
              Full name

              <input
                value={form.full_name}
                onChange={set("full_name")}
                required
              />
            </label>


            <label>
              Email

              <input
                type="email"
                value={form.email}
                onChange={set("email")}
                required
              />
            </label>


            <label>
              Age

              <input
                type="number"
                min="13"
                max="120"
                value={form.age}
                onChange={set("age")}
                required
              />
            </label>


            <label>
              Gender{" "}

              <span className="optional">
                optional
              </span>

              <input
                value={form.gender}
                onChange={set("gender")}
              />
            </label>

          </>
        )}


        {/* STEP 2 */}

        {step === 2 && (
          <>

            <label>
              Primary activity

              <select
                value={form.sport}
                onChange={set("sport")}
              >
                <option>Gym/Fitness</option>
                <option>Running</option>
                <option>Football</option>
                <option>Cricket</option>
                <option>Basketball</option>
                <option>Tennis</option>
                <option>Other</option>
              </select>
            </label>


            <label>
              Height (cm)

              <input
                type="number"
                value={form.height_cm}
                onChange={set("height_cm")}
                required
              />
            </label>


            <label>
              Weight (kg)

              <input
                type="number"
                value={form.weight_kg}
                onChange={set("weight_kg")}
                required
              />
            </label>


            <label>
              Experience

              <select
                value={form.fitness_level}
                onChange={set("fitness_level")}
              >

                <option value="beginner">
                  Beginner
                </option>

                <option value="intermediate">
                  Intermediate
                </option>

                <option value="advanced">
                  Advanced
                </option>

              </select>

            </label>

          </>
        )}


        {/* STEP 3 */}

        {step === 3 && (
          <>

            <label>
              What matters most right now?

              <select
                value={form.fitness_goal}
                onChange={set("fitness_goal")}
              >

                <option value="improve_fitness">
                  Improve fitness
                </option>

                <option value="build_strength">
                  Build strength
                </option>

                <option value="improve_technique">
                  Improve technique
                </option>

                <option value="improve_flexibility">
                  Improve flexibility
                </option>

                <option value="sports_performance">
                  Sports performance
                </option>

                <option value="weight_management">
                  Weight management
                </option>

              </select>
            </label>


            <div className="choice-note">
              You can change this any time from your profile.
            </div>

          </>
        )}


        {/* STEP 4 */}

        {step === 4 && (
          <>

            <label>
              Create password

              <input
                type="password"
                value={form.password}
                onChange={set("password")}
                placeholder="8+ characters, letter and number"
                required
              />
            </label>


            <label>
              Confirm password

              <input
                type="password"
                value={form.confirm_password}
                onChange={set("confirm_password")}
                required
              />
            </label>

          </>
        )}


        {error && (
          <p className="error">
            {error}
          </p>
        )}


        <div className="form-actions">

          {step > 1 && (
            <button
              type="button"
              className="button ghost"
              onClick={() => setStep(step - 1)}
            >
              Back
            </button>
          )}


          {step < 4 ? (

            <button
              type="button"
              className="button"
              onClick={next}
            >
              Continue →
            </button>

          ) : (

            <button
              className="button"
              disabled={busy}
            >
              {busy
                ? "Creating…"
                : "Create account"}
            </button>

          )}

        </div>

      </form>

    </AuthLayout>
  );
}


/* =========================
   DASHBOARD
========================= */

function Dashboard({
  user,
  token,
  onLogout,
}) {
  const [editing, setEditing] = useState(false);
  const [summary, setSummary] = useState(null);
  const [summaryError, setSummaryError] = useState("");
  const [selectedWorkout, setSelectedWorkout] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoError, setVideoError] = useState("");

  useEffect(() => {
    let isCurrent = true;

    api.analyticsSummary(token)
      .then((data) => {
        if (isCurrent) {
          setSummary(data);
          setSelectedWorkout(data.recent_workouts[0] || null);
        }
      })
      .catch((error) => {
        if (isCurrent) setSummaryError(error.message);
      });

    return () => {
      isCurrent = false;
    };
  }, [token]);

  const deleteRecentWorkout = async (workoutId) => {
    if (!window.confirm("Delete this saved workout? This cannot be undone.")) return;

    try {
      await api.deleteWorkout(token, workoutId);
      const refreshedSummary = await api.analyticsSummary(token);
      setSummary(refreshedSummary);
      setSelectedWorkout(refreshedSummary.recent_workouts[0] || null);
    } catch (error) {
      setSummaryError(error.message || "Could not delete this workout.");
    }
  };

  const viewWorkoutVideo = async (workoutId) => {
    try {
      setVideoError("");
      const url = await api.workoutVideo(token, workoutId);
      if (videoUrl) URL.revokeObjectURL(videoUrl);
      setVideoUrl(url);
    } catch (error) {
      setVideoError(error.message || "Could not load the saved video.");
    }
  };

  const closeWorkoutVideo = () => {
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    setVideoUrl(null);
  };

  const selectedWorkoutCount = selectedWorkout && summary
    ? summary.exercise_counts[selectedWorkout.exercise] || 0
    : summary?.total_workouts;


  return (
    <main className="app-shell">

      {/* =========================
          SIDEBAR
      ========================= */}

      <aside>

        <Brand />


        <div className="side-label">
          OVERVIEW
        </div>


        <Link
          className="nav-active"
          to="/dashboard"
        >
          ⌂ Dashboard
        </Link>


        <Link to="/workout">
          ◌ AI Workout
        </Link>


        <Link to="/video-analysis">
          ◉ Video Analysis
        </Link>

       {/*
        <a className="nav-disabled">
          ↗ Progress
        </a>
        */}


        {/* =========================
            LOGOUT
        ========================= */}

        <div className="side-bottom">

          <button
            type="button"
            className="logout-btn"
            onClick={onLogout}
          >
            <span>↪</span>
            <span>Log out</span>
          </button>

        </div>

      </aside>


      {/* =========================
          DASHBOARD CONTENT
      ========================= */}

      <section className="dashboard">

        <div className="dashboard-top">

          <div>

            <p className="eyebrow">
              YOUR SPACE
            </p>

            <h1>
              Hi, {user.full_name.split(" ")[0]}.
            </h1>

            <p className="muted">
              Start small. Stay consistent.
              Your data will grow with you.
            </p>

          </div>


          <button
            className="avatar"
            onClick={() => setEditing(!editing)}
            title="Edit profile"
          >
            {user.full_name.charAt(0)}
          </button>

        </div>


        {editing ? (

          <ProfileEditor user={user} />

        ) : (

          <>

            {/* METRICS */}

            <div className="metric-grid">

              <Metric
                label={selectedWorkout ? `${selectedWorkout.exercise.toUpperCase()} WORKOUTS` : "WORKOUTS"}
                value={summary ? selectedWorkoutCount : "…"}
                caption={selectedWorkout ? `Times ${selectedWorkout.exercise} was saved` : "Saved sessions"}
              />


              <Metric
                label="TOTAL REPS"
                value={summary ? summary.total_reps : "…"}
                caption="Across saved workouts"
              />


              <Metric
                label="FORM SCORE"
                value={summary?.average_technique_score != null ? `${Math.round(summary.average_technique_score)}%` : "—"}
                caption={summary?.best_technique_score != null ? `Best ${Math.round(summary.best_technique_score)}%` : "Available after analysis"}
              />

            </div>


            {summaryError && <p className="error">Could not load your analytics: {summaryError}</p>}

            {summary && summary.total_workouts > 0 ? (
              <section className="history-card">
                <div className="history-heading">
                  <div>
                    <p className="eyebrow">RECENT ACTIVITY</p>
                    <h2>Your latest workouts</h2>
                  </div>
                  <Link className="text-link" to="/workout">Train again →</Link>
                </div>
                <div className="history-list">
                  {summary.recent_workouts.map((workout) => (
                    <article key={workout.id} className={`history-row ${selectedWorkout?.id === workout.id ? "history-row-selected" : ""}`}>
                      <div><button className="history-select" onClick={() => setSelectedWorkout(workout)}>{workout.exercise}</button><small>{new Date(workout.created_at).toLocaleDateString()}</small></div>
                      <div><strong>{workout.total_reps}</strong><small>reps</small></div>
                      <div><strong>{workout.technique_score == null ? "—" : `${Math.round(workout.technique_score)}%`}</strong><small>form score</small></div>
                      {workout.has_analyzed_video && <button className="history-video" onClick={() => viewWorkoutVideo(workout.id)}>View video</button>}
                      <button className="history-delete" onClick={() => deleteRecentWorkout(workout.id)} aria-label={`Delete ${workout.exercise} workout`}>Delete</button>
                    </article>
                  ))}
                </div>

                {selectedWorkout && (
                  <section className="selected-workout-card">
                    <div>
                      <p className="eyebrow">SELECTED WORKOUT</p>
                      <h3>{selectedWorkout.exercise}</h3>
                      <p className="muted">Saved {new Date(selectedWorkout.created_at).toLocaleString()}</p>
                    </div>
                    <div className="selected-workout-stats">
                      <span><strong>{selectedWorkout.total_reps}</strong> total reps</span>
                      <span><strong>{selectedWorkout.correct_reps}</strong> correct</span>
                      <span><strong>{selectedWorkout.incorrect_reps}</strong> incorrect</span>
                      <span><strong>{selectedWorkout.technique_score == null ? "—" : `${Math.round(selectedWorkout.technique_score)}%`}</strong> technique</span>
                    </div>
                  </section>
                )}
              </section>
            ) : (
              <section className="empty-card">

              <div className="orb">
                ✦
              </div>

              <p className="eyebrow">
                YOUR FIRST SESSION
              </p>

              <h2>
                Let’s build your baseline.
              </h2>

              <p>
                AI Coach and workout tracking are
                being prepared for the next FitMotion
                release.
              </p>


              <div className="hero-actions">

                <Link
                  className="button"
                  to="/workout"
                >
                  Start Workout →
                </Link>


                <Link
                  className="button ghost"
                  to="/video-analysis"
                >
                  Analyze Video →
                </Link>

              </div>

            </section>
            )}

            {videoError && <p className="error">{videoError}</p>}

            {videoUrl && (
              <div className="video-modal" role="dialog" aria-modal="true" aria-label="Saved workout video">
                <div className="video-modal-content">
                  <button className="video-modal-close" onClick={closeWorkoutVideo}>Close ×</button>
                  <video src={videoUrl} controls autoPlay className="saved-workout-video" />
                </div>
              </div>
            )}

          </>

        )}

      </section>

    </main>
  );
}


/* =========================
   METRIC
========================= */

function Metric({
  label,
  value,
  caption,
}) {
  return (
    <article className="metric">

      <p>
        {label}
      </p>

      <strong>
        {value}
      </strong>

      <small>
        {caption}
      </small>

    </article>
  );
}


/* =========================
   PROFILE EDITOR
========================= */

function ProfileEditor({ user }) {
  return (
    <section className="profile-card">

      <h2>
        Your profile
      </h2>


      <dl>

        <dt>
          Email
        </dt>

        <dd>
          {user.email}
        </dd>


        <dt>
          Activity
        </dt>

        <dd>
          {user.sport || "Not set"}
        </dd>


        <dt>
          Level
        </dt>

        <dd>
          {user.fitness_level || "Not set"}
        </dd>


        <dt>
          Goal
        </dt>

        <dd>
          {(user.fitness_goal || "Not set")
            .replaceAll("_", " ")}
        </dd>

      </dl>


      <p className="muted">
        Profile editing is available from the API now;
        the full dashboard editor is part of the next UI refinement.
      </p>

    </section>
  );
}


/* =========================
   APP
========================= */

function App() {

  const [session, setSession] = useState(() => {

    try {

      return JSON.parse(
        localStorage.getItem("fitmotion_session")
      );

    } catch {

      return null;

    }

  });


  /* =========================
     LOGIN / SIGNUP
  ========================= */

  const onAuth = (result) => {

    const value = {
      token: result.access_token,
      user: result.user,
    };


    localStorage.setItem(
      "fitmotion_session",
      JSON.stringify(value)
    );


    setSession(value);
  };


  /* =========================
     LOGOUT
  ========================= */

  const logout = () => {

    localStorage.removeItem(
      "fitmotion_session"
    );

    setSession(null);
  };


  return (
    <>
      <CustomCursor />


      <Routes>

        {/* LANDING */}
        <Route
          path="/"
          element={<Landing />}
        />

        {/* LOGIN */}
        <Route
          path="/login"
          element={
            session ? (
              <Navigate to="/dashboard" />
            ) : (
              <Login onAuth={onAuth} />
            )
          }
        />

        {/* SIGNUP */}
        <Route
          path="/signup"
          element={
            session ? (
              <Navigate to="/dashboard" />
            ) : (
              <Signup onAuth={onAuth} />
            )
          }
        />

        {/* DASHBOARD */}
        <Route
          path="/dashboard"
          element={
            session ? (
              <Dashboard
                user={session.user}
                token={session.token}
                onLogout={logout}
              />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        {/* WORKOUT */}
        <Route
          path="/workout"
          element={
            session ? (
              <Workout user={session.user} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        {/* VIDEO ANALYSIS */}
        <Route
          path="/video-analysis"
          element={
            session ? (
              <VideoAnalysis token={session.token} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        <Route
          path="*"
          element={<Navigate to="/" />}
        />

      </Routes>
    </>
  );
}


export default App;
