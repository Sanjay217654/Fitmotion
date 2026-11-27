import { useEffect, useRef } from "react";

function CustomCursor() {
  const cursorRef = useRef(null);

  useEffect(() => {
    const cursor = cursorRef.current;

    if (!cursor) return;

    const moveCursor = (event) => {
      cursor.style.left = `${event.clientX}px`;
      cursor.style.top = `${event.clientY}px`;
    };

    const addHover = (event) => {
      const target = event.target.closest(
        "a, button, select, input, textarea, .clickable"
      );

      if (target) {
        cursor.classList.add("cursor-hover");
      } else {
        cursor.classList.remove("cursor-hover");
      }
    };

    const mouseDown = () => {
      cursor.classList.add("cursor-click");
    };

    const mouseUp = () => {
      cursor.classList.remove("cursor-click");
    };

    const mouseLeave = () => {
      cursor.style.opacity = "0";
    };

    const mouseEnter = () => {
      cursor.style.opacity = "1";
    };

    window.addEventListener("mousemove", moveCursor);
    window.addEventListener("mouseover", addHover);
    window.addEventListener("mousedown", mouseDown);
    window.addEventListener("mouseup", mouseUp);
    window.addEventListener("mouseleave", mouseLeave);
    window.addEventListener("mouseenter", mouseEnter);

    return () => {
      window.removeEventListener("mousemove", moveCursor);
      window.removeEventListener("mouseover", addHover);
      window.removeEventListener("mousedown", mouseDown);
      window.removeEventListener("mouseup", mouseUp);
      window.removeEventListener("mouseleave", mouseLeave);
      window.removeEventListener("mouseenter", mouseEnter);
    };
  }, []);

  return (
    <div
      ref={cursorRef}
      className="custom-cursor"
      aria-hidden="true"
    />
  );
}

export default CustomCursor;