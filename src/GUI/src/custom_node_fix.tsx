// Revised CustomNode.tsx using new scale-aware Layout
import React, { useMemo } from 'react';
import { Handle, Position } from '@xyflow/react';
import * as design from './nodeDesign';
import { useTheme } from './ThemeContext';

export const CustomNode = React.memo(function CustomNode({ data, selected }) {
  const { node, size = 'large', onBypassToggle } = data;
  const { mode } = useTheme();
  const colors = design.getColors(mode);
  const L = design.Layout(size);

  const isBypassed = node.parameters?.bypass?.value === true;
  const hasError = node.errors.length > 0;
  const hasWarning = node.warnings.length > 0;

  const calculateMinHeight = (inputCount, outputCount) => {
    const count = Math.max(inputCount, outputCount);
    return count > 0 ? (count + 1) * L.handle.minSpacing : undefined;
  };

  const minHeight = calculateMinHeight(node.inputs.length, node.outputs.length);

  const containerStyle = {
    position: 'relative',
    padding: `${L.node.paddingY}px ${L.node.paddingX}px`,
    border: `${L.node.borderWidth}px solid ${selected ? colors.border.selected : colors.border.active}`,
    borderRadius: `${L.node.borderRadius}px`,
    background: isBypassed ? colors.background.bypassed : colors.background.active,
    minWidth: `${L.node.minWidth}px`,
    minHeight,
  };

  const textAreaStyle = {
    paddingTop: L.text.paddingTop,
    paddingBottom: L.text.paddingBottom,
    paddingLeft: L.text.paddingSide,
    paddingRight: L.text.paddingSide,
    display: 'flex',
    flexDirection: 'column',
    gap: L.text.gapLines,
  };

  const glyphStyle = {
    fontSize: L.text.glyphSize,
    fontWeight: 'bold',
    textAlign: 'center',
    color: colors.text.active,
  };

  const typeStyle = {
    fontSize: L.text.typeSize,
    color: colors.text.active,
    fontWeight: '500',
  };

  const nameStyle = {
    fontSize: L.text.nameSize,
    fontWeight: 'bold',
    textAlign: 'center',
    color: colors.text.active,
  };

  return (
    <div style={containerStyle}>

      {L.visibility.showIndicators && (
        <div style={{
          position: 'absolute',
          left: L.indicators.offset,
          top: L.indicators.offset,
          display: 'flex',
          flexDirection: 'column',
          gap: L.indicators.gap,
        }}>
          <div style={{
            width: L.indicators.diameter,
            height: L.indicators.diameter,
            borderRadius: '50%',
            background: colors.cooking[node.state] || colors.cooking.uncooked,
          }} />

          {hasError && <div style={{ width: L.indicators.diameter, height: L.indicators.diameter, borderRadius: '50%', background: colors.error.fill }} />}
          {hasWarning && <div style={{ width: L.indicators.diameter, height: L.indicators.diameter, borderRadius: '50%', background: colors.warning.fill }} />}
        </div>
      )}

      {L.visibility.showBypass && (
        <div
          onClick={(e) => { e.stopPropagation(); onBypassToggle?.(node.session_id); }}
          style={{
            position: 'absolute',
            right: L.bypass.offsetRight,
            top: '50%',
            transform: 'translateY(-50%)',
            width: L.bypass.diameter,
            height: L.bypass.diameter,
            borderRadius: '50%',
            background: colors.bypass.default,
            cursor: 'pointer',
          }}
        />
      )}

      <div style={textAreaStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: L.text.gapHeader }}>
          <div style={glyphStyle}>{node.glyph || '?'}</div>
          <div style={typeStyle}>{node.type}</div>
        </div>

        {L.visibility.showName && (
          <div style={nameStyle}>{node.name}</div>
        )}
      </div>

      {node.inputs.map((input, i) => (
        <Handle
          key={input.index}
          type="target"
          position={Position.Left}
          id={`input-${i}`}
          title={`${input.name} (${input.data_type})`}
          style={{
            top: `${((i + 1) / (node.inputs.length + 1)) * 100}%`,
            left: -L.handle.offset,
            width: L.handle.diameter,
            height: L.handle.diameter,
            border: `${L.handle.borderWidth}px solid ${colors.handle.input.border}`,
            background: colors.handle.input.fill,
          }}
        />
      ))}

      {node.outputs.map((output, i) => (
        <Handle
          key={output.index}
          type="source"
          position={Position.Right}
          id={`output-${i}`}
          title={`${output.name} (${output.data_type})`}
          style={{
            top: `${((i + 1) / (node.outputs.length + 1)) * 100}%`,
            right: -L.handle.offset,
            width: L.handle.diameter,
            height: L.handle.diameter,
            border: `${L.handle.borderWidth}px solid ${colors.handle.output.border}`,
            background: colors.handle.output.fill,
          }}
        />
      ))}

    </div>
  );
});
