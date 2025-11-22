const scrapeBtn = document.getElementById("scrape-btn");
const scrapeStatus = document.getElementById("scrape-status");
const pagesInput = document.getElementById("pages-input");

const recommendForm = document.getElementById("recommend-form");
const recommendStatus = document.getElementById("recommend-status");
const resultsContainer = document.getElementById("results");

async function runScrape() {
  const pages = parseInt(pagesInput.value || "1", 10);

  scrapeStatus.textContent = "Scraping in progress...";
  scrapeBtn.disabled = true;

  try {
    const res = await fetch(`/scrape?pages=${pages}`);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    scrapeStatus.textContent = `Scraping completed. New internships: ${data.new_internships}`;
  } catch (err) {
    console.error(err);
    scrapeStatus.textContent = "Error while scraping. Check console.";
  } finally {
    scrapeBtn.disabled = false;
  }
}

scrapeBtn.addEventListener("click", (e) => {
  e.preventDefault();
  runScrape();
});

async function runRecommend(e) {
  e.preventDefault();
  recommendStatus.textContent = "Fetching recommendations...";
  resultsContainer.innerHTML = "";

  const skillsRaw = document.getElementById("skills").value || "";
  const interests = document.getElementById("interests").value || "";
  const locationPref = document.getElementById("location").value || "";
  const experience = document.getElementById("experience").value || "beginner";
  const topK = parseInt(document.getElementById("top-k").value || "10", 10);

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
  };

  try {
    const res = await fetch("/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    const results = data.results || [];

    if (results.length === 0) {
      recommendStatus.textContent =
        "No recommendations yet. Try scraping first or adjust your profile.";
      return;
    }

    recommendStatus.textContent = `Got ${results.length} recommendations.`;

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
        score.textContent = `Match score: ${item.score.toFixed(3)}`;
      }

      const desc = document.createElement("div");
      desc.className = "result-description";
      desc.textContent =
        item.description?.slice(0, 260) ||
        "No description available. Click 'View' to see more.";

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

      resultsContainer.appendChild(card);
    });
  } catch (err) {
    console.error(err);
    recommendStatus.textContent = "Error fetching recommendations. Check console.";
  }
}

recommendForm.addEventListener("submit", runRecommend);
