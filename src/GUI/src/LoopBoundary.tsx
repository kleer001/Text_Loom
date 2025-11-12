import React from 'react';
import { useViewport } from '@xyflow/react';
import type { Node } from '@xyflow/react';

interface Point {
  x: number;
  y: number;
}

function getConvexHull(points: Point[]): Point[] {
  const sorted = [...points].sort((a, b) => a.x - a.x || a.y - b.y);

  const cross = (o: Point, a: Point, b: Point) =>
    (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);

  const lower: Point[] = [];
  for (const point of sorted) {
    while (lower.length >= 2 &&
           cross(lower[lower.length - 2], lower[lower.length - 1], point) <= 0) {
      lower.pop();
    }
    lower.push(point);
  }

  const upper: Point[] = [];
  for (let i = sorted.length - 1; i >= 0; i--) {
    const point = sorted[i];
    while (upper.length >= 2 &&
           cross(upper[upper.length - 2], upper[upper.length - 1], point) <= 0) {
      upper.pop();
    }
    upper.push(point);
  }

  upper.pop();
  lower.pop();
  return lower.concat(upper);
}

interface LoopBoundaryProps {
  nodes: Node[];
  padding?: number;
}

const NODE_WIDTH = 150;
const NODE_HEIGHT = 60;
const DEFAULT_PADDING = 30;

export const LoopBoundary: React.FC<LoopBoundaryProps> = ({ nodes, padding = DEFAULT_PADDING }) => {
  const { x: viewportX, y: viewportY, zoom } = useViewport();

  if (nodes.length === 0) return null;

  // Use all 4 corners of each node's bounding box
  const nodePoints: Point[] = [];
  nodes.forEach(node => {
    const x = node.position.x;
    const y = node.position.y;
    // Add all 4 corners of the node's bounding box
    nodePoints.push(
      { x, y },                           // Top-left
      { x: x + NODE_WIDTH, y },           // Top-right
      { x, y: y + NODE_HEIGHT },          // Bottom-left
      { x: x + NODE_WIDTH, y: y + NODE_HEIGHT } // Bottom-right
    );
  });

  const hull = getConvexHull(nodePoints);

  // If hull is too small (line or single point), don't render
  if (hull.length < 3) return null;

  const center = {
    x: nodePoints.reduce((sum, p) => sum + p.x, 0) / nodePoints.length,
    y: nodePoints.reduce((sum, p) => sum + p.y, 0) / nodePoints.length,
  };

  const paddedHull = hull.map(point => {
    const dx = point.x - center.x;
    const dy = point.y - center.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    // Avoid division by zero
    if (dist === 0) return point;
    return {
      x: point.x + (dx / dist) * padding,
      y: point.y + (dy / dist) * padding,
    };
  });

  const pathData = paddedHull
    .map((point, i) => `${i === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ') + ' Z';

  return (
    <svg
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 1000,
        overflow: 'visible',
      }}
    >
      <g transform={`translate(${viewportX}, ${viewportY}) scale(${zoom})`}>
        <path
          d={pathData}
          fill="rgba(255, 140, 0, 0.15)"
          stroke="rgba(255, 140, 0, 0.8)"
          strokeWidth={3 / zoom}
        />
      </g>
    </svg>
  );
};
