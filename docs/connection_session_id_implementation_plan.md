# Implementation Plan: Add Persistent Session IDs to Connections

## Overview
Add persistent UUID-based session IDs to `NodeConnection` objects, mirroring the pattern used in `MobileItem` for nodes. This will make connections first-class entities with stable identifiers, simplifying frontend code and enabling future features.

## Reference Implementation
See `src/core/mobile_item.py` lines 33, 53, 163-184, 207 for the session ID pattern to replicate.

---

## Step 1: Add Session IDs to NodeConnection (Backend Core)

**Files to modify:**
- `src/core/node_connection.py`

**Changes:**

### 1.1 Add class-level tracking
```python
import uuid

class NodeConnection(NetworkEntity):
    """Represents a connection between two nodes."""

    # Add class variable to track all connection session IDs
    _existing_session_ids: Set[str] = set()

    def __init__(self, output_node: 'Node', input_node: 'Node',
                 output_index: int, input_index: int):
        super().__init__()
        self._output_node: 'Node' = output_node
        self._input_node: 'Node' = input_node
        self._output_index: int = output_index
        self._input_index: int = input_index
        self._selected: bool = False

        # Add session ID generation (same pattern as MobileItem)
        self._session_id: str = self._generate_unique_session_id()
```

### 1.2 Add session ID methods
Copy these methods from `MobileItem` (lines 163-184):

```python
    def session_id(self) -> str:
        """Returns the unique session ID for this connection."""
        return self._session_id

    @classmethod
    def _generate_unique_session_id(cls) -> str:
        """
        Generate a unique string session ID.

        Returns:
            str: A unique session ID (UUID as string).

        Raises:
            RuntimeError: If unable to generate a unique ID after 100 attempts.
        """
        for attempt in range(100):
            new_id = cls._generate_session_id()
            if new_id not in cls._existing_session_ids:
                cls._existing_session_ids.add(new_id)
                return new_id

        raise RuntimeError('Unable to generate a unique session ID for connection')

    @staticmethod
    def _generate_session_id() -> str:
        """Generate a string session ID using UUID."""
        return str(uuid.uuid4())
```

### 1.3 Add cleanup on deletion
```python
    def __del__(self) -> None:
        """Clean up when the connection is deleted."""
        self._existing_session_ids.discard(self._session_id)
```

### 1.4 Update __repr__
```python
    def __repr__(self) -> str:
        """Returns a string representation of the NodeConnection."""
        return (
            f'NodeConnection(session_id={self._session_id}, '
            f'output_node={self._output_node.name()}, '
            f'input_node={self._input_node.name()}, '
            f'output_index={self._output_index}, '
            f'input_index={self._input_index})'
        )
```

**Testing:**
- Create a connection → verify it has a unique session_id
- Create multiple connections → verify all IDs are unique
- Delete a connection → verify ID is removed from tracking set

**Acceptance Criteria:**
- ✅ All connections have persistent UUID session IDs
- ✅ Session IDs are unique across all connections
- ✅ Session IDs remain stable throughout connection lifetime
- ✅ No breaking changes to existing connection creation/deletion logic

---

## Step 2: Update API to Use Connection IDs (Backend API)

**Files to modify:**
- `src/api/models.py`
- `src/api/routers/connections.py`

**Changes:**

### 2.1 Update ConnectionResponse model
Add `connection_id` field to `ConnectionResponse` (line ~222):

```python
class ConnectionResponse(BaseModel):
    """A connection between two nodes."""

    # Add connection ID as first field
    connection_id: str = Field(..., description="Unique connection session ID")

    # Source (output) side
    source_node_session_id: str = Field(..., description="Source node's session ID")
    source_node_path: str = Field(..., description="Source node's path")
    source_output_index: int = Field(..., description="Output socket index")
    source_output_name: str = Field(..., description="Output socket name")

    # Target (input) side
    target_node_session_id: str = Field(..., description="Target node's session ID")
    target_node_path: str = Field(..., description="Target node's path")
    target_input_index: int = Field(..., description="Input socket index")
    target_input_name: str = Field(..., description="Input socket name")
```

### 2.2 Update connection_to_response helper
Find the `connection_to_response` function in `models.py` and add connection ID:

