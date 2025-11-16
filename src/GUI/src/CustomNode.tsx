import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeResponse } from './types';
import * as design from './nodeDesign';

interface CustomNodeData {
  node: NodeResponse;
  onBypassToggle?: (sessionId: string) => void;
}

const MIN_HANDLE_SPACING = 12;
const VERTICAL_PADDING = 20;

const STATE_COLORS: Record<string, string> = {
  unchanged: design.COLOR_COOKING_UNCHANGED,
  uncooked: design.COLOR_COOKING_UNCOOKED,
  cooking: design.COLOR_COOKING_COOKING,
};

function calculateMinHeight(inputCount: number, outputCount: number): number {
  const handleCount = Math.max(inputCount, outputCount);
  return handleCount > 0 ? (handleCount + 1) * MIN_HANDLE_SPACING + VERTICAL_PADDING : 0;
}

export const CustomNode: React.FC<{ data: CustomNodeData; selected?: boolean }> = ({ data, selected }) => {
  const { node, onBypassToggle } = data;

  // Extract bypass and display states from parameters
  const isBypassed = node.parameters?.bypass?.value === true;
  const isOnDisplay = node.parameters?.display?.value === true;

  const minHeight = calculateMinHeight(node.inputs.length, node.outputs.length);
  const stateColor = STATE_COLORS[node.state] ?? design.COLOR_COOKING_UNCOOKED;
  const borderColor = selected ? design.COLOR_BORDER_SELECTED :
                      isBypassed ? design.COLOR_BORDER_BYPASSED :
                      design.COLOR_BORDER_ACTIVE;
  const backgroundColor = isBypassed ? design.COLOR_BG_BYPASSED : design.COLOR_BG_ACTIVE;
  const textColor = isBypassed ? design.COLOR_TEXT_BYPASSED : design.COLOR_TEXT_ACTIVE;

  const hasError = node.errors.length > 0;
  const hasWarning = node.warnings.length > 0;

  const handleBypassClick = () => {
    if (onBypassToggle) {
      onBypassToggle(node.session_id);
    }
  };

  return (
    <div
      style={{
        position: 'relative',
        padding: `${design.NODE_PADDING_VERTICAL}px ${design.NODE_PADDING_HORIZONTAL}px`,
        border: `${design.NODE_BORDER_WIDTH}px solid ${borderColor}`,
        borderRadius: `${design.NODE_BORDER_RADIUS}px`,
        background: backgroundColor,
        minWidth: `${design.NODE_MIN_WIDTH}px`,
        minHeight: minHeight || undefined,
        boxShadow: selected ? '0 4px 8px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.1)',
      }}
    >
      {/* Cooking State Circle (Top-Left) */}
      <div
        style={{
          position: 'absolute',
          left: `${design.COOKING_STATE_LEFT}px`,
          top: `${design.COOKING_STATE_TOP}px`,
          width: `${design.COOKING_STATE_DIAMETER}px`,
          height: `${design.COOKING_STATE_DIAMETER}px`,
          borderRadius: '50%',
          background: stateColor,
          opacity: isBypassed ? design.OPACITY_BYPASSED : 1,
        }}
      />

      {/* Error/Warning Indicators (Bottom-Left) */}
      {(hasError || hasWarning) && (
        <div
          style={{
            position: 'absolute',
            left: `${design.ERROR_WARNING_LEFT}px`,
            bottom: `${design.ERROR_WARNING_BOTTOM}px`,
            display: 'flex',
            gap: `${design.ERROR_WARNING_DUAL_GAP}px`,
            opacity: isBypassed ? design.OPACITY_BYPASSED : 1,
          }}
        >
          {hasError && hasWarning ? (
            <>
              {/* Dual circles - half width each */}
              <div
                style={{
                  width: `${design.ERROR_WARNING_DUAL_WIDTH}px`,
                  height: `${design.ERROR_WARNING_DIAMETER}px`,
                  borderRadius: '50%',
                  background: design.COLOR_ERROR,
                }}
                title="Has errors"
              />
              <div
                style={{
                  width: `${design.ERROR_WARNING_DUAL_WIDTH}px`,
                  height: `${design.ERROR_WARNING_DIAMETER}px`,
                  borderRadius: '50%',
                  background: design.COLOR_WARNING,
                }}
                title="Has warnings"
              />
            </>
          ) : hasError ? (
            <div
              style={{
                width: `${design.ERROR_WARNING_DIAMETER}px`,
                height: `${design.ERROR_WARNING_DIAMETER}px`,
                borderRadius: '50%',
                background: design.COLOR_ERROR,
              }}
              title="Has errors"
            />
          ) : (
            <div
              style={{
                width: `${design.ERROR_WARNING_DIAMETER}px`,
                height: `${design.ERROR_WARNING_DIAMETER}px`,
                borderRadius: '50%',
                background: design.COLOR_WARNING,
              }}
              title="Has warnings"
            />
          )}
        </div>
      )}

      {/* Display State Square (Top-Right) */}
      <div
        style={{
          position: 'absolute',
          right: `${design.DISPLAY_STATE_RIGHT}px`,
          top: `${design.DISPLAY_STATE_TOP}px`,
          width: `${design.DISPLAY_STATE_SIZE}px`,
          height: `${design.DISPLAY_STATE_SIZE}px`,
          border: isOnDisplay
            ? `${design.DISPLAY_STATE_BORDER_WIDTH_ON}px solid ${design.COLOR_DISPLAY_BORDER_ON}`
            : `${design.DISPLAY_STATE_BORDER_WIDTH_OFF}px solid ${design.COLOR_DISPLAY_BORDER_OFF}`,
          background: isOnDisplay ? design.COLOR_DISPLAY_FILL_ON : 'transparent',
          opacity: isBypassed ? design.OPACITY_BYPASSED : 1,
        }}
        title={isOnDisplay ? 'On display' : 'Not on display'}
      />

      {/* Bypass/Template Button (Bottom-Right) */}
      <div
        onClick={handleBypassClick}
        style={{
          position: 'absolute',
          right: `${design.BYPASS_BUTTON_RIGHT}px`,
          bottom: `${design.BYPASS_BUTTON_BOTTOM}px`,
          width: `${design.BYPASS_BUTTON_SIZE}px`,
          height: `${design.BYPASS_BUTTON_SIZE}px`,
          background: design.COLOR_BYPASS_DEFAULT,
          borderRadius: `${design.BYPASS_BUTTON_BORDER_RADIUS}px`,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 'bold',
          color: 'white',
          opacity: isBypassed ? design.OPACITY_BYPASSED : 1,
          transition: 'background 0.2s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = design.COLOR_BYPASS_HOVER;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = design.COLOR_BYPASS_DEFAULT;
        }}
        title={isBypassed ? 'Bypassed (Template)' : 'Click to bypass'}
      >
        {isBypassed && '×'}
      </div>

      {/* Text Content Area */}
      <div
        style={{
          position: 'relative',
          minHeight: `${design.TEXT_LINE_HEIGHT * 2}px`,
          paddingTop: `${design.TEXT_AREA_TOP}px`,
          paddingBottom: `${design.TEXT_AREA_BOTTOM}px`,
          paddingLeft: `${design.TEXT_AREA_LEFT - design.NODE_PADDING_HORIZONTAL}px`,
          paddingRight: `${design.TEXT_AREA_RIGHT - design.NODE_PADDING_HORIZONTAL}px`,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          opacity: isBypassed ? design.OPACITY_BYPASSED : 1,
        }}
      >
        {/* Node Type (small text above glyph) */}
        <div
          style={{
            fontSize: `${design.TEXT_TYPE_FONT_SIZE}px`,
            color: textColor,
            marginBottom: '2px',
          }}
        >
          {node.type}
        </div>

        {/* Glyph */}
        <div
          style={{
            fontSize: `${design.TEXT_GLYPH_SIZE}px`,
            lineHeight: `${design.TEXT_LINE_HEIGHT}px`,
            color: textColor,
            marginBottom: '2px',
          }}
        >
          {node.glyph || '?'}
        </div>

        {/* Node Name */}
        <div
          style={{
            fontSize: `${design.TEXT_FONT_SIZE}px`,
            fontWeight: 'bold',
            color: textColor,
            lineHeight: `${design.TEXT_LINE_HEIGHT}px`,
          }}
        >
          {node.name}
        </div>
      </div>

      {/* Input Handles */}
      {node.inputs.map((input, idx) => (
        <Handle
          key={`input-${input.index}`}
          type="target"
          position={Position.Left}
          id={`input-${idx}`}
          title={`${input.name} (${input.data_type})`}
          style={{
            top: `${((idx + 1) / (node.inputs.length + 1)) * 100}%`,
            left: `-${design.HANDLE_OFFSET}px`,
            width: `${design.HANDLE_DIAMETER}px`,
            height: `${design.HANDLE_DIAMETER}px`,
            border: `${design.HANDLE_BORDER_WIDTH}px solid ${
              isBypassed
                ? design.COLOR_HANDLE_BYPASSED_BORDER
                : design.COLOR_HANDLE_INPUT_BORDER
            }`,
            background: isBypassed
              ? design.COLOR_HANDLE_BYPASSED_FILL
              : design.COLOR_HANDLE_INPUT_FILL,
            opacity: isBypassed ? design.OPACITY_BYPASSED : 1,
          }}
        />
      ))}

      {/* Output Handles */}
      {node.outputs.map((output, idx) => (
        <Handle
          key={`output-${output.index}`}
          type="source"
          position={Position.Right}
          id={`output-${idx}`}
          title={`${output.name} (${output.data_type})`}
          style={{
            top: `${((idx + 1) / (node.outputs.length + 1)) * 100}%`,
            right: `-${design.HANDLE_OFFSET}px`,
            width: `${design.HANDLE_DIAMETER}px`,
            height: `${design.HANDLE_DIAMETER}px`,
            border: `${design.HANDLE_BORDER_WIDTH}px solid ${
              isBypassed
                ? design.COLOR_HANDLE_BYPASSED_BORDER
                : design.COLOR_HANDLE_OUTPUT_BORDER
            }`,
            background: isBypassed
              ? design.COLOR_HANDLE_BYPASSED_FILL
              : design.COLOR_HANDLE_OUTPUT_FILL,
            opacity: isBypassed ? design.OPACITY_BYPASSED : 1,
          }}
        />
      ))}
    </div>
  );
};
