const levels = [
  "Level 1: Foundations of Process Automation",
  "Level 2: Process Mapping and Business Thinking",
  "Level 3: Tools Used in Industry",
  "Level 4: AI + Process Automation",
  "Level 5: Building Real Automation Systems",
  "Level 6: Enterprise and Mastery"
];

export default function LearnPage() {
  return (
    <section>
      <h1>Learning Path</h1>
      <p>Structured journey from beginner to enterprise-scale process architect.</p>
      <ol>
        {levels.map((level) => (
          <li key={level} style={{ marginBottom: 8 }}>
            {level}
          </li>
        ))}
      </ol>
    </section>
  );
}
