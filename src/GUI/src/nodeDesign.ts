type ThemeMode = 'light' | 'dark';

export const SCALES = {
  large: {
    UNIT: 4,
    FONT_MULT: 1.0,
    ICON_MULT: 1.0,
    HANDLE_MULT: 1.0,
    SHOW_NAME: true,
    SHOW_INDICATORS: true,
    SHOW_BYPASS: true,
  },
  medium: {
    UNIT: 3,
    FONT_MULT: 0.9,
    ICON_MULT: 0.85,
    HANDLE_MULT: 0.9,
    SHOW_NAME: true,
    SHOW_INDICATORS: true,
    SHOW_BYPASS: true,
  },
  small: {
    UNIT: 2,
    FONT_MULT: 0.8,
    ICON_MULT: 0.75,
    HANDLE_MULT: 0.8,
    SHOW_NAME: false,
    SHOW_INDICATORS: false,
    SHOW_BYPASS: true,
  },
};

export const Layout = (scale: keyof typeof SCALES) => {
  const S = SCALES[scale];
  return {
    UNIT: S.UNIT,

    node: {
      minWidth: 150,
      paddingX: 3 * S.UNIT,
      paddingY: 2 * S.UNIT,
      borderRadius: 2 * S.UNIT,
      borderWidth: 2,
    },

    text: {
      glyphSize: 14 * S.FONT_MULT,
      typeSize: 10 * S.FONT_MULT,
      nameSize: 14 * S.FONT_MULT,
      gapHeader: 2 * S.UNIT,
      gapLines: 1.5 * S.UNIT,
      paddingTop: 2 * S.UNIT,
      paddingBottom: 2 * S.UNIT,
      paddingSide: 2 * S.UNIT,
    },

    indicators: {
      diameter: 12 * S.ICON_MULT,
      offset: 2 * S.UNIT,
      gap: 1 * S.UNIT,
    },

    bypass: {
      diameter: 12 * S.ICON_MULT,
      offsetRight: 2 * S.UNIT,
    },

    handle: {
      diameter: 12 * S.HANDLE_MULT,
      borderWidth: 2,
      offset: 1.5 * S.UNIT,
      minSpacing: 2 * S.UNIT,
    },

    visibility: {
      showName: S.SHOW_NAME,
      showIndicators: S.SHOW_INDICATORS,
      showBypass: S.SHOW_BYPASS,
    },
  };
};

export const OPACITY_BYPASSED = 0.6;
export const OPACITY_ACTIVE = 1;

export const EDGE_WIDTH_DEFAULT = 2;
export const EDGE_WIDTH_HOVER = 3;
export const EDGE_WIDTH_SELECTED = 4;

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
  edge: {
    default: mode === 'light' ? '#888888' : '#9CA3AF',
    hover: mode === 'light' ? '#5B8FC7' : '#7CB3E8',
    selected: mode === 'light' ? '#1976d2' : '#60a5fa',
  },
});
