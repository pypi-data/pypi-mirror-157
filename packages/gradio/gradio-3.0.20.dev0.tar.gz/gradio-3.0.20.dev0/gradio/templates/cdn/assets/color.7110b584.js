import { ab as ordered_colors } from './index.8fc23c0a.js';

const get_next_color = (index) => {
  return ordered_colors[index % ordered_colors.length];
};

export { get_next_color as g };
