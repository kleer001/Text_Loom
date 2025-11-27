import React, { useMemo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeResponse } from './types';
import * as design from './nodeDesign';
import { useTheme } from './ThemeContext';

interface CustomNodeData {
  node: NodeResponse;
  size?: 'large' | 'medium' | 'small';
  onBypassToggle?: (sessionId: string) => void;
}

const calculateMinHeight = (inputCount: number, outputCount: number, minSpacing: number): number | undefined => {
  const count = Math.max(inputCount, outputCount);
  return count > 0 ? (count + 1) * minSpacing : undefined;
};

const getOpacity = (isBypassed: boolean): number =>
  isBypassed ? design.OPACITY_BYPASSED : design.OPACITY_ACTIVE;

const CustomNodeComponent: React.FC<{ data: CustomNodeData; selected?: boolean }> = ({
  data,
  selected
}) => {
  const { node, size = 'large', onBypassToggle } = data;
  const { mode } = useTheme();
  const colors = design.getColors(mode);
  const L = design.Layout(size);

  const isBypassed = node.parameters?.bypass?.value === true;
  const hasError = node.errors.length > 0;
  const hasWarning = node.warnings.length > 0;
  const opacity = getOpacity(isBypassed);

  const minHeight = calculateMinHeight(node.inputs.length, node.outputs.length, L.handle.minSpacing);

  const borderColor = selected
    ? colors.border.selected
    : isBypassed
    ? colors.border.bypassed
    : colors.border.active;
  const backgroundColor = isBypassed ? colors.background.bypassed : colors.background.active;
  const textColor = isBypassed ? colors.text.bypassed : colors.text.active;

  const containerStyle = useMemo(() => ({
    position: 'relative' as const,
    padding: `${L.node.paddingY}px ${L.node.paddingX}px`,
    border: `${L.node.borderWidth}px solid ${borderColor}`,
    borderRadius: `${L.node.borderRadius}px`,
    background: backgroundColor,
    minWidth: `${L.node.minWidth}px`,
    minHeight: minHeight || undefined,
    boxShadow: selected ? '0 4px 8px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.1)',
  }), [L.node.paddingY, L.node.paddingX, L.node.borderWidth, borderColor, L.node.borderRadius, backgroundColor, L.node.minWidth, minHeight, selected]);

  const textAreaStyle = useMemo(() => ({
    paddingTop: L.text.paddingTop,
    paddingBottom: L.text.paddingBottom,
    paddingLeft: L.text.paddingSide,
    paddingRight: L.text.paddingSide,
    display: 'flex',
    flexDirection: 'column' as const,
    gap: L.text.gapLines,
    opacity,
  }), [L.text.paddingTop, L.text.paddingBottom, L.text.paddingSide, L.text.gapLines, opacity]);

  const glyphStyle = useMemo(() => ({
    fontSize: L.text.glyphSize,
    fontWeight: 'bold' as const,
    textAlign: 'center' as const,
    color: textColor,
  }), [L.text.glyphSize, textColor]);

  const typeStyle = useMemo(() => ({
    fontSize: L.text.typeSize,
    color: textColor,
    fontWeight: '500',
  }), [L.text.typeSize, textColor]);

  const nameStyle = useMemo(() => ({
    fontSize: L.text.nameSize,
    fontWeight: 'bold' as const,
    textAlign: 'center' as const,
    color: textColor,
  }), [L.text.nameSize, textColor]);

  const indicatorsContainerStyle = useMemo(() => ({
    position: 'absolute' as const,
    left: L.indicators.offset,
    top: L.indicators.offset,
    display: 'flex',
    flexDirection: 'column' as const,
    gap: L.indicators.gap,
    opacity,
  }), [L.indicators.offset, L.indicators.gap, opacity]);

  const cookingStateCircleStyle = useMemo(() => ({
    width: L.indicators.diameter,
    height: L.indicators.diameter,
    borderRadius: '50%',
    background: colors.cooking[node.state] || colors.cooking.uncooked,
  }), [L.indicators.diameter, colors.cooking, node.state]);

  const bypassButtonStyle = useMemo(() => ({
    position: 'absolute' as const,
    right: L.bypass.offsetRight,
    top: '50%',
    transform: 'translateY(-50%)',
    width: L.bypass.diameter,
    height: L.bypass.diameter,
    borderRadius: '50%',
    background: colors.bypass.default,
    cursor: 'pointer',
    opacity,
    transition: 'background 0.2s',
  }), [L.bypass.offsetRight, L.bypass.diameter, colors.bypass.default, opacity]);

  const glyphBackgroundStyle = useMemo(() => ({
    position: 'absolute' as const,
    left: 0,
    top: 0,
    bottom: 0,
    width: L.text.glyphSize + 2 * L.glyph.padding,
    background: isBypassed ? colors.glyph.background.bypassed : colors.glyph.background.active,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderTopLeftRadius: `${L.node.borderRadius}px`,
    borderBottomLeftRadius: `${L.node.borderRadius}px`,
  }), [L.text.glyphSize, L.glyph.padding, L.node.borderRadius, isBypassed, colors.glyph.background]);

  const templateToggleStyle = useMemo(() => ({
    position: 'absolute' as const,
    right: 0,
    top: L.template.paddingY,
    bottom: L.template.paddingY,
    width: L.template.width,
    background: isBypassed ? colors.template.on : colors.template.off,
    cursor: 'pointer',
    borderTopRightRadius: `${L.node.borderRadius}px`,
    borderBottomRightRadius: `${L.node.borderRadius}px`,
    transition: 'background 0.2s',
  }), [L.template.width, L.template.paddingY, L.node.borderRadius, isBypassed, colors.template]);

  const smallNodeNameStyle = useMemo(() => ({
    fontSize: L.text.nameSize,
    fontWeight: 'bold' as const,
    color: textColor,
    paddingLeft: L.text.glyphSize + 2 * L.glyph.padding + L.glyph.bufferFromEdge,
    paddingRight: L.template.width + L.glyph.bufferFromEdge,
    display: 'flex',
    alignItems: 'center',
    minHeight: '100%',
  }), [L.text.nameSize, L.text.glyphSize, L.glyph.padding, L.glyph.bufferFromEdge, L.template.width, textColor]);

  return (
    <div style={containerStyle}>

      {L.visibility.showIndicators && (
        <div style={indicatorsContainerStyle}>
          <div
            style={cookingStateCircleStyle}
            title="Cooking state"
          />

          {hasError && (
            <div
              style={{
                width: L.indicators.diameter,
                height: L.indicators.diameter,
                borderRadius: '50%',
                background: colors.error.fill,
                boxShadow: `0 0 0 2px ${colors.error.fill}, 0 0 0 4px ${colors.error.outline}`,
              }}
              title="Has errors"
            />
          )}

          {hasWarning && (
            <div
              style={{
                width: L.indicators.diameter,
                height: L.indicators.diameter,
                borderRadius: '50%',
                background: colors.warning.fill,
                boxShadow: `0 0 0 2px ${colors.warning.fill}, 0 0 0 4px ${colors.warning.outline}`,
              }}
              title="Has warnings"
            />
          )}
        </div>
      )}

      {size === 'small' ? (
        <>
          <div style={glyphBackgroundStyle}>
            <div style={{ ...glyphStyle, opacity }}>{node.glyph || '?'}</div>
          </div>

          <div style={{ ...smallNodeNameStyle, opacity }}>
            {node.name}
          </div>

          <div
            onClick={(e) => {
              e.stopPropagation();
              onBypassToggle?.(node.session_id);
              e.currentTarget.style.background = !isBypassed ? colors.template.onHover : colors.template.offHover;
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = isBypassed ? colors.template.onHover : colors.template.offHover;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = isBypassed ? colors.template.on : colors.template.off;
            }}
            style={templateToggleStyle}
            title={isBypassed ? 'Template Mode On' : 'Template Mode Off'}
          />
        </>
      ) : (
        <>
          {L.visibility.showBypass && (
            <div
              onClick={(e) => {
                e.stopPropagation();
                onBypassToggle?.(node.session_id);
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = colors.bypass.hover;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = colors.bypass.default;
              }}
              style={bypassButtonStyle}
              title={isBypassed ? 'Bypassed (Template)' : 'Click to bypass'}
            />
          )}

          <div style={textAreaStyle}>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: L.handle.diameter }}>
              <div style={glyphStyle}>{node.glyph || '?'}</div>
              <div style={typeStyle}>{node.type}</div>
            </div>

            {L.visibility.showName && (
              <div style={nameStyle}>{node.name}</div>
            )}
          </div>
        </>
      )}

      {node.inputs.map((input, i) => {
        const handleBorderColor = isBypassed ? colors.handle.bypassed.border : colors.handle.input.border;
        const handleFillColor = isBypassed ? colors.handle.bypassed.fill : colors.handle.input.fill;

        return (
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
              border: `${L.handle.borderWidth}px solid ${handleBorderColor}`,
              background: handleFillColor,
              opacity,
            }}
          />
        );
      })}

      {node.outputs.map((output, i) => {
        const handleBorderColor = isBypassed ? colors.handle.bypassed.border : colors.handle.output.border;
        const handleFillColor = isBypassed ? colors.handle.bypassed.fill : colors.handle.output.fill;

        return (
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
              border: `${L.handle.borderWidth}px solid ${handleBorderColor}`,
              background: handleFillColor,
              opacity,
            }}
          />
        );
      })}

    </div>
  );
};

export const CustomNode = React.memo(CustomNodeComponent);
