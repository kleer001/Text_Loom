# Flicker Issues

**Issue 1:** Inline data object recreated on every render
**File:** src/GUI/src/GraphCanvas.tsx:156
**Fix:** Memoize node data objects individually

**Issue 2:** Unmemoized custom node component causes full rerender
**File:** src/GUI/src/CustomNode.tsx:94
**Fix:** Wrap export with React.memo

**Issue 3:** Inline style objects in CustomNode recreated every render
**File:** src/GUI/src/CustomNode.tsx:131-140, 142-161, 180-206, 208-262
**Fix:** Extract to useMemo or constants outside component

**Issue 4:** Node transformation effect runs on every workspace change
**File:** src/GUI/src/GraphCanvas.tsx:137-182
**Fix:** Use stable references for callbacks in dependencies, consider splitting effect
