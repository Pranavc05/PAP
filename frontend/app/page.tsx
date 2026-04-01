const cards = [
  {
    title: "Learn",
    description: "Start with foundations, then grow into advanced automation system design."
  },
  {
    title: "Build",
    description: "Design and simulate workflows using visual nodes and business scenarios."
  },
  {
    title: "Get AI Feedback",
    description: "Use a Socratic AI coach that asks better questions before recommending tools."
  }
];

export default function HomePage() {
  return (
    <section>
      <h1>AI EdTech Platform for Process Automation</h1>
      <p>
        Build real-world process improvement skills through interactive lessons, workflow labs, and
        guided AI coaching.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginTop: 24 }}>
        {cards.map((card) => (
          <article
            key={card.title}
            style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}
          >
            <h3>{card.title}</h3>
            <p>{card.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
