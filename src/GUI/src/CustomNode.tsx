import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeResponse, InputInfo, OutputInfo } from './types';
import * as design from './nodeDesign';

interface CustomNodeData {
  node: NodeResponse;
  onBypassToggle?: (sessionId: string) => void;
  onDisplayToggle?: (sessionId: string) => void;
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
      height: `${diameter}px`,
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
  const { node, onBypassToggle, onDisplayToggle } = data;
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
          display: 'flex',
          flexDirection: 'column',
          gap: `${design.ERROR_WARNING_DUAL_GAP}px`,
          opacity,
        }}
      >
        <div
          style={{
            width: `${design.COOKING_STATE_DIAMETER}px`,
            height: `${design.COOKING_STATE_DIAMETER}px`,
            borderRadius: '50%',
            background: stateColor,
          }}
          title="Cooking state"
        />

        {hasError && (
          <IndicatorCircle
            color={design.COLOR_ERROR}
            title="Has errors"
          />
        )}

        {hasWarning && (
          <IndicatorCircle
            color={design.COLOR_WARNING}
            title="Has warnings"
          />
        )}
      </div>

      <div
        onClick={(e) => {
          e.stopPropagation();
          onBypassToggle?.(node.session_id);
        }}
        style={{
          position: 'absolute',
          right: `${design.TEMPLATE_CIRCLE_RIGHT}px`,
          top: '50%',
          transform: 'translateY(-50%)',
          width: `${design.TEMPLATE_CIRCLE_DIAMETER}px`,
          height: `${design.TEMPLATE_CIRCLE_DIAMETER}px`,
          borderRadius: '50%',
          background: design.COLOR_BYPASS_DEFAULT,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: `${design.TEMPLATE_CIRCLE_FONT_SIZE}px`,
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
          paddingTop: `${design.TEXT_AREA_TOP}px`,
          paddingBottom: `${design.TEXT_AREA_BOTTOM}px`,
          paddingLeft: `${design.TEXT_AREA_LEFT - design.NODE_PADDING_HORIZONTAL}px`,
          paddingRight: `${design.TEXT_AREA_RIGHT - design.NODE_PADDING_HORIZONTAL}px`,
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
          opacity,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
          }}
        >
          <div
            style={{
              fontSize: `${design.TEXT_GLYPH_SIZE}px`,
              fontWeight: 'bold',
              flex: 1,
              textAlign: 'center',
              color: textColor,
            }}
          >
            {node.glyph || '?'}
          </div>

          <div
            style={{
              fontSize: `${design.TEXT_TYPE_FONT_SIZE}px`,
              color: textColor,
              fontWeight: '500',
            }}
          >
            {node.type}
          </div>
        </div>

        <div
          style={{
            fontSize: `${design.TEXT_FONT_SIZE}px`,
            fontWeight: 'bold',
            color: textColor,
            textAlign: 'center',
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
