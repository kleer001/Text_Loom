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

const DEFAULT_NODE_WIDTH = 180;
const DEFAULT_NODE_HEIGHT = 80;
const DEFAULT_PADDING = 30;

function getNodeDimensions(node: Node): { width: number; height: number } {
  return {
    width: node.measured?.width ?? node.width ?? DEFAULT_NODE_WIDTH,
    height: node.measured?.height ?? node.height ?? DEFAULT_NODE_HEIGHT,
  };
}

function extractBoundingBoxCorners(nodes: Node[]): Point[] {
  const corners: Point[] = [];
  nodes.forEach(node => {
    const { x, y } = node.position;
    const { width, height } = getNodeDimensions(node);
    corners.push(
      { x, y },
      { x: x + width, y },
      { x, y: y + height },
      { x: x + width, y: y + height }
    );
  });
  return corners;
}

function calculateCentroid(points: Point[]): Point {
  return {
    x: points.reduce((sum, p) => sum + p.x, 0) / points.length,
    y: points.reduce((sum, p) => sum + p.y, 0) / points.length,
  };
}

function expandHullWithPadding(hull: Point[], centroid: Point, padding: number): Point[] {
  return hull.map(point => {
    const dx = point.x - centroid.x;
    const dy = point.y - centroid.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist === 0) return point;
    return {
      x: point.x + (dx / dist) * padding,
      y: point.y + (dy / dist) * padding,
    };
  });
}

function buildSvgPath(points: Point[]): string {
  return points.map((point, i) => `${i === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ') + ' Z';
}

export const LoopBoundary: React.FC<LoopBoundaryProps> = ({ nodes, padding = DEFAULT_PADDING }) => {
  const { x: viewportX, y: viewportY, zoom } = useViewport();

  if (nodes.length === 0) return null;

  const boundingBoxCorners = extractBoundingBoxCorners(nodes);
  const hull = getConvexHull(boundingBoxCorners);

  if (hull.length < 3) return null;

  const centroid = calculateCentroid(boundingBoxCorners);
  const paddedHull = expandHullWithPadding(hull, centroid, padding);
  const pathData = buildSvgPath(paddedHull);

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