```python
def connection_to_response(connection: NodeConnection) -> ConnectionResponse:
    """Convert a NodeConnection to ConnectionResponse."""
    return ConnectionResponse(
        connection_id=connection.session_id(),  # Add this line
        source_node_session_id=connection.output_node().session_id(),
        source_node_path=connection.output_node().path(),
        source_output_index=connection.output_index(),
        source_output_name=connection.output_name(),
        target_node_session_id=connection.input_node().session_id(),
        target_node_path=connection.input_node().path(),
        target_input_index=connection.input_index(),
        target_input_name=connection.input_name(),
    )
```

### 2.3 Add new DELETE endpoint (by ID)
Add this new endpoint to `src/api/routers/connections.py`:

```python
@router.delete(
    "/connections/{connection_id}",
    response_model=SuccessResponse,
    summary="Delete a connection by ID",
    description="Deletes a connection using its session ID.",
    responses={
        200: {"description": "Connection deleted successfully"},
        404: {"description": "Connection not found", "model": ErrorResponse}
    }
)
def delete_connection_by_id(connection_id: str) -> SuccessResponse:
    """
    Delete a connection by its session ID.

    This is the preferred way to delete connections in the GUI.

    Args:
        connection_id: The connection's session ID

    Returns:
        SuccessResponse: Confirmation of deletion

    Raises:
        HTTPException: 404 if connection not found
    """
    try:
        # Search all nodes for a connection with this ID
        connection_found = None

        for node in NodeEnvironment.nodes.values():
            # Check all input connections
            for input_idx, connection in node._inputs.items():
                if connection and connection.session_id() == connection_id:
                    connection_found = connection
                    break

            if connection_found:
                break

        if not connection_found:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "connection_not_found",
                    "message": f"Connection with ID '{connection_id}' does not exist"
                }
            )

        # Remove the connection
        target_node = connection_found.input_node()
        target_node.remove_connection(connection_found)

        return SuccessResponse(
            success=True,
            message=f"Connection {connection_id} deleted"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Failed to delete connection: {str(e)}"
            }
        )
```

### 2.4 Keep old DELETE endpoint for backward compatibility
Keep the existing `delete_connection(request: ConnectionDeleteRequest)` endpoint unchanged for now. It can be deprecated later.

**Testing:**
- POST /connections → response includes `connection_id`
- GET /workspace → all connections include `connection_id`
- DELETE /connections/{connection_id} → successfully deletes connection
- DELETE /connections (old endpoint) → still works

**Acceptance Criteria:**
- ✅ All API responses include connection_id
- ✅ New DELETE endpoint accepts connection ID
- ✅ Old DELETE endpoint still works (backward compatibility)
- ✅ 404 error if connection ID not found

---

## Step 3: Update Frontend to Use Connection IDs (GUI)

**Files to modify:**
- `src/GUI/src/types.ts`
- `src/GUI/src/apiClient.ts`
- `src/GUI/src/GraphCanvas.tsx`
- `src/GUI/src/utils/edgeMapping.ts`

**Changes:**

### 3.1 Update TypeScript types
Add `connection_id` to `ConnectionResponse` in `types.ts`:

```typescript
export interface ConnectionResponse {
  connection_id: string;  // Add this
  source_node_session_id: string;
  source_node_path: string;
  source_output_index: number;
  source_output_name: string;
  target_node_session_id: string;
  target_node_path: string;
  target_input_index: number;
  target_input_name: string;
}
```

### 3.2 Add new API method
Add to `apiClient.ts`:

```typescript
async deleteConnectionById(connectionId: string): Promise<void> {
  await this.fetchJson<void>(`/connections/${connectionId}`, {
    method: 'DELETE',
  });
}
```

### 3.3 Update edge mapping utility
Modify `connectionsToEdges` in `utils/edgeMapping.ts` to use connection ID:

```typescript
export function connectionsToEdges(
  connections: ConnectionResponse[],
  edgeOptions?: Partial<Edge>
): Edge[] {
  return connections.map(conn => ({
    // Use connection_id directly as React Flow edge ID
    id: conn.connection_id,
    source: conn.source_node_session_id,
    target: conn.target_node_session_id,
    sourceHandle: `output-${conn.source_output_index}`,
    targetHandle: `input-${conn.target_input_index}`,
    ...edgeOptions,
  }));
}
```

