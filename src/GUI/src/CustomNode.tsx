import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeResponse, InputInfo, OutputInfo } from './types';
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

const calculateMinHeight = (inputCount: number, outputCount: number): number => {
  const handleCount = Math.max(inputCount, outputCount);
  return handleCount > 0 ? (handleCount + 1) * MIN_HANDLE_SPACING + VERTICAL_PADDING : 0;
};

const getOpacity = (isBypassed: boolean): number =>
  isBypassed ? design.OPACITY_BYPASSED : design.OPACITY_ACTIVE;

interface IndicatorCircleProps {
  color: string;
  title: string;
  diameter?: number;
}

const IndicatorCircle: React.FC<IndicatorCircleProps> = ({
  color,
  title,
  diameter = design.ERROR_WARNING_DIAMETER
}) => (
  <div
    style={{
      width: `${diameter}px`,
      height: `${design.ERROR_WARNING_DIAMETER}px`,
      borderRadius: '50%',
      background: color,
    }}
    title={title}
  />
);

interface HandleProps {
  item: InputInfo | OutputInfo;
  idx: number;
  total: number;
  type: 'target' | 'source';
  position: Position;
  isBypassed: boolean;
  borderColor: string;
  fillColor: string;
}

const NodeHandle: React.FC<HandleProps> = ({
  item,
  idx,
  total,
  type,
  position,
  isBypassed,
  borderColor,
  fillColor,
}) => {
  const positionProp = position === Position.Left ? 'left' : 'right';

  return (
    <Handle
      key={`${type}-${item.index}`}
      type={type}
      position={position}
      id={`${type === 'target' ? 'input' : 'output'}-${idx}`}
      title={`${item.name} (${item.data_type})`}
      style={{
        top: `${((idx + 1) / (total + 1)) * 100}%`,
        [positionProp]: `-${design.HANDLE_OFFSET}px`,
        width: `${design.HANDLE_DIAMETER}px`,
        height: `${design.HANDLE_DIAMETER}px`,
        border: `${design.HANDLE_BORDER_WIDTH}px solid ${borderColor}`,
        background: fillColor,
        opacity: getOpacity(isBypassed),
      }}
    />
  );
};

export const CustomNode: React.FC<{ data: CustomNodeData; selected?: boolean }> = ({
  data,
  selected
}) => {
  const { node, onBypassToggle } = data;
  const isBypassed = node.parameters?.bypass?.value === true;
  const isOnDisplay = node.parameters?.display?.value === true;
  const hasError = node.errors.length > 0;
  const hasWarning = node.warnings.length > 0;

  const minHeight = calculateMinHeight(node.inputs.length, node.outputs.length);
  const stateColor = STATE_COLORS[node.state] ?? design.COLOR_COOKING_UNCOOKED;
  const borderColor = selected ? design.COLOR_BORDER_SELECTED :
                      isBypassed ? design.COLOR_BORDER_BYPASSED :
                      design.COLOR_BORDER_ACTIVE;
  const backgroundColor = isBypassed ? design.COLOR_BG_BYPASSED : design.COLOR_BG_ACTIVE;
  const textColor = isBypassed ? design.COLOR_TEXT_BYPASSED : design.COLOR_TEXT_ACTIVE;
  const opacity = getOpacity(isBypassed);

  const handleBorderColor = isBypassed ? design.COLOR_HANDLE_BYPASSED_BORDER :
    (type: 'input' | 'output') => type === 'input' ?
      design.COLOR_HANDLE_INPUT_BORDER : design.COLOR_HANDLE_OUTPUT_BORDER;

  const handleFillColor = isBypassed ? design.COLOR_HANDLE_BYPASSED_FILL :
    (type: 'input' | 'output') => type === 'input' ?
      design.COLOR_HANDLE_INPUT_FILL : design.COLOR_HANDLE_OUTPUT_FILL;

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
      <div
        style={{
          position: 'absolute',
          left: `${design.COOKING_STATE_LEFT}px`,
          top: `${design.COOKING_STATE_TOP}px`,
          width: `${design.COOKING_STATE_DIAMETER}px`,
          height: `${design.COOKING_STATE_DIAMETER}px`,
          borderRadius: '50%',
          background: stateColor,
          opacity,
        }}
      />

      {(hasError || hasWarning) && (
        <div
          style={{
            position: 'absolute',
            left: `${design.ERROR_WARNING_LEFT}px`,
            bottom: `${design.ERROR_WARNING_BOTTOM}px`,
            display: 'flex',
            gap: `${design.ERROR_WARNING_DUAL_GAP}px`,
            opacity,
          }}
        >
          {hasError && hasWarning ? (
            <>
              <IndicatorCircle
                color={design.COLOR_ERROR}
                title="Has errors"
                diameter={design.ERROR_WARNING_DUAL_WIDTH}
              />
              <IndicatorCircle
                color={design.COLOR_WARNING}
                title="Has warnings"
                diameter={design.ERROR_WARNING_DUAL_WIDTH}
              />
            </>
          ) : (
            <IndicatorCircle
              color={hasError ? design.COLOR_ERROR : design.COLOR_WARNING}
              title={hasError ? 'Has errors' : 'Has warnings'}
            />
          )}
        </div>
      )}

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
          opacity,
        }}
        title={isOnDisplay ? 'On display' : 'Not on display'}
      />

      <div
        onClick={() => onBypassToggle?.(node.session_id)}
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
          fontSize: `${design.BYPASS_BUTTON_FONT_SIZE}px`,
          fontWeight: 'bold',
          color: 'white',
          opacity,
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
          opacity,
        }}
      >
        <div
          style={{
            fontSize: `${design.TEXT_TYPE_FONT_SIZE}px`,
            color: textColor,
            marginBottom: `${design.TEXT_ELEMENT_MARGIN}px`,
          }}
        >
          {node.type}
        </div>

        <div
          style={{
            fontSize: `${design.TEXT_GLYPH_SIZE}px`,
            lineHeight: `${design.TEXT_LINE_HEIGHT}px`,
            color: textColor,
            marginBottom: `${design.TEXT_ELEMENT_MARGIN}px`,
          }}
        >
          {node.glyph || '?'}
        </div>

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

      {node.inputs.map((input, idx) => (
        <NodeHandle
          key={`input-${input.index}`}
          item={input}
          idx={idx}
          total={node.inputs.length}
          type="target"
          position={Position.Left}
          isBypassed={isBypassed}
          borderColor={typeof handleBorderColor === 'function' ? handleBorderColor('input') : handleBorderColor}
          fillColor={typeof handleFillColor === 'function' ? handleFillColor('input') : handleFillColor}
        />
      ))}

      {node.outputs.map((output, idx) => (
        <NodeHandle
          key={`output-${output.index}`}
          item={output}
          idx={idx}
          total={node.outputs.length}
          type="source"
          position={Position.Right}
          isBypassed={isBypassed}
          borderColor={typeof handleBorderColor === 'function' ? handleBorderColor('output') : handleBorderColor}
          fillColor={typeof handleFillColor === 'function' ? handleFillColor('output') : handleFillColor}
        />
      ))}
    </div>
  );
};
