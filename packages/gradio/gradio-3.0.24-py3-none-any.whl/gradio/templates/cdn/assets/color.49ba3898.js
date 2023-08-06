import { ab as ordered_colors } from './index.5626b7e1.js';

const get_next_color = (index) => {
  return ordered_colors[index % ordered_colors.length];
};

export { get_next_color as g };
