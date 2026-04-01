"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type CourseOverview = {
  id: string;
  title: string;
  description: string;
  level: number;
  module_count: number;
  lesson_count: number;
};

type LessonOverview = {
  id: string;
  title: string;
};

type ModuleOverview = {
  id: string;
  lessons: LessonOverview[];
};

type CourseDetail = {
  id: string;
  modules: ModuleOverview[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function LearnPage() {
  const [courses, setCourses] = useState<CourseOverview[]>([]);
  const [lessonMap, setLessonMap] = useState<Record<string, LessonOverview[]>>({});
  const [status, setStatus] = useState("Loading courses...");

  useEffect(() => {
    const loadCourses = async () => {
      try {
        const response = await fetch(`${API_BASE}/courses`);
        if (!response.ok) {
          setStatus("Failed to load courses");
          return;
        }
        const data = (await response.json()) as CourseOverview[];
        setCourses(data);
        const details = await Promise.all(
          data.map(async (course) => {
            const detailResponse = await fetch(`${API_BASE}/courses/${course.id}`);
            if (!detailResponse.ok) {
              return { id: course.id, modules: [] } as CourseDetail;
            }
            return (await detailResponse.json()) as CourseDetail;
          })
        );
        const nextMap: Record<string, LessonOverview[]> = {};
        for (const course of details) {
          nextMap[course.id] = course.modules.flatMap((module) => module.lessons);
        }
        setLessonMap(nextMap);
        setStatus(data.length ? "Courses loaded" : "No courses yet");
      } catch {
        setStatus("Backend unavailable. Start API server to view learning content.");
      }
    };
    void loadCourses();
  }, []);

  return (
    <section>
      <h1>Learning Path</h1>
      <p>Structured journey from beginner to enterprise-scale process architect.</p>
      <p style={{ color: "#475569" }}>{status}</p>
      <div style={{ display: "grid", gap: 12 }}>
        {courses.map((course) => (
          <article
            key={course.id}
            style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}
          >
            <h3 style={{ margin: "0 0 6px 0" }}>
              Level {course.level}: {course.title}
            </h3>
            <p style={{ margin: "0 0 8px 0" }}>{course.description}</p>
            <small>
              {course.module_count} modules • {course.lesson_count} lessons
            </small>
            <div style={{ marginTop: 10, display: "grid", gap: 6 }}>
              {(lessonMap[course.id] ?? []).map((lesson) => (
                <Link key={lesson.id} href={`/quiz/${lesson.id}`}>
                  Quiz: {lesson.title}
                </Link>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
