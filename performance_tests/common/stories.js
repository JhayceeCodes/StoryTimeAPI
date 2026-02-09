// Pick story ID from available stories
const storyIds = [1, 2, 3, 4, 5, 7];

export function pickStoryId() {
  return storyIds[Math.floor(Math.random() * storyIds.length)];
}
