type ThemeMode = 'light' | 'dark';

export const NODE_MIN_WIDTH = 150;
export const NODE_PADDING_VERTICAL = 10;
export const NODE_PADDING_HORIZONTAL = 15;
export const NODE_BORDER_WIDTH = 2;
export const NODE_BORDER_RADIUS = 8;

export const INDICATOR_EDGE_OFFSET = 8;

export const COOKING_STATE_DIAMETER = 12;
export const COOKING_STATE_LEFT = INDICATOR_EDGE_OFFSET;
export const COOKING_STATE_TOP = INDICATOR_EDGE_OFFSET;

export const ERROR_WARNING_DIAMETER = 12;
export const ERROR_WARNING_LEFT = INDICATOR_EDGE_OFFSET;
export const ERROR_WARNING_BOTTOM = INDICATOR_EDGE_OFFSET;
export const ERROR_WARNING_DUAL_WIDTH = 6;
export const ERROR_WARNING_DUAL_GAP = 2;

export const TEMPLATE_CIRCLE_DIAMETER = 12;
export const TEMPLATE_CIRCLE_RIGHT = INDICATOR_EDGE_OFFSET;
export const TEMPLATE_CIRCLE_FONT_SIZE = 14;

export const TEXT_SPACING_FROM_INDICATOR = 8;
export const TEXT_AREA_TOP = INDICATOR_EDGE_OFFSET;
export const TEXT_AREA_BOTTOM = INDICATOR_EDGE_OFFSET;
export const TEXT_AREA_LEFT = ERROR_WARNING_LEFT + ERROR_WARNING_DIAMETER + TEXT_SPACING_FROM_INDICATOR;
export const TEXT_AREA_RIGHT = TEMPLATE_CIRCLE_RIGHT + TEMPLATE_CIRCLE_DIAMETER + TEXT_SPACING_FROM_INDICATOR;

export const TEXT_LINE_HEIGHT = 20;
export const TEXT_FONT_SIZE = 14;
export const TEXT_TYPE_FONT_SIZE = 9;
export const TEXT_GLYPH_SIZE = 14;
export const TEXT_ELEMENT_MARGIN = 2;
export const TEXT_CONTENT_GAP = 6;
export const TEXT_HEADER_GAP = 8;

export const HANDLE_DIAMETER = 10;
export const HANDLE_BORDER_WIDTH = 2;
export const HANDLE_OFFSET = 6;

export const OPACITY_BYPASSED = 0.6;
export const OPACITY_ACTIVE = 1;

export const getColors = (mode: ThemeMode) => ({
  cooking: {
    uncooked: '#ff9800',
    unchanged: '#4caf50',
    cooking: '#2196f3',
    cooked: '#4caf50',
  },
  error: {
    fill: '#A855F7',
    outline: '#D4AAFB',
  },
  warning: {
    fill: '#FCD34D',
    outline: '#FEE9A6',
  },
  bypass: {
    default: mode === 'light' ? '#CED0D5' : '#4B5563',
    hover: mode === 'light' ? '#E5E7EB' : '#6B7280',
  },
  text: {
    active: mode === 'light' ? '#1F2937' : '#F9FAFB',
    bypassed: mode === 'light' ? '#4B5563' : '#9CA3AF',
  },
  background: {
    active: mode === 'light' ? '#FFFFFF' : '#374151',
    bypassed: mode === 'light' ? '#374151' : '#1F2937',
  },
  border: {
    active: mode === 'light' ? '#CCCCCC' : '#4B5563',
    bypassed: mode === 'light' ? '#4B5563' : '#374151',
    selected: mode === 'light' ? '#1976d2' : '#60a5fa',
  },
  handle: {
    input: {
      border: mode === 'light' ? '#E5E7EB' : '#4B5563',
      fill: mode === 'light' ? '#FFFFFF' : '#374151',
    },
    output: {
      border: mode === 'light' ? '#10B981' : '#34D399',
      fill: mode === 'light' ? '#D1FAE5' : '#064E3B',
    },
    bypassed: {
      border: mode === 'light' ? '#6B7280' : '#4B5563',
      fill: mode === 'light' ? '#9CA3AF' : '#374151',
    },
  },
  canvas: {
    background: mode === 'light' ? '#f5f5f5' : '#111827',
    grid: mode === 'light' ? '#d1d5db' : '#374151',
  },
});
