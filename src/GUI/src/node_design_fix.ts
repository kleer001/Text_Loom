// Revised nodeDesign.ts with scale system
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
