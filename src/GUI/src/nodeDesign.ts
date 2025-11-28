type ThemeMode = 'light' | 'dark';

const GROUP_COLORS = {
  orange: {
    0: '#602c10',
    100: '#b7541f',
    200: '#e38959',
    300: '#f2c7b1',
    400: '#f8e0d3',
  },
  grey: {
    0: '#17191c',
    100: '#3c4048',
    200: '#6b7280',
    300: '#a0a6b0',
    400: '#d8dadf',
  },
  green: {
    0: '#10602c',
    100: '#1fb754',
    200: '#59e389',
    300: '#b1f2c7',
    400: '#d3f8e0',
  },
  purple: {
    0: '#2c1060',
    100: '#541fb7',
    200: '#8959e3',
    300: '#c7b1f2',
    400: '#e0d3f8',
  },
};

export const getGroupColors = (group: string, mode: ThemeMode) => {
  const palette = GROUP_COLORS[group as keyof typeof GROUP_COLORS];
  if (!palette) {
    return {
      background: mode === 'light' ? '#FFFFFF' : '#374151',
      glyphBackground: mode === 'light' ? '#F3F4F6' : '#4B5563',
    };
  }

  return {
    background: mode === 'light' ? palette[400] : palette[100],
    glyphBackground: mode === 'light' ? palette[300] : palette[0],
  };
};

export const SCALES = {
  large: {
    UNIT: 4,
    FONT_MULT: 1.0,
    ICON_MULT: 1.0,
    HANDLE_MULT: 1.0,
    GLYPH_BUFFER_MULT: 1.5,
    GLYPH_PADDING_MULT: 1.5,
    NODE_PADDING_MULT: 1.0,
    TEXT_PADDING_MULT: 1.0,
    SHOW_TYPE: true,
    SHOW_NAME: true,
    SHOW_INDICATORS: true,
    SHOW_ERROR_WARNING: true,
    SHOW_BYPASS: true,
  },
  medium: {
    UNIT: 3,
    FONT_MULT: 0.9,
    ICON_MULT: 0.85,
    HANDLE_MULT: 0.9,
    GLYPH_BUFFER_MULT: 0.75,
    GLYPH_PADDING_MULT: 1.5,
    NODE_PADDING_MULT: 0.5,
    TEXT_PADDING_MULT: 0.5,
    SHOW_TYPE: false,
    SHOW_NAME: true,
    SHOW_INDICATORS: true,
    SHOW_ERROR_WARNING: false,
    SHOW_BYPASS: true,
  },
  small: {
    UNIT: 2,
    FONT_MULT: 0.8,
    ICON_MULT: 0.75,
    HANDLE_MULT: 0.8,
    GLYPH_BUFFER_MULT: 0.75,
    GLYPH_PADDING_MULT: 2.25,
    NODE_PADDING_MULT: 0.5,
    TEXT_PADDING_MULT: 0.5,
    SHOW_TYPE: false,
    SHOW_NAME: false,
    SHOW_INDICATORS: false,
    SHOW_ERROR_WARNING: false,
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
      paddingY: 2 * S.UNIT * S.NODE_PADDING_MULT,
      borderRadius: 2 * S.UNIT,
      borderWidth: 2,
    },

    text: {
      glyphSize: 14 * S.FONT_MULT,
      typeSize: 10 * S.FONT_MULT,
      nameSize: 14 * S.FONT_MULT,
      gapHeader: 2 * S.UNIT,
      gapLines: 1.5 * S.UNIT,
      paddingTop: 2 * S.UNIT * S.TEXT_PADDING_MULT,
      paddingBottom: 2 * S.UNIT * S.TEXT_PADDING_MULT,
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

    glyph: {
      padding: S.GLYPH_PADDING_MULT * S.UNIT,
      bufferFromEdge: S.GLYPH_BUFFER_MULT * S.UNIT,
    },

    template: {
      width: 24 * S.ICON_MULT,
      paddingY: 1 * S.UNIT,
    },

    visibility: {
      showType: S.SHOW_TYPE,
      showName: S.SHOW_NAME,
      showIndicators: S.SHOW_INDICATORS,
      showErrorWarning: S.SHOW_ERROR_WARNING,
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
  template: {
    off: mode === 'light' ? '#9CA3AF' : '#6B7280',
    on: mode === 'light' ? '#4B5563' : '#374151',
  },
  glyph: {
    background: {
      active: mode === 'light' ? '#F3F4F6' : '#4B5563',
      bypassed: mode === 'light' ? '#4B5563' : '#111827',
    },
  },
  text: {
    active: mode === 'light' ? '#1F2937' : '#F9FAFB',
    bypassed: mode === 'light' ? '#FFFFFF' : '#F9FAFB',
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
