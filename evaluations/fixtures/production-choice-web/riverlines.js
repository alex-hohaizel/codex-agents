"use strict";

const element = (id) => document.getElementById(id);
const storyTitle = element("story-title");
const links = reports.map((entry) => {
  const listItem = document.createElement("li");
  const link = document.createElement("a");
  link.href = "#story";
  link.textContent = entry.reach;
  link.addEventListener("click", (event) => {
    event.preventDefault();
    renderStory(entry);
    storyTitle.focus();
  });
  listItem.append(link);
  element("chronology").append(listItem);
  return link;
});

function renderStory(entry) {
  storyTitle.textContent = entry.title;
  element("story-location").textContent = entry.reach;
  element("story-text").textContent = entry.body;
  element("story-source").textContent = `${entry.source} · ${entry.recorded} · ${entry.confidence}`;
  element("notes").open = false;
  links.forEach((link, index) => {
    if (reports[index] === entry) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  });
}

renderStory(reports[0]);
