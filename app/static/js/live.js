const liveForm = document.getElementById("live-form");
const liveStatus = document.getElementById("live-status");
const liveResults = document.getElementById("live-results");

async function runLiveSearch(e) {
  e.preventDefault();
  liveStatus.textContent = "Scraping and ranking internships...";
  liveResults.innerHTML = "";

  const skillsRaw = document.getElementById("live-skills").value || "";
  const interests = document.getElementById("live-interests").value || "";
  const locationPref = document.getElementById("live-location").value || "";
  const experience = document.getElementById("live-experience").value || "beginner";
  const pages = parseInt(document.getElementById("live-pages").value || "1", 10);
  const topK = parseInt(document.getElementById("live-top-k").value || "10", 10);

  const skills = skillsRaw
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);

  const payload = {
    skills,
    interests,
    location_preference: locationPref,
    experience_level: experience,
    top_k: topK,
    pages,
  };

  try {
    const res = await fetch("/live-search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    const results = data.results || [];

    if (!results.length) {
      liveStatus.textContent =
        "No relevant internships found for the given pages. Try increasing 'Pages per source' or changing requirements.";
      return;
    }

    liveStatus.textContent = `Found ${results.length} relevant internships (live scraped).`;

    results.forEach((item) => {
      const card = document.createElement("div");
      card.className = "result-card";

      const header = document.createElement("div");
      header.className = "result-header";

      const title = document.createElement("div");
      title.className = "result-title";
      title.textContent = item.title || "Untitled";

      const company = document.createElement("div");
      company.className = "result-company";
      company.textContent = item.company || "";

      header.appendChild(title);
      header.appendChild(company);

      const meta = document.createElement("div");
      meta.className = "result-meta";

      const loc = item.location ? `📍 ${item.location}` : "";
      const dur = item.duration ? `⏱ ${item.duration}` : "";
      const stipend = item.stipend ? `💰 ${item.stipend}` : "";

      [loc, dur, stipend].forEach((m) => {
        if (!m) return;
        const span = document.createElement("span");
        span.textContent = m;
        meta.appendChild(span);
      });

      const score = document.createElement("div");
      score.className = "result-score";
      if (typeof item.score === "number") {
        score.textContent = `Match score: ${item.score.toFixed(3)} (live)`;
      }

      const desc = document.createElement("div");
      desc.className = "result-description";
      desc.textContent =
        item.description?.slice(0, 260) ||
        "No description available. Click 'View internship' for more details.";

      const skillsDiv = document.createElement("div");
      skillsDiv.className = "result-skills";
      (item.skills || []).forEach((skill) => {
        const pill = document.createElement("span");
        pill.className = "skill-pill";
        pill.textContent = skill;
        skillsDiv.appendChild(pill);
      });

      const linkDiv = document.createElement("div");
      linkDiv.className = "result-link";
      if (item.link) {
        const a = document.createElement("a");
        a.href = item.link;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.textContent = "View internship ↗";
        linkDiv.appendChild(a);
      }

      card.appendChild(header);
      card.appendChild(meta);
      card.appendChild(score);
      card.appendChild(desc);
      card.appendChild(skillsDiv);
      card.appendChild(linkDiv);

      liveResults.appendChild(card);
    });
  } catch (err) {
    console.error(err);
    liveStatus.textContent =
      "Error during live search. Check browser console or backend logs.";
  }
}

liveForm.addEventListener("submit", runLiveSearch);
