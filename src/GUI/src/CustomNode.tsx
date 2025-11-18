import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeResponse, InputInfo, OutputInfo } from './types';
import * as design from './nodeDesign';
import { useTheme } from './ThemeContext';

interface CustomNodeData {
  node: NodeResponse;
  onBypassToggle?: (sessionId: string) => void;
  onDisplayToggle?: (sessionId: string) => void;
}

const MIN_HANDLE_SPACING = 12;
const VERTICAL_PADDING = 20;

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
  outlineColor?: string;
}

const IndicatorCircle: React.FC<IndicatorCircleProps> = ({
  color,
  title,
  diameter = design.ERROR_WARNING_DIAMETER,
  outlineColor
}) => (
  <div
    style={{
      width: `${diameter}px`,
      height: `${diameter}px`,
      borderRadius: '50%',
      background: color,
      boxShadow: outlineColor
        ? `0 0 0 2px ${color}, 0 0 0 4px ${outlineColor}`
        : undefined,
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
  const { node, onBypassToggle, onDisplayToggle: _onDisplayToggle } = data;
  const { mode } = useTheme();
  const colors = design.getColors(mode);

  const isBypassed = node.parameters?.bypass?.value === true;
  const _isOnDisplay = node.parameters?.display?.value === true;
  // _onDisplayToggle and _isOnDisplay are reserved for future display toggle feature
  void _onDisplayToggle;
  void _isOnDisplay;
  const hasError = node.errors.length > 0;
  const hasWarning = node.warnings.length > 0;

  const minHeight = calculateMinHeight(node.inputs.length, node.outputs.length);
  const stateColor = colors.cooking[node.state as keyof typeof colors.cooking] ?? colors.cooking.uncooked;
  const borderColor = selected
    ? colors.border.selected
    : isBypassed
    ? colors.border.bypassed
    : colors.border.active;
  const backgroundColor = isBypassed ? colors.background.bypassed : colors.background.active;
  const textColor = isBypassed ? colors.text.bypassed : colors.text.active;
  const opacity = getOpacity(isBypassed);

  const getHandleBorderColor = (type: 'input' | 'output'): string =>
    isBypassed ? colors.handle.bypassed.border :
    type === 'input' ? colors.handle.input.border : colors.handle.output.border;

  const getHandleFillColor = (type: 'input' | 'output'): string =>
    isBypassed ? colors.handle.bypassed.fill :
    type === 'input' ? colors.handle.input.fill : colors.handle.output.fill;

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
            color={colors.error.fill}
            title="Has errors"
            outlineColor={colors.error.outline}
          />
        )}

        {hasWarning && (
          <IndicatorCircle
            color={colors.warning.fill}
            title="Has warnings"
            outlineColor={colors.warning.outline}
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
          background: colors.bypass.default,
          cursor: 'pointer',
          opacity,
          transition: 'background 0.2s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = colors.bypass.hover;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = colors.bypass.default;
        }}
        title={isBypassed ? 'Bypassed (Template)' : 'Click to bypass'}
      />


      <div
        style={{
          position: 'relative',
          paddingTop: `${design.TEXT_AREA_TOP}px`,
          paddingBottom: `${design.TEXT_AREA_BOTTOM}px`,
          paddingLeft: `${design.TEXT_AREA_LEFT - design.NODE_PADDING_HORIZONTAL}px`,
          paddingRight: `${design.TEXT_AREA_RIGHT - design.NODE_PADDING_HORIZONTAL}px`,
          display: 'flex',
          flexDirection: 'column',
          gap: `${design.TEXT_CONTENT_GAP}px`,
          opacity,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: `${design.TEXT_HEADER_GAP}px`,
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
          borderColor={getHandleBorderColor('input')}
          fillColor={getHandleFillColor('input')}
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
          borderColor={getHandleBorderColor('output')}
          fillColor={getHandleFillColor('output')}
        />
      ))}
    </div>
  );
};