### 3.4 Simplify GraphCanvas.tsx
Update the connection handlers to use the new simpler approach:

**Create Connection (onConnect):**
```typescript
const onConnect = useCallback(async (connection: Connection) => {
  const sourceOutputIndex = parseInt(connection.sourceHandle?.replace('output-', '') || '0');
  const targetInputIndex = parseInt(connection.targetHandle?.replace('input-', '') || '0');

  const sourceNode = nodes.find(n => n.id === connection.source);
  const targetNode = nodes.find(n => n.id === connection.target);

  if (!sourceNode || !targetNode) {
    console.error('Source or target node not found');
    return;
  }

  const request: ConnectionRequest = {
    source_node_path: (sourceNode.data as { node: NodeResponse }).node.path,
    source_output_index: sourceOutputIndex,
    target_node_path: (targetNode.data as { node: NodeResponse }).node.path,
    target_input_index: targetInputIndex,
  };

  try {
    const newConnection = await apiClient.createConnection(request);

    // Use connection_id as edge ID (no more manual ID generation!)
    setEdges(prevEdges => {
      const filtered = prevEdges.filter(e =>
        !(e.target === connection.target &&
          e.targetHandle === connection.targetHandle)
      );

      const newEdge: Edge = {
        id: newConnection.connection_id,  // Use connection ID!
        source: connection.source,
        target: connection.target,
        sourceHandle: connection.sourceHandle!,
        targetHandle: connection.targetHandle!,
        type: 'smoothstep',
        animated: false,
        style: { stroke: '#888', strokeWidth: 2 },
      };

      return [...filtered, newEdge];
    });

    await loadWorkspace();

  } catch (error) {
    console.error('Failed to create connection:', error);
  }
}, [nodes, setEdges, loadWorkspace]);
```

**Delete Connection (onEdgesDelete):**
```typescript
const onEdgesDelete = useCallback(async (edgesToDelete: Edge[]) => {
  // Much simpler - just delete by ID!
  for (const edge of edgesToDelete) {
    try {
      await apiClient.deleteConnectionById(edge.id);
    } catch (error) {
      console.error('Failed to delete connection:', error);
    }
  }

  setEdges(prevEdges =>
    prevEdges.filter(e => !edgesToDelete.includes(e))
  );

  await loadWorkspace();

}, [setEdges, loadWorkspace]);
```

**What gets removed:**
- ❌ No more parsing handle IDs to get indices in delete handler
- ❌ No more finding nodes to get paths in delete handler
- ❌ No more building ConnectionDeleteRequest objects
- ❌ No more manual edge ID generation from session IDs and indices

**Testing:**
- Create connection → edge ID matches backend connection_id
- Delete connection → sends DELETE /connections/{id}
- Workspace refresh → edges use connection IDs consistently
- Browser devtools → verify simpler network requests

**Acceptance Criteria:**
- ✅ Edge IDs come directly from backend connection IDs
- ✅ Connection deletion uses simple ID-based API
- ✅ No handle parsing or manual ID generation in delete handler
- ✅ All connection operations work correctly

---

## Migration Notes

**No migration needed** - This is additive:
- Existing code continues to work
- New connections automatically get IDs
- Connections created at runtime get IDs immediately
- If connections are persisted to disk, add session_id to serialization

## Rollback Plan

If issues arise, revert in reverse order:
1. Revert Step 3 (frontend) - restore handle parsing logic
2. Revert Step 2 (API) - remove connection_id from responses
3. Revert Step 1 (core) - remove session_id from NodeConnection

## Benefits Summary

✅ **Cleaner code** - 50% less code in frontend delete handler
✅ **More robust** - No string parsing, no NaN bugs
✅ **Consistent** - Connections are first-class like nodes
✅ **Future-proof** - Enables connection metadata, undo/redo, etc.
✅ **Better UX** - Faster, more reliable connection operations

## Estimated Effort

- **Step 1**: 30 minutes (copy-paste pattern from MobileItem)
- **Step 2**: 45 minutes (update models and add endpoint)
- **Step 3**: 30 minutes (simplify frontend code)

**Total**: ~2 hours
