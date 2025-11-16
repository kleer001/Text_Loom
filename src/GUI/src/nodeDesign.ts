// Node Design Constants - Pixel-Perfect Specification

// Node Container
export const NODE_MIN_WIDTH = 150;
export const NODE_PADDING_VERTICAL = 10;
export const NODE_PADDING_HORIZONTAL = 15;
export const NODE_BORDER_WIDTH = 2;
export const NODE_BORDER_RADIUS = 8;

// Visual Indicators - Common
export const INDICATOR_EDGE_OFFSET = 8;

// Cooking State Circle (Top-Left)
export const COOKING_STATE_DIAMETER = 12;
export const COOKING_STATE_LEFT = INDICATOR_EDGE_OFFSET;
export const COOKING_STATE_TOP = INDICATOR_EDGE_OFFSET;

// Error/Warning Indicators (Bottom-Left)
export const ERROR_WARNING_DIAMETER = 12;
export const ERROR_WARNING_LEFT = INDICATOR_EDGE_OFFSET;
export const ERROR_WARNING_BOTTOM = INDICATOR_EDGE_OFFSET;
export const ERROR_WARNING_DUAL_WIDTH = 6;
export const ERROR_WARNING_DUAL_GAP = 2;

// Display State Square (Top-Right)
export const DISPLAY_STATE_SIZE = 14;
export const DISPLAY_STATE_RIGHT = INDICATOR_EDGE_OFFSET;
export const DISPLAY_STATE_TOP = INDICATOR_EDGE_OFFSET;
export const DISPLAY_STATE_BORDER_WIDTH_OFF = 1.5;
export const DISPLAY_STATE_BORDER_WIDTH_ON = 3;

// Bypass/Template Control Square (Bottom-Right)
export const BYPASS_BUTTON_SIZE = 16;
export const BYPASS_BUTTON_RIGHT = INDICATOR_EDGE_OFFSET;
export const BYPASS_BUTTON_BOTTOM = INDICATOR_EDGE_OFFSET;
export const BYPASS_BUTTON_BORDER_RADIUS = 2;

// Text Content Area
export const TEXT_SPACING_FROM_INDICATOR = 8;
export const TEXT_AREA_TOP = INDICATOR_EDGE_OFFSET;
export const TEXT_AREA_BOTTOM = INDICATOR_EDGE_OFFSET;
export const TEXT_AREA_LEFT = ERROR_WARNING_LEFT + ERROR_WARNING_DIAMETER + TEXT_SPACING_FROM_INDICATOR;
export const TEXT_AREA_RIGHT = BYPASS_BUTTON_RIGHT + BYPASS_BUTTON_SIZE + TEXT_SPACING_FROM_INDICATOR;

// Text Styling
export const TEXT_LINE_HEIGHT = 20;
export const TEXT_FONT_SIZE = 14;
export const TEXT_ROW_SPACING = 4;
export const TEXT_TYPE_FONT_SIZE = 9;
export const TEXT_GLYPH_SIZE = 14;
export const TEXT_GLYPH_MARGIN_RIGHT = 6;
export const TEXT_NAME_TOP_OFFSET = 8;

// Connection Points (Handles)
export const HANDLE_DIAMETER = 10;
export const HANDLE_BORDER_WIDTH = 2;
export const HANDLE_OFFSET = 6;

// Colors - Cooking State
export const COLOR_COOKING_UNCOOKED = '#ff9800';    // Orange
export const COLOR_COOKING_UNCHANGED = '#4caf50';   // Green (cooked)
export const COLOR_COOKING_COOKING = '#2196f3';     // Blue

// Colors - Error/Warning
export const COLOR_ERROR = '#A855F7';               // Purple
export const COLOR_WARNING = '#FCD34D';             // Yellow

// Colors - Display State
export const COLOR_DISPLAY_BORDER_OFF = '#93C5FD';  // Light blue
export const COLOR_DISPLAY_BORDER_ON = '#E879F9';   // Magenta
export const COLOR_DISPLAY_FILL_ON = '#3B82F6';     // Blue

// Colors - Bypass Button
export const COLOR_BYPASS_DEFAULT = '#6B7280';      // Grey
export const COLOR_BYPASS_HOVER = '#9CA3AF';        // Lighter grey

// Colors - Text
export const COLOR_TEXT_ACTIVE = '#1F2937';         // Dark grey
export const COLOR_TEXT_BYPASSED = '#4B5563';       // Medium grey

// Colors - Node Background & Border
export const COLOR_BG_ACTIVE = 'white';
export const COLOR_BG_BYPASSED = '#374151';         // Dark grey
export const COLOR_BORDER_ACTIVE = '#ccc';
export const COLOR_BORDER_BYPASSED = '#4B5563';     // Medium grey
export const COLOR_BORDER_SELECTED = '#1976d2';

// Colors - Handles
export const COLOR_HANDLE_INPUT_BORDER = '#E5E7EB';
export const COLOR_HANDLE_INPUT_FILL = '#FFFFFF';
export const COLOR_HANDLE_OUTPUT_BORDER = '#10B981';
export const COLOR_HANDLE_OUTPUT_FILL = '#D1FAE5';
export const COLOR_HANDLE_BYPASSED_BORDER = '#6B7280';
export const COLOR_HANDLE_BYPASSED_FILL = '#9CA3AF';

// Opacity
export const OPACITY_BYPASSED = 0.6;               // 60% (100% - 40% reduction)
